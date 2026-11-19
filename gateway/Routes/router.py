from fastapi import APIRouter,Request,Depends,HTTPException,Response
from Config.envconfig import Settings,get_settings
from Services.tokens import DecodeToken,EncodeToken,DecodeRefreshToken
import jwt
from starlette import status
from Services.Ratelimitter import UpdateRateLimmiter
from Config.databaseConnection import engine,BlackListTokens
from sqlmodel import Session
from Config.redisConnection import redisConnect
from fastapi.responses import RedirectResponse,JSONResponse
from datetime import timezone,timedelta,datetime
import json
import httpx
from pydantic import BaseModel,Field,EmailStr
from bullmq import Queue

userId = ""


async def Authenticatetoken(request: Request,response:Response):

    isRefreshTokenAvailable = request.cookies.get("RefreshToken")

    if isRefreshTokenAvailable is None:

        response.delete_cookie(
            key="AccessToken",
            path="/"
        )
        response.delete_cookie(
            key="RefreshToken",
            path="/"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                **dict(response.headers),
            },
            detail="Unauthorized access"
        )


    env: Settings = get_settings()
    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)

    if decode_refresh_token == 'DecodeError':

        response.delete_cookie(
            key="AccessToken",
            path="/"
        )
        response.delete_cookie(
            key="RefreshToken",
            path="/"
        )
        
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                **dict(response.headers),
            },
            detail="Unauthorized access"
        )

    # find accesstoken in redis
    
    val = redisConnect.get(str(request.cookies.get("AccessToken")))

    if val is None:

        with Session(engine) as session:
            result = session.query(BlackListTokens).filter(BlackListTokens.token == str(request.cookies.get("AccessToken"))).first()
            if result != None:
                redisConnect.set(str(request.cookies.get("AccessToken")),'expired')
                pass
            session.close()

    if val == "expired".encode('utf-8'):
        pass

    # decode accesstoken 
    
    decoded_token = await DecodeToken(token= request.cookies.get("AccessToken"), env=env)

    if type(decoded_token) == jwt.exceptions.ExpiredSignatureError:
        Insert = BlackListTokens(token= request.cookies.get("AccessToken"))
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()



        decode_refresh_token = await DecodeToken(token=request.cookies.get("RefreshToken"), env=env)
        exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
        
        accessData = dict(exp=int(exp_time.timestamp())+120,userid=decode_refresh_token['userid'],role="customer",type="access")
        json.dumps(accessData)


        accesstoken = await EncodeToken(Data=accessData,env=env)
        
        response.set_cookie(
            key="AccessToken",
            value=str(accesstoken),
            httponly=True,
            secure= False if env.environment == "development" else True,
            samesite="lax" if env.environment == "development" else "lax",
            partitioned=False,
            expires=str(datetime.now() + timedelta(minutes=20))
        )

        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            headers={
                **dict(response.headers),
            }
        )   
        
    
    elif type(decoded_token) == jwt.exceptions.InvalidTokenError:

        Insert = BlackListTokens(token=request.cookies["AccessToken"])
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()

        redisConnect.set(str(request.cookies["AccessToken"]),'expired')

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

    ratelimit = await UpdateRateLimmiter(userid=decoded_token['userid'])
    if ratelimit == 'you are rate limited':
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Rate Limited")

    userId = decoded_token['userid']
    return userId



delete_account_data_queue = Queue("delete_account_data")



router = APIRouter(
    prefix="/api/users",
    dependencies=[Depends(Authenticatetoken)],
)

class AccountPasswordCred(BaseModel):
    password:str = Field(default="",min_length=8,max_length=16)

class Verify_OTP(BaseModel):
    otp:str = Field(min_length=6,max_length=6)
    email:EmailStr


@router.get("/is_authenticated")
async def IsAuthenticated(request:Request):
    env:Settings = get_settings()
    
    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)

    async with httpx.AsyncClient() as client:
        response = await client.get(url=f"{env.authurl}/is_authenticated",headers={
            "x-internal-secret":env.internal_token,
            "userid":str(decode_refresh_token['userid'])
        })



        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message']
        )

