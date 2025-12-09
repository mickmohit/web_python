from pydantic import Field, ConfigDict
from .user import User

class UserResponse(User):
    # to handle the MongoDB _id field. both below setup
    id: str = Field(alias="_id", default=None)
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            "id": str
        }
    )