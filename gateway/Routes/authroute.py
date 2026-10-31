from fastapi import APIRouter,Depends,Response,Request,HTTPException
from fastapi.responses import JSONResponse
from Config.envconfig import get_settings,Settings
from pydantic import BaseModel,Field,EmailStr
import httpx
from datetime import datetime,timezone,timedelta
import json
from Services.Ratelimitter import AddRateLimmiter
from Services.tokens import EncodeToken
from starlette import status
from google.oauth2 import id_token
from google.auth.transport import requests



class UserCred(BaseModel):
    username: str = Field(default="")
    email: EmailStr
    password: str = Field(default="",min_length=8,max_length=16)
    sub: str = Field(default="")
    picture: str = Field(default="")


class GoogleLogin(BaseModel):
    google_token: str

authrouter = APIRouter(
    prefix="/api/auth"
)



@authrouter.post("/login")
async def LoginRoute(res:Response,userCred:UserCred,env:Settings = Depends(get_settings)):


    url = env.authurl
    print(url)

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{url}/login",json={"email":userCred.email,"password":userCred.password},headers={
            "x-internal-secret":env.internal_token
        })
    
        if(response.status_code == status.HTTP_200_OK):

            exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
            exp_time2 = datetime.now(timezone.utc) + timedelta(seconds=30000)

            accessData = dict(exp=int(exp_time.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="access")
            refreshData = dict(exp=int(exp_time2.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="refresh")

            json.dumps(accessData)
            json.dumps(refreshData)

            accesstoken = await EncodeToken(Data=accessData,env=env)
            refreshtoken = await EncodeToken(Data=refreshData,env=env)

            jsonResponse = JSONResponse(
                status_code=response.status_code,
                content=response.json()['detail']['message']
            )

            jsonResponse.delete_cookie(key='RefreshToken',path="/")
            jsonResponse.delete_cookie(key='AccessToken',path="/")

            # Access Token Set
            jsonResponse.set_cookie(
                key="AccessToken",
                value=str(accesstoken),
                httponly=True,
                secure= False if env.environment == "development" else True,
                samesite="lax" if env.environment == "development" else "lax",
                partitioned=False,
                expires=str(datetime.now() + timedelta(minutes=20))
            )

            # Refresh Token Set
            jsonResponse.set_cookie(
                key="RefreshToken",
                value=str(refreshtoken),
                httponly=True,
                secure= False if env.environment == "development" else True,
                samesite="lax" if env.environment == "development" else "lax",
                partitioned=False,
                expires=str(datetime.now() + timedelta(minutes=500))
            )

            AddRateLimmiter(response.json()['detail']['userid'])

            return jsonResponse
        
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message'] if response.json()['detail']['message'] else response.json()
        )
        

@authrouter.post("/signup")
async def SignupRoute(res:Response,userCred:UserCred,env:Settings = Depends(get_settings)):
    url = env.authurl
    print(UserCred)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{url}/signup",json={"username":userCred.username,"email": userCred.email, "password": userCred.password, "sub": userCred.sub,"picture": userCred.picture},headers={
            "x-internal-secret":env.internal_token
        })
        
        if(response.status_code == status.HTTP_201_CREATED):
            exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
            exp_time2 = datetime.now(timezone.utc) + timedelta(seconds=30000)

            accessData = dict(exp=int(exp_time.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="access")
            refreshData = dict(exp=int(exp_time2.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="refresh")

            json.dumps(accessData)
            json.dumps(refreshData)

            accesstoken = await EncodeToken(Data=accessData,env=env)
            refreshtoken = await EncodeToken(Data=refreshData,env=env)

            jsonResponse = JSONResponse(
                status_code=response.status_code,
                content=response.json()['detail']['message']
            )

            jsonResponse.delete_cookie(key='RefreshToken',path="/")
            jsonResponse.delete_cookie(key='AccessToken',path="/")

            # Access Token Set
            jsonResponse.set_cookie(
                key="AccessToken",
                value=str(accesstoken),
                httponly=True,
                secure= False if env.environment == "development" else True,
                samesite="lax" if env.environment == "development" else "lax",
                partitioned=False,
                expires=str(datetime.now() + timedelta(minutes=20))
            )

            # Refresh Token Set
            jsonResponse.set_cookie(
                key="RefreshToken",
                value=str(refreshtoken),
                httponly=True,
                secure= False if env.environment == "development" else True,
                samesite="lax" if env.environment == "development" else "lax",
                partitioned=False,
                expires=str(datetime.now() + timedelta(minutes=500))
            )

            AddRateLimmiter(response.json()['detail']['userid'])
            
            return jsonResponse
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message'] if response.json()['detail']['message'] else response.json()
        )



@authrouter.post("/update_password")
async def UpdatePasswordFun(userCred:UserCred,env:Settings = Depends(get_settings)):
    url = env.authurl
    print(UserCred)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{url}/update_password",json={"email": userCred.email, "password": userCred.password},headers={
            "x-internal-secret":env.internal_token
        })

    return JSONResponse(
        status_code=response.status_code,
        content=response.json()['detail'] if response.json()['detail'] else response.json()
    )
    

