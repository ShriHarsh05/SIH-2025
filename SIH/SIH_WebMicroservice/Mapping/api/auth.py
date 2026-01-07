# -------------------------------------------------------------
# auth.py - OAuth 2.0 Authentication Module
# -------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

# OAuth setup (only if credentials are provided)
oauth = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    try:
        config = Config(environ={
            "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
            "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET
        })
        oauth = OAuth(config)
        oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        print("✅ Google OAuth configured successfully")
    except Exception as e:
        print(f"⚠️  Google OAuth not configured: {e}")
else:
    print("ℹ️  Google OAuth credentials not provided - using email/password only")

# In-memory user storage (replace with database in production)
# Pre-hashed password for demo user (password: demo123)
fake_users_db = {
    "demo@example.com": {
        "username": "demo@example.com",
        "full_name": "Demo User",
        "email": "demo@example.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJkYvJ3Iu",  # demo123
        "disabled": False,
    }
}

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Optional authentication (returns None if not authenticated)
async def get_optional_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

# Routes
@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Traditional username/password login"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not oauth:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    if not oauth:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            email = user_info.get('email')
            name = user_info.get('name')
            
            # Create or update user in database
            if email not in fake_users_db:
                fake_users_db[email] = {
                    "username": email,
                    "full_name": name,
                    "email": email,
                    "hashed_password": "",  # OAuth users don't need password
                    "disabled": False,
                }
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": email}, expires_delta=access_token_expires
            )
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"http://localhost:8000/ui/index.html?token={access_token}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@router.post("/auth/register")
async def register(username: str, password: str, email: str, full_name: str = ""):
    """Register new user (traditional auth)"""
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    
    return {"message": "User registered successfully"}

@router.post("/auth/logout")
async def logout():
    """Logout (client should delete token)"""
    return {"message": "Logged out successfully"}
