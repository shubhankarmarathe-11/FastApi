from fastapi import APIRouter,HTTPException, Response,Depends,Request
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Services.AuthServices import InsertUser,GetUserDetails,DeleteUser,VerifyIsUser,UpdatePassword,InsertUserGoogle,GetUserDetailsGoogle,Is_Authenticated,Is_Password_Added,Add_Account_Password,Update_Email_Status
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
    password: str = Field(default="",min_length=8,max_length=16)
    sub: str = Field(default="")
    picture: str = Field(default="")

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)


class is_userCred(BaseModel):
    email: EmailStr


class GoogleCred(BaseModel):
    username: str
    email: EmailStr
    sub: str = Field(default="")
    picture: str = Field(default="")

class is_email_authenticated(BaseModel):
    userid: str


class AccountPasswordCred(BaseModel):
    password: str = Field(default="",min_length=8,max_length=16)


@authroute.get("/is_authenticated")
async def Is_Email_Authenticated(request:Request):
    userid = request.headers.get('userid')

    result = await Is_Authenticated(userid)

    if result == "not verified":
        raise HTTPException(status_code=406,detail={"message":"not verified"})

    
    elif result == "Database Error":
        raise HTTPException(status_code=500,detail={"message":"Internal server error"})

    else:
        raise HTTPException(status_code=200,detail={"message":"verified"})

@authroute.get("/is_password_added")
async def Is_PasswordAdded(request:Request):
    userid = request.headers.get('userid')

    print(userid)
    
    result = await Is_Password_Added(userid)
    
    if result == "not added":
        raise HTTPException(status_code=406,detail={"message":"not added"})
    
        
    elif result == "Database Error":
        raise HTTPException(status_code=500,detail={"message":"Internal server error"})
    
    else:
        raise HTTPException(status_code=200,detail={"message":"added"})


@authroute.post("/signup/google")
async def SignupWithGoogle(UserCred:GoogleCred):
    result = await InsertUserGoogle(UserCred)
    if result == "Duplicate entry":
        raise HTTPException(status_code=400,detail={"userid":"","message":"User already exists"})
    
    elif result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})        
        
    else:
        raise HTTPException(status_code=201,detail=result)

@authroute.post("/login/google")
async def SignupWithGoogle(UserCred:GoogleCred):
    result = await GetUserDetailsGoogle(UserCred)
    
    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})
    elif result == "User not found":
        raise HTTPException(status_code=404,detail={"userid":"","message":"user not found"})
    elif result == "Incorrect Password":
        raise HTTPException(status_code=401,detail={"userid":"","message":"Incorrect token id"})
    else:
        raise HTTPException(status_code=200,detail=result)



@authroute.post("/is_user")
async def is_User(IsUserCred:is_userCred):
    result = await VerifyIsUser(email=IsUserCred.email)
    if result['message'] == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})        

    elif result['message'] == "User not found":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={"userid":"","message":"not user"})

    raise HTTPException(status_code=status.HTTP_200_OK,detail={"userid":result["userid"],"message":"is user"})


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


@authroute.post("/update_password")
async def UpdatePasswordfun(Cred:LoginCred):
    result = await UpdatePassword(Cred)

    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})

    else:
        raise HTTPException(status_code=201,detail=result)


@authroute.put("/add_account_password")
async def AddAccountPassword(request:Request,Password:AccountPasswordCred):
    userid = request.headers.get('userid')
    
    result = await Add_Account_Password(userid,str(Password.password))

    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})
    
    else:
        raise HTTPException(status_code=201,detail={"userid":"","message":"Password Added"})

@authroute.put("/update_verify_status")
async def UpdateEmailStatus(request:Request):
    userid = request.headers.get('userid')
    
    result = await Update_Email_Status(userid=userid)

    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"userid":"","message":"Internal server error"})
    
    else:
        raise HTTPException(status_code=201,detail={"userid":"","message":"Status Updated"})

@authroute.delete("/accountdelete")
async def AccountDelete(userId:str):


    result = await DeleteUser(UserId=userId)
    if result == "Database Error":
        raise HTTPException(status_code=500,detail={"message":"Internal server error"})
    else:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED,detail={"message":result})

