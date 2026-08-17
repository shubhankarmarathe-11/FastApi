from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber


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
async def SignupRoute(Cred:SignCred):

    if Cred.username == "shubhankar":
        raise HTTPException(status_code=401,detail="please use different username")

    return Cred

@authroute.post("/api/auth/login")
async def LoginRoute(Cred:LoginCred):
    return Cred