@authrouter.post("/login/google")
async def GoogleAuth(Cred:GoogleLogin,env:Settings = Depends(get_settings)):
    GOOGLE_CLIENT_ID = env.google_client_id
    url = env.authurl

    try:
        transport_request = requests.Request()

        user_info = id_token.verify_oauth2_token(
            Cred.google_token,
            transport_request,
            GOOGLE_CLIENT_ID
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/login/google",json={"username":user_info['name'],"email": user_info['email'], "sub": user_info['sub'],"picture": user_info['picture']},headers={
                "x-internal-secret":env.internal_token
            })
            if(response.status_code == status.HTTP_200_OK):
    
                exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
                exp_time2 = datetime.now(timezone.utc) + timedelta(seconds=30000)
    
                accessData = dict(exp=int(exp_time.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="access")
                refreshData = dict(exp=int(exp_time2.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="refresh")
    
                json.dumps(accessData)
                json.dumps(refreshData)
    
                accesstoken = await EncodeToken(Data=accessData,env=env)
                refreshtoken = await EncodeToken(Data=refreshData,env=env)
    
                jsonResponse = JSONResponse(
                    status_code=response.status_code,
                    content=response.json()['detail']['message']
                )
    
                jsonResponse.delete_cookie(key='RefreshToken',path="/")
                jsonResponse.delete_cookie(key='AccessToken',path="/")
    
                # Access Token Set
                jsonResponse.set_cookie(
                    key="AccessToken",
                    value=str(accesstoken),
                    httponly=True,
                    secure= False if env.environment == "development" else True,
                    samesite="lax" if env.environment == "development" else "lax",
                    partitioned=False,
                    expires=str(datetime.now() + timedelta(minutes=20))
                )
    
                # Refresh Token Set
                jsonResponse.set_cookie(
                    key="RefreshToken",
                    value=str(refreshtoken),
                    httponly=True,
                    secure= False if env.environment == "development" else True,
                    samesite="lax" if env.environment == "development" else "lax",
                    partitioned=False,
                    expires=str(datetime.now() + timedelta(minutes=500))
                )
    
                AddRateLimmiter(response.json()['detail']['userid'])
    
                return jsonResponse
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()['detail']['message'] if response.json()['detail']['message'] else response.json()
            )

    except Exception as e:
        print(f"Invalid token: {e}")
        return None



@authrouter.post("/signup/google")
async def GoogleAuth(Cred:GoogleLogin,response:Response,request:Request,env:Settings = Depends(get_settings)):
    GOOGLE_CLIENT_ID = env.google_client_id
    url = env.authurl

    try:
        transport_request = requests.Request()

        user_info = id_token.verify_oauth2_token(
            Cred.google_token,
            transport_request,
            GOOGLE_CLIENT_ID
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/signup/google",json={"username":user_info['name'],"email": user_info['email'], "sub": user_info['sub'],"picture": user_info['picture']},headers={
                "x-internal-secret":env.internal_token
            })

            if(response.status_code == status.HTTP_201_CREATED):
                exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
                exp_time2 = datetime.now(timezone.utc) + timedelta(seconds=30000)

                accessData = dict(exp=int(exp_time.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="access")
                refreshData = dict(exp=int(exp_time2.timestamp()),userid=response.json()['detail']['userid'],role="customer",type="refresh")

                json.dumps(accessData)
                json.dumps(refreshData)

                accesstoken = await EncodeToken(Data=accessData,env=env)
                refreshtoken = await EncodeToken(Data=refreshData,env=env)

                jsonResponse = JSONResponse(
                    status_code=response.status_code,
                    content=response.json()['detail']['message']
                )

                jsonResponse.delete_cookie(key='RefreshToken',path="/")
                jsonResponse.delete_cookie(key='AccessToken',path="/")

                # Access Token Set
                jsonResponse.set_cookie(
                    key="AccessToken",
                    value=str(accesstoken),
                    httponly=True,
                    secure= False if env.environment == "development" else True,
                    samesite="lax" if env.environment == "development" else "lax",
                    partitioned=False,
                    expires=str(datetime.now() + timedelta(minutes=20))
                )

                # Refresh Token Set
                jsonResponse.set_cookie(
                    key="RefreshToken",
                    value=str(refreshtoken),
                    httponly=True,
                    secure= False if env.environment == "development" else True,
                    samesite="lax" if env.environment == "development" else "lax",
                    partitioned=False,
                    expires=str(datetime.now() + timedelta(minutes=500))
                )

                AddRateLimmiter(response.json()['detail']['userid'])
                
                return jsonResponse
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()['detail']['message'] if response.json()['detail']['message'] else response.json()
            )






    except Exception as e:
        print(f"Invalid token: {e}")
        return None



    
