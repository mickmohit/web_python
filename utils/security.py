import jwt
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from model.userLogin import TokenData
import bcrypt

# Security Config
SECRET_KEY = "code"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
# Update the pwd_context configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    #bcrypt__max_password_size=72,  # Explicitly set max password size
    bcrypt__ident="2b"  # Use the more modern bcrypt version
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        print(f"Debug - Plain password: {plain_password}")
        print(f"Debug - Hashed password type: {type(hashed_password)}")
        print(f"Debug - Hashed password value: {hashed_password}")
        
        # If hashed_password is None or empty, return False
        if not hashed_password:
            print("Debug - Hashed password is empty or None")
            return False
            
        # Convert plain password to bytes
        plain_bytes = plain_password.encode('utf-8')
        print(f"Debug - Plain bytes: {plain_bytes}")
        
        # Handle the hashed password
        if isinstance(hashed_password, str):
            print("Debug - Hashed password is a string")
            # If it's a string, it should be in the format $2b$...
            if not hashed_password.startswith('$2b$'):
                print("Debug - Hashed password doesn't start with $2b$")
                return False
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            print("Debug - Hashed password is not a string, assuming bytes")
            hashed_bytes = hashed_password
            
        print(f"Debug - Hashed bytes: {hashed_bytes}")
        
        # Verify the password
        result = bcrypt.checkpw(plain_bytes, hashed_bytes)
        print(f"Debug - Password verification result: {result}")
        return result
        
    except Exception as e:
        print(f"Error in verify_password: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_password_hash(password: str) -> str:
    # Convert to bytes and hash
    password_bytes = password.encode('utf-8')
    # Hash with salt - bcrypt automatically handles the 72-byte limit
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Auth Dependencies
def get_current_user(token: str = Depends(oauth2_scheme)):
    from config.db import conn
    token_data = verify_token(token)
    user_doc = conn.users.user.find_one({"email": token_data.email})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_doc

def get_active_user(current_user = Depends(get_current_user)):
    if not current_user.get('done', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
