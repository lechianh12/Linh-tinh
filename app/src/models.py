from beanie import Document
from datetime import datetime
from pydantic import Field, EmailStr
from typing import Optional
from pydantic import BaseModel, ConfigDict
import uuid

class User_Account(Document):
    email: Optional[EmailStr]
    password: str
    date_created: datetime = datetime.now()




    class Settings:
        name = "user account management"

    class Config:
        json_schema_extra = {
            "email": "user@example.com",
            "password": "12345678",
            "date_created":datetime.now(),
        }


class LoginRequest(BaseModel):
    email: str
    password: str
