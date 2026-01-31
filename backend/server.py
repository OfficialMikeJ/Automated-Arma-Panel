from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import psutil
import subprocess
import asyncio
import tarfile
import urllib.request
import signal
import time

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'tactical-server-panel-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    hashed_password: str
    security_questions: Optional[dict] = None  # {q1: answer1, q2: answer2, q3: answer3, q4: answer4}
    is_admin: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    password: str
    security_questions: Optional[dict] = None

class UserLogin(BaseModel):
    username: str
    password: str

class SecurityQuestionsSetup(BaseModel):
    question1: str
    answer1: str
    question2: str
    answer2: str
    question3: str
    answer3: str
    question4: str
    answer4: str

class PasswordResetRequest(BaseModel):
    username: str
    answer1: str
    answer2: str
    answer3: str
    answer4: str
    new_password: str

class FirstTimeSetup(BaseModel):
    username: str
    password: str
    security_questions: dict

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class ServerInstance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    game_type: str  # "arma_reforger" or "arma_4"
    port: int
    max_players: int
    current_players: int = 0
    status: str = "offline"  # online, offline, restarting
    install_path: str
    pid: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str

class ServerInstanceCreate(BaseModel):
    name: str
    game_type: str
    port: int
    max_players: int
    install_path: str

class ServerInstanceUpdate(BaseModel):
    name: Optional[str] = None
    port: Optional[int] = None
    max_players: Optional[int] = None
    current_players: Optional[int] = None
    status: Optional[str] = None

class SystemResources(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float

class SteamCMDStatus(BaseModel):
    installed: bool
    path: Optional[str] = None
    version: Optional[str] = None

class ServerMod(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    server_id: str
    workshop_id: str
    name: str
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServerModCreate(BaseModel):
    workshop_id: str
    name: str
    enabled: bool = True

class ServerConfig(BaseModel):
    content: str

class ServerLogs(BaseModel):
    logs: str
    lines: int

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"user_id": user_id, "username": payload.get("username")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Authentication routes
@api_router.get("/auth/check-first-run")
async def check_first_run():
    """Check if this is first run (no admin user exists)"""
    admin_user = await db.users.find_one({"is_admin": True}, {"_id": 0})
    return {"is_first_run": admin_user is None}

@api_router.post("/auth/first-time-setup", response_model=Token)
async def first_time_setup(setup_data: FirstTimeSetup):
    """Create the first admin user with security questions"""
    # Check if admin already exists
    existing_admin = await db.users.find_one({"is_admin": True}, {"_id": 0})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin user already exists")
    
    # Hash security answers
    hashed_security = {
        k: hash_password(v.lower().strip()) 
        for k, v in setup_data.security_questions.items()
    }
    
    # Create admin user
    user = User(
        username=setup_data.username,
        hashed_password=hash_password(setup_data.password),
        security_questions=hashed_security,
        is_admin=True
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user.username
    )

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash security questions if provided
    hashed_security = None
    if user_data.security_questions:
        hashed_security = {
            k: hash_password(v.lower().strip()) 
            for k, v in user_data.security_questions.items()
        }
    
    # Create user
    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        security_questions=hashed_security,
        is_admin=False
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user.username
    )

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["id"], "username": user["username"]}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user["username"]
    )

# Server instance routes
@api_router.post("/servers", response_model=ServerInstance)
async def create_server_instance(
    server_data: ServerInstanceCreate,
    current_user: dict = Depends(get_current_user)
):
    server = ServerInstance(
        **server_data.model_dump(),
        user_id=current_user["user_id"]
    )
    
    doc = server.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.servers.insert_one(doc)
    
    return server

@api_router.get("/servers", response_model=List[ServerInstance])
async def get_server_instances(current_user: dict = Depends(get_current_user)):
    servers = await db.servers.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    for server in servers:
        if isinstance(server['created_at'], str):
            server['created_at'] = datetime.fromisoformat(server['created_at'])
    
    return servers

