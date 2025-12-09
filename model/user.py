from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    
    title: str
    description: Optional[str] = None
    done: bool