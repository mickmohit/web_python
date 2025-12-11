from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from routes.userController import user
from routes.registerController import register
from config.db import conn
from utils.security import get_current_user, get_active_user

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with a prefix
app.include_router(user, prefix="/api", tags=["users"])
app.include_router(register, tags=["register"])

# Add pagination support
add_pagination(app)

# Auth dependencies are now imported from utils.security