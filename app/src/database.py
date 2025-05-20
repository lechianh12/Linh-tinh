import motor
import motor.motor_asyncio
import beanie
from models import User_Account
from dotenv import load_dotenv
import os
load_dotenv() 


MONGODB_URL = os.getenv("MONGODB_URL")
# MONGODB_URL = "mongodb://localhost:27017"
if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not set in .env file")

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

    await beanie.init_beanie(
        database=client.User_Mangement, 
        document_models=[User_Account]
    )