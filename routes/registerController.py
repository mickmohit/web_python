from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from bson import ObjectId
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import timedelta
from fastapi import status
from utils.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from config.db import conn
from utils.security import create_access_token, get_active_user, get_password_hash, verify_password
from model.user import User
from model.userLogin import Token
from model.userResponse import UserResponse
from fastapi_pagination import Page, paginate, Params
from pydantic import BaseModel
import json

# Create a router instance
register = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@register.post("/register", response_model=UserResponse)
def register_user(user: User):
    user_doc = conn.users.user.find_one({"email": user.email})
    if user_doc:
         raise HTTPException(
                status_code=404,
                detail="User Already Exists!"
            )
    
    hashed_password = get_password_hash(user.hashed_password)
    print(f"Debug - Hashed password during registration: {hashed_password}")  # Debug log
    input_user = User(
        title=user.title,
        description=user.description,
        done=user.done,
        name=user.name,
        email=user.email,
        hashed_password=hashed_password  # Use the hashed password, not the plain one
    )

    user_dict = input_user.model_dump(exclude={"id"})  # Changed from dict() to model_dump()
    #user_dict["hashed_password"] = hashed_password  # Update with hashed password
       
    result = conn.users.user.insert_one(dict(user_dict))
   
   #to handle pop, as mongo return insertone object not dict - Create a response that matches UserResponse model
    response = user_dict.copy()
    response["id"] = str(result.inserted_id)
    return response

@register.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_doc = conn.users.user.find_one({"email": form_data.username})

    if not user_doc or not verify_password(form_data.password, user_doc["hashed_password"]): #access mongo doc object like user_doc["hashed_password"]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    if not user_doc.get("done", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_doc["email"]}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type":"bearer"}
    
@register.get("/profile", response_model=UserResponse)
def get_profile(current_user:User = Depends(get_active_user)):
   # Convert ObjectId to string for the response
    current_user["id"] = str(current_user.pop("_id"))
    return current_user

@register.get("/verify-token")
def verify_token_endpoint(current_user:User = Depends(get_active_user)):
    return {
        "valid": True,
        "user": { 
           # "id":current_user.id,
           "name": current_user.get("name"),
           "email": current_user.get("email")
        }
    }