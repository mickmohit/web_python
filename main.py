from fastapi.middleware.cors import CORSMiddleware
from routes.userController import user
from fastapi import FastAPI
from fastapi_pagination import add_pagination


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
# Add this at the end of the file
add_pagination(app)

