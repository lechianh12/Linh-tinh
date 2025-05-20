# # File main.py

# import uvicorn
# from fastapi import FastAPI, Depends
# from pydantic import BaseModel
# from fastapi.security import HTTPBearer


# from datetime import datetime

# import jwt
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer
# from pydantic import ValidationError


# import motor
# import motor.motor_asyncio
# import beanie
# from beanie import Document
# from typing import Optional
# from pydantic import EmailStr


# class Task(Document):
#     email: Optional[EmailStr]
#     password: str
#     date_created: datetime = datetime.now()
#     token: Optional[str] = None

#     class Settings:
#         name = "user account management"

#     class Config:
#         schema_extra = {
#             "email": "user@example.com",
#             "password": "12345678",
#             "date_created":datetime.now(),
#         }

# async def init_db():
#     client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017//db_name//user accout management")

#     await beanie.init_beanie(
#         database=client.db_name,
#         document_models=[Task]
#     )




# reusable_oauth2 = HTTPBearer(
#     scheme_name='Authorization'
# )


# SECURITY_ALGORITHM = 'HS256'
# SECRET_KEY = '123456'

# reusable_oauth2 = HTTPBearer(
#     scheme_name='Authorization'
# )

# def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> str:
#     """
#     Decode JWT token to get username => return username
#     """
#     try:
#         payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
#         if payload.get('username') < datetime.now():
#             raise HTTPException(status_code=403, detail="Token expired")
#         return payload.get('username')
#     except(jwt.PyJWTError, ValidationError):
#         raise HTTPException(
#             status_code=403,
#             detail=f"Could not validate credentials",
#         )



# app = FastAPI(
#     title='FastAPI JWT', openapi_url='/openapi.json', docs_url='/docs',
#     description='fastapi jwt'
# )

# @app.on_event('startup')
# async def connect():
#     await init_db()


# @app.get('/books', dependencies=[Depends(reusable_oauth2)])
# def list_books():
#     return {'data': ['Sherlock Homes', 'Harry Potter', 'Rich Dad Poor Dad']}

# if __name__ == '__main__':
#     uvicorn.run(app, port=3000)

# File test_db_connection.py

# File test_db_connection.py

# File test_db_connection.py

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
import motor.motor_asyncio
import beanie
from beanie import Document
from typing import Optional
from pydantic import EmailStr, ValidationError
from datetime import datetime, timedelta
import jwt


SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = 'your_secret_key'  
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Task(Document):
    email: Optional[EmailStr]
    password: str
    date_created: datetime = datetime.now()
    token: Optional[str] = None

    class Settings:
        name = "user account management"

    class Config:
        schema_extra = {
            "email": "test@example.com",
            "password": "test_password",
            "date_created": datetime.now(),
        }




async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    await beanie.init_beanie(
        database=client.get_database("User_Mangement"),
        document_models=[Task]
    )

async def get_all_tasks():
    tasks = await Task.find_all().to_list()
    for task in tasks:
        print(task.title, task.completed)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt


reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)

async def get_current_user(http_authorization_credentials: HTTPBearer = Depends(reusable_oauth2)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception
    user = await Task.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

app = FastAPI(
    title='FastAPI Test DB Connection and JWT',
    description='Simple FastAPI app to test MongoDB connection, Beanie setup, and JWT authentication'
)

@app.on_event('startup')
async def connect_db():
    try:
        await init_db()
        print("Successfully connected to MongoDB and initialized Beanie.")
    except Exception as e:
        print(f"Error connecting to MongoDB or initializing Beanie: {e}")

@app.get("/ping")
async def ping():
    try:
        count = await Task.all().count()
        first_user = await Task.find_one()
        access_token = None
        if first_user:
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"email": first_user.email}, expires_delta=access_token_expires
            )
        return {
            "message": "Successfully connected and can query the database.",
            "collection_count": count,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query the database or generate token: {e}")

@app.get("/protected", dependencies=[Depends(get_current_user)])
async def protected_route(current_user: Task = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}! This is a protected endpoint.", "user_id": str(current_user.id)}

if __name__ == '__main__':

    uvicorn.run(app, port=8001)
    


