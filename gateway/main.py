from fastapi import FastAPI, HTTPException,Request
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel,EmailStr
from Routes import router,authroute,shortnerRouter
from sqlmodel import SQLModel
from Config.databaseConnection import engine
from Config.envconfig import Settings,get_settings
import secrets
import string
from Config.redisConnection import redisConnect
from Services.tokens import DecodeRefreshToken

class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str

class VerifyEmail(BaseModel):
    email: EmailStr
    otp: str

app = FastAPI()

SQLModel.metadata.create_all(engine)





async def OtpGenerator(length=6):
    digits = string.digits
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    return otp





app.add_middleware(CORSMiddleware,allow_origins="*",allow_methods=["GET","POST","PUT","DELETE"],allow_credentials=True,allow_headers="*")
@app.get("/")
def root():
    raise HTTPException(status_code=status.HTTP_200_OK,detail="Hello World")

@app.post("/api/email")
async def emailService(emailCred:EmailCred,request:Request):
    env:Settings = get_settings()

    is_user_logged_in = request.cookies.get("RefreshToken")
    print(is_user_logged_in)

    decode_refresh_token = ""

    if is_user_logged_in != None:
        decode_refresh_token = await DecodeRefreshToken(token=is_user_logged_in,env=env)

    print(emailCred.email)

    async with httpx.AsyncClient() as client:
        response = await client.post(url=f"{env.authurl}/is_user", json={"email": emailCred.email},headers={
            "x-internal-secret": env.internal_token 
        })
        print(response.json())
        if response.json()['detail']["message"] == "not user":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="not user")

        elif response.json()['detail']["message"] == "Internal server error":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error")

    print(decode_refresh_token)

    if(decode_refresh_token != "" and decode_refresh_token['userid']!=response.json()['detail']['userid']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please use logged in account email")

    otp = await OtpGenerator();
    edited_html = emailCred.html.replace("{{otp}}",str(otp))

    redisConnect.set(f"{emailCred.email}_otp",f"{otp}")
    redisConnect.expire(f"{emailCred.email}_otp",60)

    url = "http://192.168.5.32:8002/api/email"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"email": emailCred.email,"html":edited_html,"subject": emailCred.subject,"type": emailCred.type},headers={
            "x-internal-secret": env.internal_token 
        })
    return response.json()



@app.post("/api/email/verifyotp")
async def VerifyOtp(emailCred:VerifyEmail):

    is_Exist_otp = redisConnect.get(f"{emailCred.email}_otp")

    if is_Exist_otp == emailCred.otp.encode('utf-8'):
        raise HTTPException(status_code=status.HTTP_200_OK,detail="correct otp")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid otp")



    



app.include_router(router.router)
app.include_router(authroute.authrouter)
app.include_router(shortnerRouter.shortner)