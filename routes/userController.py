from fastapi import APIRouter, HTTPException, status, Query
from bson import ObjectId
from typing import List, Optional
from config.db import conn
from model.user import User
from model.userResponse import UserResponse
from fastapi_pagination import Page, paginate, Params
from pydantic import BaseModel
import json
  

# Create a router instance
user = APIRouter()

#db = conn.users

# class UserInDB(User):
#     class Config:
#         from_attributes = True
#         json_encoders = {ObjectId: str}

@user.get('/')
async def get_user():
    users = []
    for user in conn.users.user.find():
       # user['id'] = str(user['_id'])
        user['_id'] = str(user['_id'])
        users.append(user)
    return users

@user.get('/user', response_model=Page[UserResponse])
async def get_users_withPagination(
    title: Optional[str] = Query(None, description="Filter users by title"),
    description: Optional[str] = Query(None, description="Matching description for users"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="User per page")):
    #http://localhost:8000/api/user?title=Damn it is working&description=Test&page=2&size=20
    # Build the query
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}  # Case-insensitive search
    if description:
        query["description"] = {"$regex": description, "$options": "i"}
    
    # Get total count for pagination
    total = conn.users.user.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * size
    cursor = conn.users.user.find(query).skip(skip).limit(size)

    # Convert cursor to list and handle _id conversion
    users = []
    for user_doc in cursor:
        user_dict = dict(user_doc)
        user_dict["_id"] = str(user_dict["_id"])
        users.append(user_dict)
    
    # Return paginated results
    return paginate(users)
    

@user.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    # Convert the Pydantic model to a dict and insert into MongoDB
    #user_dict = user.dict()
    user_dict = user.model_dump()  # Changed from dict() to model_dump()
   
    result = conn.users.user.insert_one(dict(user_dict))
    
    # Fetch the created document
    created_user = conn.users.user.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string and rename _id to id
    created_user['id'] = str(created_user.pop('_id'))
    
    # Return the created user with the proper response model
    #you are passing the contents of the created_user variable as keyword arguments (kwargs) to the UserResponse constructor or function. This is known as dictionary unpacking. 
    return UserResponse(**created_user)

@user.put('/{user_id}', response_model=UserResponse)
async def update_user(user_id: str, user: User):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    update_data = dict(user)
    print(update_data)
    result = conn.users.user.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = conn.users.user.find_one({"_id": ObjectId(user_id)})
    updated_user['id'] = str(updated_user.pop('_id'))
    return UserResponse(**updated_user)
   

@user.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    result = conn.users.user.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return None

@user.get('/{user_id}', response_model=UserResponse)
async def get_user_single(user_id: str):
   if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
   user = conn.users.user.find_one({"_id": ObjectId(user_id)})
    
   if not user:
        raise HTTPException(status_code=404, detail="User not found")
   
   user['id'] = str(user.pop('_id'))
   return UserResponse(**user)
   