@api_router.get("/servers/{server_id}", response_model=ServerInstance)
async def get_server_instance(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if isinstance(server['created_at'], str):
        server['created_at'] = datetime.fromisoformat(server['created_at'])
    
    return server

@api_router.patch("/servers/{server_id}", response_model=ServerInstance)
async def update_server_instance(
    server_id: str,
    update_data: ServerInstanceUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Check if server exists
    existing = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not existing:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Update only provided fields
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if update_dict:
        await db.servers.update_one(
            {"id": server_id},
            {"$set": update_dict}
        )
    
    # Get updated server
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if isinstance(server['created_at'], str):
        server['created_at'] = datetime.fromisoformat(server['created_at'])
    
    return server

@api_router.delete("/servers/{server_id}")
async def delete_server_instance(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = await db.servers.delete_one(
        {"id": server_id, "user_id": current_user["user_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return {"message": "Server deleted successfully"}

# Server control routes
@api_router.post("/servers/{server_id}/start")
async def start_server(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("/tmp/arma_servers") / server_id / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Start a dummy process (simulating server)
    # In production, this would be: ./ArmaReforgerServer or similar
    log_file = logs_dir / "server.log"
    process = subprocess.Popen(
        ["bash", "-c", f"while true; do echo '[$(date)] Server running on port {server['port']}...'; sleep 5; done"],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    
    # Update server with PID
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "online", "current_players": 0, "pid": process.pid}}
    )
    
    return {"message": "Server started successfully", "status": "online", "pid": process.pid}

@api_router.post("/servers/{server_id}/stop")
async def stop_server(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Kill the process if it exists
    if server.get("pid"):
        try:
            # Kill the process group to ensure all child processes are killed
            os.killpg(os.getpgid(server["pid"]), signal.SIGTERM)
        except ProcessLookupError:
            pass  # Process already dead
        except Exception as e:
            logger.warning(f"Error killing process {server['pid']}: {e}")
    
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "offline", "current_players": 0, "pid": None}}
    )
    
    return {"message": "Server stopped successfully", "status": "offline"}

@api_router.post("/servers/{server_id}/restart")
async def restart_server(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Set restarting status
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "restarting"}}
    )
    
    # Stop the server
    if server.get("pid"):
        try:
            os.killpg(os.getpgid(server["pid"]), signal.SIGTERM)
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.warning(f"Error killing process {server['pid']}: {e}")
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Start the server
    logs_dir = Path("/tmp/arma_servers") / server_id / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "server.log"
    
    process = subprocess.Popen(
        ["bash", "-c", f"while true; do echo '[$(date)] Server running on port {server['port']}...'; sleep 5; done"],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "online", "current_players": 0, "pid": process.pid}}
    )
    
    return {"message": "Server restarted successfully", "status": "online", "pid": process.pid}

# System resources
@api_router.get("/system/resources", response_model=SystemResources)
async def get_system_resources(current_user: dict = Depends(get_current_user)):
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return SystemResources(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_used_gb=round(memory.used / (1024**3), 2),
        memory_total_gb=round(memory.total / (1024**3), 2),
        disk_percent=disk.percent,
        disk_used_gb=round(disk.used / (1024**3), 2),
        disk_total_gb=round(disk.total / (1024**3), 2)
    )

