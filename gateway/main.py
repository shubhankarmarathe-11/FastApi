from fastapi import FastAPI, HTTPException
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
async def emailService(emailCred:EmailCred):
    env:Settings = get_settings()

    print(emailCred.email)

    async with httpx.AsyncClient() as client:
        response = await client.post(url=f"{env.authurl}/is_user", json={"email": emailCred.email},headers={
            "x-internal-secret": env.internal_token 
        })
        print(response.json())
        if response.json()['detail']["message"] == "not user":
            return response.json()

        elif response.json()['detail']["message"] == "Internal server error":
            return response.json()

    

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