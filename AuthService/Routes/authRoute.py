from fastapi import APIRouter,HTTPException, Response,Depends,Request
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Services.AuthServices import InsertUser,GetUserDetails,DeleteUser
from datetime import datetime
from Config.envConfig import Settings,get_settings
from starlette import status
from Config.redisConnection import redisConnect


async def VerifyInternalHeader(req:Request,res:Response):
    env:Settings = get_settings()
    
    backendToken = req.headers.get("x-internal-secret");
    actualToken = env.internal_token;

    if backendToken is None or backendToken != actualToken:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message":"Access forbidden: Invalid token"}
        )




authroute = APIRouter(
    prefix="/api/auth",
    dependencies=[Depends(VerifyInternalHeader)]
)

class SignCred(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)
    sub: str = Field(default="")
    picture: str = Field(default="")

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)




@authroute.post("/signup")
async def SignupRoute(Cred:SignCred,res: Response):

    result = await InsertUser(Cred)
    if result == "Duplicate entry":
        raise HTTPException(status_code=400,detail={"userid":"","message":"User already exists"})

    elif result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})        
    
    else:
        raise HTTPException(status_code=201,detail=result)

@authroute.post("/login")
async def LoginRoute(Cred:LoginCred):

    result = await GetUserDetails(Cred)

    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})
    elif result == "User not found":
        raise HTTPException(status_code=404,detail={"userid":"","message":"user not found"})
    elif result == "Incorrect Password":
        raise HTTPException(status_code=401,detail={"userid":"","message":"Incorrect Password"})
    else:
        raise HTTPException(status_code=200,detail=result)


@authroute.delete("/accountdelete")
async def AccountDelete(userId:str):


    result = await DeleteUser(UserId=userId)
    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"message":"Internal server error"})
    else:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,detail={"message":result})

