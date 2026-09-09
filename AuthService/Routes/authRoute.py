from fastapi import APIRouter,HTTPException, Response
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Services.AuthServices import InsertUser,GetUserDetails

authroute = APIRouter()

class SignCred(BaseModel):
    username: str
    email: EmailStr
    number: PhoneNumber
    password: str = Field(min_length=8,max_length=16)

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)



@authroute.post("/api/auth/signup")
async def SignupRoute(Cred:SignCred,res: Response):

    result = await InsertUser(Cred)
    if result == "Duplicate entry":
        raise HTTPException(status_code=400,detail="User already exists")

# key: str, value, max_age, expires, path, domain, secure, httponly, samesite, partitioned

    raise HTTPException(status_code=201,detail="User created successfully")

@authroute.post("/api/auth/login")
async def LoginRoute(Cred:LoginCred):

    result = await GetUserDetails(Cred)

    if result == "Database Error":
        raise HTTPException(status_code=500,detail="Internal server error")
    elif result == "User not found":
        raise HTTPException(status_code=404,detail="user not found")
    elif result == "Incorrect Password":
        raise HTTPException(status_code=401,detail="Incorrect Password")
    else:
        raise HTTPException(status_code=200,detail="correct credentials")


