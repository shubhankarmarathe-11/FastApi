import json
from datetime import datetime,timedelta,timezone
from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel,EmailStr,Field
from Config.envconfig import Settings, get_settings
from Services.tokens import EncodeToken
from Routes import router
from Services.Ratelimitter import AddRateLimmiter

class LoginUser(BaseModel):
    username: str
    email: EmailStr
    number: PhoneNumber
    password: str = Field(min_length=8,max_length=16)

class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str

app = FastAPI()

app.add_middleware(CORSMiddleware,allow_origins="*",allow_methods=["GET","POST","PUT","DELETE"],allow_credentials=True,allow_headers="*")
@app.get("/")
def root():
    raise HTTPException(status_code=status.HTTP_200_OK,detail="Hello World")

@app.post("/api/email")
async def emailService(emailCred:EmailCred):
    url = "http://127.0.0.1:8001/api/email"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"email": emailCred.email,"html": emailCred.html,"subject": emailCred.subject,"type": emailCred.type})
    return response.json()


@app.post("/api/auth/{rest_of_path:path}")
async def authService(res:Response,rest_of_path: str,UserCred:LoginUser, env:Settings = Depends(get_settings)):
    url = f"http://127.0.0.1:8001/api/auth/{rest_of_path}"

    if rest_of_path == "login":
        async with httpx.AsyncClient() as client:
            response = await client.post(url,json={"email":UserCred.email,"password":UserCred.password})

        if(response.status_code == status.HTTP_200_OK):

            exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
            Data = dict(exp=int(exp_time.timestamp())+120,userid=response.json()['detail']['userid'],role="Admin")
            json.dumps(Data)
            token = await EncodeToken(Data=Data,env=env)
            res.set_cookie(key="AccessToken",value=str(token),httponly=True,expires=str(datetime.now() + timedelta(minutes=2)))
            AddRateLimmiter(response.json()['detail']['userid'])

        return response.json()['detail']['message']


    elif rest_of_path == "signup":
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"username":UserCred.username,"email": UserCred.email,"number": UserCred.number, "password": UserCred.password})
        return response.json()


app.include_router(router.router)