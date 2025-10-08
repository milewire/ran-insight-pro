from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from token"""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }

# Global auth service instance
auth_service = AuthService()

# For future use - user management
class UserManager:
    """User management service (placeholder for future implementation)"""
    
    def __init__(self):
        self.users = {}  # In production, this would be a database
    
    def create_user(self, username: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Create a new user"""
        user_id = f"user_{len(self.users) + 1}"
        hashed_password = auth_service.get_password_hash(password)
        
        user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "role": role,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        self.users[user_id] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        for user in self.users.values():
            if user["username"] == username and auth_service.verify_password(password, user["hashed_password"]):
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)

# Global user manager instance
user_manager = UserManager()