# Server configuration management
@api_router.get("/servers/{server_id}/config", response_model=ServerConfig)
async def get_server_config(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Create config directory if it doesn't exist
    config_dir = Path("/tmp/arma_servers") / server_id
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "server.cfg"
    
    # Create default config if doesn't exist
    if not config_file.exists():
        default_config = f"""// Server Configuration for {server['name']}
hostname = "{server['name']}";
password = "";
passwordAdmin = "admin123";
maxPlayers = {server['max_players']};
motd[] = {{"Welcome to {server['name']}", "Tactical Operations"}};
voteThreshold = 0.33;
voteMissionPlayers = 1;

// Network Settings
serverPort = {server['port']};
serverCommandPassword = "tactical123";

// Gameplay Settings
disableVoN = 0;
persistent = 1;
autoSelectMission = true;

// Performance
maxPing = 200;
maxDesync = 150;
maxPacketLoss = 50;
"""
        config_file.write_text(default_config)
    
    content = config_file.read_text()
    return ServerConfig(content=content)

@api_router.put("/servers/{server_id}/config")
async def update_server_config(
    server_id: str,
    config: ServerConfig,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    config_dir = Path("/tmp/arma_servers") / server_id
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "server.cfg"
    
    config_file.write_text(config.content)
    
    return {"message": "Configuration updated successfully"}

# Mod management
@api_router.get("/servers/{server_id}/mods", response_model=List[ServerMod])
async def get_server_mods(
    server_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify server exists
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    mods = await db.mods.find({"server_id": server_id}, {"_id": 0}).to_list(1000)
    
    for mod in mods:
        if isinstance(mod['created_at'], str):
            mod['created_at'] = datetime.fromisoformat(mod['created_at'])
    
    return mods

@api_router.post("/servers/{server_id}/mods", response_model=ServerMod)
async def add_server_mod(
    server_id: str,
    mod_data: ServerModCreate,
    current_user: dict = Depends(get_current_user)
):
    # Verify server exists
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    mod = ServerMod(
        **mod_data.model_dump(),
        server_id=server_id
    )
    
    doc = mod.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.mods.insert_one(doc)
    
    return mod

@api_router.delete("/servers/{server_id}/mods/{mod_id}")
async def delete_server_mod(
    server_id: str,
    mod_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify server exists
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    result = await db.mods.delete_one({"id": mod_id, "server_id": server_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    return {"message": "Mod deleted successfully"}

@api_router.patch("/servers/{server_id}/mods/{mod_id}/toggle")
async def toggle_server_mod(
    server_id: str,
    mod_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify server exists
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Get current mod state
    mod = await db.mods.find_one({"id": mod_id, "server_id": server_id}, {"_id": 0})
    
    if not mod:
        raise HTTPException(status_code=404, detail="Mod not found")
    
    # Toggle enabled state
    new_state = not mod.get("enabled", True)
    await db.mods.update_one(
        {"id": mod_id},
        {"$set": {"enabled": new_state}}
    )
    
    return {"message": "Mod toggled successfully", "enabled": new_state}

# Log viewer
@api_router.get("/servers/{server_id}/logs", response_model=ServerLogs)
async def get_server_logs(
    server_id: str,
    lines: int = 100,
    current_user: dict = Depends(get_current_user)
):
    server = await db.servers.find_one(
        {"id": server_id, "user_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    log_file = Path("/tmp/arma_servers") / server_id / "logs" / "server.log"
    
    if not log_file.exists():
        return ServerLogs(logs="No logs available yet. Start the server to generate logs.", lines=0)
    
    # Read last N lines
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            logs_content = ''.join(last_lines)
        
        return ServerLogs(logs=logs_content, lines=len(last_lines))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

# SteamCMD management
@api_router.get("/steamcmd/status", response_model=SteamCMDStatus)
async def get_steamcmd_status(current_user: dict = Depends(get_current_user)):
    steamcmd_path = Path.home() / "steamcmd"
    installed = (steamcmd_path / "steamcmd.sh").exists()
    
    return SteamCMDStatus(
        installed=installed,
        path=str(steamcmd_path) if installed else None,
        version="Latest" if installed else None
    )

@api_router.post("/steamcmd/install")
async def install_steamcmd(current_user: dict = Depends(get_current_user)):
    steamcmd_path = Path.home() / "steamcmd"
    
    # Check if already installed
    if (steamcmd_path / "steamcmd.sh").exists():
        return {"message": "SteamCMD is already installed", "path": str(steamcmd_path)}
    
    try:
        # Create directory
        steamcmd_path.mkdir(parents=True, exist_ok=True)
        
        # Download steamcmd
        tar_path = steamcmd_path / "steamcmd_linux.tar.gz"
        url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
        
        urllib.request.urlretrieve(url, tar_path)
        
        # Extract
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=steamcmd_path)
        
        # Remove tar file
        tar_path.unlink()
        
        # Make executable
        (steamcmd_path / "steamcmd.sh").chmod(0o755)
        
        return {
            "message": "SteamCMD installed successfully",
            "path": str(steamcmd_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()