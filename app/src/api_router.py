from fastapi import APIRouter, HTTPException, Path
from models import User_Account
from typing import List, Optional
from beanie import PydanticObjectId
from models import LoginRequest
from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from pydantic import EmailStr
from passlib.context import CryptContext


SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(email, password, user_account: User_Account):
    if email != user_account.email:
        return False
    return pwd_context.verify(password, user_account.password)

def get_password_hash(password):
    return pwd_context.hash(password)




@router.post('/login')
async def login(request_data: LoginRequest):
    user_account = await User_Account.find_one(User_Account.email == request_data.email)

    if verify_password(email=request_data.email, password=request_data.password, user_account=user_account):
        return user_account
    else:
        raise HTTPException(status_code=404, detail="User not found or password incorrect")

@router.get('/')
async def getalluser() -> List[User_Account]:
    user_account = await User_Account.find_all().to_list()
    if user_account == None:
        raise HTTPException(
            status_code=404,
            detail="Don't have any user ask yet"
        )
    
    return user_account

@router.post('/v1/users/signup')
async def createUser(email: str, password: str):
    try:
        user_account_create = User_Account(
            email=email,
            password=get_password_hash(password),
            
        )
        user = await user_account_create.create()
        return {"message": "User has been saved"} 
        # return user
    except Exception as e:
        raise HTTPException(
            status_code=400,  
            detail=f"Failed to create user", 
        )

@router.get('/{user_id}')
async def get_user_by_id(user_id: PydanticObjectId = Path(...)) -> User_Account:
    user_to_get = await User_Account.get(user_id)
    return user_to_get

@router.put('/{user_id}')
async def updateUser(user_id: PydanticObjectId = Path(...), user: User_Account = None) -> User_Account:
    user_to_update = await User_Account.get(user_id)
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    

    user_to_update.email = user.email
    user_to_update.password = user.password

    await user_to_update.save()
    return user_to_update

@router.delete('/{user_id}')
async def deleteUser(user_id: PydanticObjectId = Path(...)):
    user_to_delete = await User_Account.get(user_id)

    await user_to_delete.delete()

    return {"message": "User deleted"}