@router.get("/is_password_added")
async def IsPasswordAdded(request:Request):
    env:Settings = get_settings()
    
    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)

    async with httpx.AsyncClient() as client:
        response = await client.get(url=f"{env.authurl}/is_password_added",headers={
            "x-internal-secret":env.internal_token,
            "userid":str(decode_refresh_token['userid'])
        })
        print(response.json())
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message']
        )



@router.post("/authenticate_email")
async def Authenticate_OTP_To_Verify_Email(request:Request,VerifyCred:Verify_OTP):

    env:Settings = get_settings()
        
    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)

    Get_otp = redisConnect.get(f"{VerifyCred.email}_otp")
    print(Get_otp)
    if (Get_otp == None):
        raise HTTPException(status_code=401,detail="Otp Expired")

    if(Get_otp.decode('utf-8') != VerifyCred.otp):
        raise HTTPException(status_code=401,detail="Invalid Otp")

    
    async with httpx.AsyncClient() as client:
        response = await client.put(url=f"{env.authurl}/update_verify_status",headers={
            "x-internal-secret":env.internal_token,
            "userid":str(decode_refresh_token['userid'])
        })

        print(response)

        if (response.status_code == 500):
            raise HTTPException(status_code=500,detail="Internal server error")

        res = JSONResponse(
            status_code=200,
            content="correct otp"
        )

    return res



@router.post("/logout")
async def LogoutRoute(request:Request,response:Response):


    accesstoken = request.cookies["AccessToken"]
    refreshtoken = request.cookies["RefreshToken"]
    Insertfirst = BlackListTokens(token=accesstoken)
    Insertsecond = BlackListTokens(token=refreshtoken)
    with Session(engine) as session:
        session.add_all([Insertfirst,Insertsecond])
        session.commit()
        session.close()

    redisConnect.set(str(request.cookies["AccessToken"]),'expired')
    res = JSONResponse(
        status_code=200,
        content="logout successful"
    )
    res.delete_cookie("AccessToken")
    res.delete_cookie("RefreshToken")
    
    return res  


@router.put("/add_account_password")
async def Add_Account_Password(request:Request,Password:AccountPasswordCred):
    env:Settings = get_settings()

    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)
    print("delete -",decode_refresh_token['userid'])

    async with httpx.AsyncClient() as client:
        response = await client.put(url=f"{env.authurl}/add_account_password",json={"password":str(Password.password)},headers={
            "x-internal-secret":env.internal_token,
            "userid":decode_refresh_token['userid']
        })

        print(response.json())

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message']
        )



@router.delete("/accountdelete")
async def AccountDelete(request:Request):

    
    env:Settings = get_settings()

    decode_refresh_token = await DecodeRefreshToken(token=request.cookies.get("RefreshToken"), env=env)
    print("delete -",decode_refresh_token['userid'])

    async with httpx.AsyncClient() as client:
        response = await client.delete(url=f"{env.authurl}/accountdelete",params={"userId":decode_refresh_token['userid']},headers={
            "x-internal-secret":env.internal_token
        })

        if response.status_code == status.HTTP_202_ACCEPTED:

            # publishRecord = redisConnect.publish("deleteRecord",str(decode_refresh_token['userid']))
            # print("Subscribers receiving message:", publishRecord)

            job = await delete_account_data_queue.add(
                        "emails",
                        {
                            "userId": str(decode_refresh_token['userid']),
                        },
                        {
                            "attempts": 3,
                            "backoff": {
                                "type": "exponential",
                                "delay": 2000
                            },
                            "removeOnComplete": True,
                            "removeOnFail":False
                        }
                    )

            accesstoken = request.cookies["AccessToken"]
            refreshtoken = request.cookies["RefreshToken"]
            Insertfirst = BlackListTokens(token=accesstoken)
            Insertsecond = BlackListTokens(token=refreshtoken)
            with Session(engine) as session:
                session.add_all([Insertfirst,Insertsecond])
                session.commit()
                session.close()
            
            redisConnect.set(str(request.cookies["AccessToken"]),'expired')
            res = JSONResponse(
                status_code=202,
                content="Account Removed"
            )
            res.delete_cookie("AccessToken")
            res.delete_cookie("RefreshToken")

            return res
        print(response)
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()['detail']['message']
        )