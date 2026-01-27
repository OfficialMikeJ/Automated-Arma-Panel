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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

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
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
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
    
    # Simulate server start (in real implementation, you would start the actual server process)
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "online", "current_players": 0}}
    )
    
    return {"message": "Server started successfully", "status": "online"}

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
    
    # Simulate server stop
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "offline", "current_players": 0}}
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
    
    # Simulate server restart
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "restarting"}}
    )
    
    # Simulate restart delay
    await asyncio.sleep(2)
    
    await db.servers.update_one(
        {"id": server_id},
        {"$set": {"status": "online", "current_players": 0}}
    )
    
    return {"message": "Server restarted successfully", "status": "online"}

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