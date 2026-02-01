from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, validator
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
import pyotp
import qrcode
import io
import re

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

# Configurable settings
SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', '60'))  # Default 60 minutes
PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '8'))
PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
PASSWORD_REQUIRE_NUMBERS = os.environ.get('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true'
PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'

# TOTP settings
TOTP_ISSUER = "Tactical Command Panel"

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
    security_questions: Optional[dict] = None
    totp_secret: Optional[str] = None
    totp_enabled: bool = False
    is_admin: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    # Sub-admin fields
    is_sub_admin: bool = False
    parent_admin_id: Optional[str] = None  # ID of the admin who created this sub-admin
    server_permissions: dict = Field(default_factory=dict)  # {server_id: {view, edit, start, stop, restart}}

class PasswordComplexityConfig(BaseModel):
    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_special: bool

class UserCreate(BaseModel):
    username: str
    password: str
    security_questions: Optional[dict] = None
    
    @validator('password')
    def validate_password(cls, v):
        errors = []
        
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
        
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if PASSWORD_REQUIRE_NUMBERS and not re.search(r'[0-9]', v):
            errors.append("Password must contain at least one number")
        
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None

class TOTPSetup(BaseModel):
    pass

class TOTPVerify(BaseModel):
    totp_code: str

class TOTPDisable(BaseModel):
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
    
    @validator('new_password')
    def validate_password(cls, v):
        errors = []
        
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
        
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if PASSWORD_REQUIRE_NUMBERS and not re.search(r'[0-9]', v):
            errors.append("Password must contain at least one number")
        
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v

class FirstTimeSetup(BaseModel):
    username: str
    password: str
    security_questions: dict
    
    @validator('password')
    def validate_password(cls, v):
        errors = []
        
        if len(v) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
        
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if PASSWORD_REQUIRE_NUMBERS and not re.search(r'[0-9]', v):
            errors.append("Password must contain at least one number")
        
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    requires_totp_setup: bool = False
    totp_enabled: bool = False
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES

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
    # Resource allocations
    cpu_cores: int = 2  # Number of CPU cores allocated
    ram_gb: int = 4  # RAM in GB
    storage_gb: int = 50  # Storage in GB
    network_speed_mbps: int = 100  # Network speed in Mbps

class ServerInstanceCreate(BaseModel):
    name: str
    game_type: str
    port: int
    max_players: int
    install_path: str
    cpu_cores: int = 2
    ram_gb: int = 4
    storage_gb: int = 50
    network_speed_mbps: int = 100

class ServerInstanceUpdate(BaseModel):
    name: Optional[str] = None
    port: Optional[int] = None
    max_players: Optional[int] = None
    current_players: Optional[int] = None
    status: Optional[str] = None
    cpu_cores: Optional[int] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    network_speed_mbps: Optional[int] = None

class SubAdminCreate(BaseModel):
    username: str
    password: str
    server_permissions: dict = Field(default_factory=dict)

class SubAdminUpdate(BaseModel):
    password: Optional[str] = None
    server_permissions: Optional[dict] = None

class ServerPermissions(BaseModel):
    view: bool = True
    edit: bool = False
    start: bool = False
    stop: bool = False
    restart: bool = False

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {"user_id": user_id, "username": payload.get("username")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        # Catch any other exceptions and return 401
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def check_server_permission(
    server_id: str,
    user_id: str,
    required_permission: str  # 'view', 'edit', 'start', 'stop', 'restart'
) -> bool:
    """Check if user has permission to perform action on server"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        return False
    
    # Admins have all permissions
    if user.get("is_admin"):
        return True
    
    # Check sub-admin permissions
    if user.get("is_sub_admin"):
        permissions = user.get("server_permissions", {}).get(server_id, {})
        return permissions.get(required_permission, False)
    
    return False

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
        username=user.username,
        requires_totp_setup=True,  # First admin login should setup TOTP
        totp_enabled=False
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
    
    # Check if TOTP is enabled
    totp_enabled = user.get("totp_enabled", False)
    
    if totp_enabled:
        # TOTP is enabled, verify code
        if not user_data.totp_code:
            raise HTTPException(status_code=401, detail="2FA code required")
        
        totp = pyotp.TOTP(user["totp_secret"])
        if not totp.verify(user_data.totp_code, valid_window=1):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["id"], "username": user["username"]}
    )
    
    # Check if admin needs to setup TOTP (first login after creation)
    requires_totp_setup = (
        user.get("is_admin", False) and 
        not totp_enabled and 
        user.get("last_login") is None
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        username=user["username"],
        requires_totp_setup=requires_totp_setup,
        totp_enabled=totp_enabled
    )

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetRequest):
    """Reset password using security questions"""
    # Find user
    user = await db.users.find_one({"username": reset_data.username}, {"_id": 0})
    if not user:
        # Don't reveal if user exists for security reasons
        raise HTTPException(status_code=400, detail="Invalid username or security answers")
    
    # Check if user has security questions
    if not user.get("security_questions"):
        raise HTTPException(status_code=400, detail="Security questions not set up for this user")
    
    # Verify all security answers
    security_questions = user["security_questions"]
    answers_to_verify = [
        ("question1", reset_data.answer1),
        ("question2", reset_data.answer2),
        ("question3", reset_data.answer3),
        ("question4", reset_data.answer4)
    ]
    
    all_correct = True
    for question_key, provided_answer in answers_to_verify:
        stored_hash = security_questions.get(question_key)
        if not stored_hash:
            continue  # Skip if question not set
        if not verify_password(provided_answer.lower().strip(), stored_hash):
            all_correct = False
            break
    
    if not all_correct:
        raise HTTPException(status_code=400, detail="Invalid username or security answers")
    
    # All answers correct, update password
    new_hashed_password = hash_password(reset_data.new_password)
    await db.users.update_one(
        {"username": reset_data.username},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {"message": "Password reset successfully"}
        {"id": user["id"]},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {"message": "Password reset successfully"}

@api_router.get("/auth/security-questions/{username}")
async def get_security_questions(username: str):
    """Get the security questions for a user (not the answers)"""
    user = await db.users.find_one({"username": username}, {"_id": 0, "security_questions": 1})
    if not user or not user.get("security_questions"):
        raise HTTPException(status_code=404, detail="Security questions not found")
    
    # Return only the question keys, not the hashed answers
    return {
        "has_questions": True,
        "questions": list(user["security_questions"].keys())
    }

@api_router.get("/auth/password-config", response_model=PasswordComplexityConfig)
async def get_password_config():
    """Get password complexity requirements"""
    return PasswordComplexityConfig(
        min_length=PASSWORD_MIN_LENGTH,
        require_uppercase=PASSWORD_REQUIRE_UPPERCASE,
        require_lowercase=PASSWORD_REQUIRE_LOWERCASE,
        require_numbers=PASSWORD_REQUIRE_NUMBERS,
        require_special=PASSWORD_REQUIRE_SPECIAL
    )

# TOTP/2FA routes
@api_router.post("/auth/totp/setup")
async def setup_totp(current_user: dict = Depends(get_current_user)):
    """Generate TOTP secret and QR code for user"""
    user = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new TOTP secret
    totp_secret = pyotp.random_base32()
    
    # Store secret (not enabled yet)
    await db.users.update_one(
        {"id": current_user["user_id"]},
        {"$set": {"totp_secret": totp_secret}}
    )
    
    # Generate provisioning URI
    totp = pyotp.TOTP(totp_secret)
    provisioning_uri = totp.provisioning_uri(
        name=user["username"],
        issuer_name=TOTP_ISSUER
    )
    
    return {
        "secret": totp_secret,
        "provisioning_uri": provisioning_uri,
        "qr_code_url": f"/api/auth/totp/qr/{current_user['user_id']}"
    }

@api_router.get("/auth/totp/qr/{user_id}")
async def get_totp_qr(user_id: str):
    """Generate QR code for TOTP setup"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user or not user.get("totp_secret"):
        raise HTTPException(status_code=404, detail="TOTP not set up")
    
    # Generate provisioning URI
    totp = pyotp.TOTP(user["totp_secret"])
    provisioning_uri = totp.provisioning_uri(
        name=user["username"],
        issuer_name=TOTP_ISSUER
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")

@api_router.post("/auth/totp/verify")
async def verify_totp_setup(
    verify_data: TOTPVerify,
    current_user: dict = Depends(get_current_user)
):
    """Verify TOTP code and enable 2FA"""
    user = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not user or not user.get("totp_secret"):
        raise HTTPException(status_code=400, detail="TOTP not set up")
    
    # Verify code
    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(verify_data.totp_code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")
    
    # Enable TOTP
    await db.users.update_one(
        {"id": current_user["user_id"]},
        {"$set": {"totp_enabled": True}}
    )
    
    return {"message": "2FA enabled successfully"}

@api_router.post("/auth/totp/disable")
async def disable_totp(
    disable_data: TOTPDisable,
    current_user: dict = Depends(get_current_user)
):
    """Disable TOTP/2FA"""
    user = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if not verify_password(disable_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Disable TOTP
    await db.users.update_one(
        {"id": current_user["user_id"]},
        {"$set": {"totp_enabled": False, "totp_secret": None}}
    )
    
    return {"message": "2FA disabled successfully"}

@api_router.get("/auth/totp/status")
async def get_totp_status(current_user: dict = Depends(get_current_user)):
    """Check if user has TOTP enabled"""
    user = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0, "totp_enabled": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"totp_enabled": user.get("totp_enabled", False)}

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
    
    # Check if server is already running
    if server.get("status") == "online" and server.get("pid"):
        try:
            # Check if process is still alive
            os.kill(server["pid"], 0)
            return {"message": "Server is already running", "status": "online", "pid": server["pid"]}
        except OSError:
            # Process is dead, continue with start
            pass
    
    # Create server directory structure
    server_dir = Path(server["install_path"])
    logs_dir = server_dir / "logs"
    configs_dir = server_dir / "configs"
    profiles_dir = server_dir / "profiles"
    
    logs_dir.mkdir(parents=True, exist_ok=True)
    configs_dir.mkdir(parents=True, exist_ok=True)
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if server executable exists
    if server["game_type"] == "arma_reforger":
        server_executable = server_dir / "ArmaReforgerServer"
    else:  # arma_4 (for future)
        server_executable = server_dir / "Arma4Server"
    
    if not server_executable.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Server executable not found at {server_executable}. Please install the server files first using SteamCMD (App ID: 1874900 for Arma Reforger)."
        )
    
    # Make executable if not already
    server_executable.chmod(0o755)
    
    # Create server configuration file if it doesn't exist
    config_file = configs_dir / "server.json"
    if not config_file.exists():
        config_data = {
            "bindAddress": "0.0.0.0",
            "bindPort": server["port"],
            "publicAddress": "",  # Leave empty for auto-detection
            "publicPort": server["port"],
            "a2s": {
                "address": "",
                "port": server["port"] + 16  # A2S port typically game_port + 16
            },
            "game": {
                "name": server["name"],
                "password": "",
                "passwordAdmin": "changeme",
                "maxPlayers": server["max_players"],
                "visible": True
            },
            "mods": []
        }
        
        import json
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
    
    # Prepare start command
    log_file = logs_dir / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    cmd = [
        str(server_executable),
        f"-config={config_file}",
        f"-profile={profiles_dir}",
        "-maxFPS=60"
    ]
    
    # Start the server process
    try:
        process = subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=str(server_dir),
            preexec_fn=os.setsid  # Create new process group for proper cleanup
        )
        
        # Wait a moment to check if process started successfully
        await asyncio.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process died immediately
            with open(log_file, "r") as f:
                error_log = f.read()
            raise HTTPException(
                status_code=500,
                detail=f"Server failed to start. Check log file: {log_file}. Error: {error_log[-500:]}"
            )
        
        # Update server status
        await db.servers.update_one(
            {"id": server_id},
            {"$set": {"status": "online", "current_players": 0, "pid": process.pid}}
        )
        
        return {
            "message": "Server started successfully",
            "status": "online",
            "pid": process.pid,
            "log_file": str(log_file)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start server: {str(e)}"
        )

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
    
    if server.get("status") == "offline":
        return {"message": "Server is already offline", "status": "offline"}
    
    # Kill the process if it exists
    if server.get("pid"):
        try:
            # Send SIGTERM first (graceful shutdown)
            os.killpg(os.getpgid(server["pid"]), signal.SIGTERM)
            
            # Wait up to 10 seconds for process to terminate
            for _ in range(10):
                try:
                    os.kill(server["pid"], 0)  # Check if process still exists
                    await asyncio.sleep(1)
                except OSError:
                    break  # Process is dead
            else:
                # Process still alive after 10 seconds, force kill
                try:
                    os.killpg(os.getpgid(server["pid"]), signal.SIGKILL)
                    logger.warning(f"Server {server_id} required SIGKILL to stop")
                except ProcessLookupError:
                    pass
        except ProcessLookupError:
            pass  # Process already dead
        except Exception as e:
            logger.warning(f"Error stopping server {server_id} (PID: {server['pid']}): {e}")
    
    # Update server status
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
    
    # Stop the server first
    if server.get("pid"):
        try:
            # Send SIGTERM for graceful shutdown
            os.killpg(os.getpgid(server["pid"]), signal.SIGTERM)
            
            # Wait up to 10 seconds for process to terminate
            for _ in range(10):
                try:
                    os.kill(server["pid"], 0)
                    await asyncio.sleep(1)
                except OSError:
                    break
            else:
                # Force kill if still alive
                try:
                    os.killpg(os.getpgid(server["pid"]), signal.SIGKILL)
                except ProcessLookupError:
                    pass
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.warning(f"Error stopping server during restart: {e}")
    
    # Wait a moment before restarting
    await asyncio.sleep(2)
    
    # Start the server again (reuse start logic)
    try:
        server_dir = Path(server["install_path"])
        logs_dir = server_dir / "logs"
        configs_dir = server_dir / "configs"
        profiles_dir = server_dir / "profiles"
        
        if server["game_type"] == "arma_reforger":
            server_executable = server_dir / "ArmaReforgerServer"
        else:
            server_executable = server_dir / "Arma4Server"
        
        if not server_executable.exists():
            await db.servers.update_one(
                {"id": server_id},
                {"$set": {"status": "offline", "pid": None}}
            )
            raise HTTPException(
                status_code=400,
                detail=f"Server executable not found at {server_executable}"
            )
        
        config_file = configs_dir / "server.json"
        log_file = logs_dir / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        cmd = [
            str(server_executable),
            f"-config={config_file}",
            f"-profile={profiles_dir}",
            "-maxFPS=60"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=str(server_dir),
            preexec_fn=os.setsid
        )
        
        await asyncio.sleep(2)
        
        if process.poll() is not None:
            await db.servers.update_one(
                {"id": server_id},
                {"$set": {"status": "offline", "pid": None}}
            )
            raise HTTPException(
                status_code=500,
                detail=f"Server failed to restart. Check log: {log_file}"
            )
        
        await db.servers.update_one(
            {"id": server_id},
            {"$set": {"status": "online", "current_players": 0, "pid": process.pid}}
        )
        
        return {
            "message": "Server restarted successfully",
            "status": "online",
            "pid": process.pid,
            "log_file": str(log_file)
        }
    except Exception as e:
        await db.servers.update_one(
            {"id": server_id},
            {"$set": {"status": "offline", "pid": None}}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart server: {str(e)}"
        )
    
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


###############################################################################
# Sub-Admin Management Routes
###############################################################################

@api_router.post("/admin/sub-admins")
async def create_sub_admin(
    sub_admin: SubAdminCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new sub-admin user (Admin only)"""
    # Verify current user is admin
    admin = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not admin or not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can create sub-admins")
    
    # Check if username exists
    existing = await db.users.find_one({"username": sub_admin.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create sub-admin user
    user = User(
        username=sub_admin.username,
        hashed_password=hash_password(sub_admin.password),
        is_sub_admin=True,
        parent_admin_id=current_user["user_id"],
        server_permissions=sub_admin.server_permissions
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('last_login'):
        doc['last_login'] = doc['last_login'].isoformat()
    
    await db.users.insert_one(doc)
    
    return {
        "message": "Sub-admin created successfully",
        "username": user.username,
        "id": user.id
    }

@api_router.get("/admin/sub-admins")
async def list_sub_admins(current_user: dict = Depends(get_current_user)):
    """List all sub-admins created by current admin"""
    admin = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not admin or not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can view sub-admins")
    
    sub_admins = await db.users.find(
        {"parent_admin_id": current_user["user_id"], "is_sub_admin": True},
        {"_id": 0, "hashed_password": 0, "totp_secret": 0}
    ).to_list(1000)
    
    return sub_admins

@api_router.get("/admin/sub-admins/{sub_admin_id}")
async def get_sub_admin(
    sub_admin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific sub-admin details"""
    admin = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not admin or not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can view sub-admins")
    
    sub_admin = await db.users.find_one(
        {"id": sub_admin_id, "parent_admin_id": current_user["user_id"]},
        {"_id": 0, "hashed_password": 0, "totp_secret": 0}
    )
    
    if not sub_admin:
        raise HTTPException(status_code=404, detail="Sub-admin not found")
    
    return sub_admin

@api_router.put("/admin/sub-admins/{sub_admin_id}")
async def update_sub_admin(
    sub_admin_id: str,
    update_data: SubAdminUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update sub-admin permissions or password"""
    admin = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not admin or not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can update sub-admins")
    
    sub_admin = await db.users.find_one(
        {"id": sub_admin_id, "parent_admin_id": current_user["user_id"]},
        {"_id": 0}
    )
    
    if not sub_admin:
        raise HTTPException(status_code=404, detail="Sub-admin not found")
    
    update_fields = {}
    if update_data.password:
        update_fields["hashed_password"] = hash_password(update_data.password)
    if update_data.server_permissions is not None:
        update_fields["server_permissions"] = update_data.server_permissions
    
    if update_fields:
        await db.users.update_one(
            {"id": sub_admin_id},
            {"$set": update_fields}
        )
    
    return {"message": "Sub-admin updated successfully"}

@api_router.delete("/admin/sub-admins/{sub_admin_id}")
async def delete_sub_admin(
    sub_admin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a sub-admin user"""
    admin = await db.users.find_one({"id": current_user["user_id"]}, {"_id": 0})
    if not admin or not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can delete sub-admins")
    
    result = await db.users.delete_one({
        "id": sub_admin_id,
        "parent_admin_id": current_user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sub-admin not found")
    
    return {"message": "Sub-admin deleted successfully"}

###############################################################################
# Changelog/Updates Route
###############################################################################

@api_router.get("/changelog")
async def get_changelog():
    """Get changelog for display on login page"""
    changelog_path = Path("/app/CHANGELOG.md")
    
    if not changelog_path.exists():
        return {"content": "# No updates available\n\nCheck back later for updates and fixes."}
    
    content = changelog_path.read_text()
    
    # Parse and return recent entries (last 50 lines or until [Previous])
    lines = content.split('\n')
    recent_lines = []
    for line in lines:
        if '[Previous]' in line:
            break
        recent_lines.append(line)
        if len(recent_lines) >= 100:  # Limit to prevent huge responses
            break
    
    return {"content": '\n'.join(recent_lines)}



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



# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch all unhandled exceptions and return proper error response"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(jwt.JWTError)
async def jwt_exception_handler(request, exc):
    """Handle JWT errors consistently"""
    logger.warning(f"JWT error: {exc}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"}
    )

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()