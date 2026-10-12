from fastapi import APIRouter,Request,Depends,HTTPException,Response
from Config.envconfig import Settings,get_settings
from Services.tokens import DecodeToken,EncodeToken
import jwt
from starlette import status
from Services.Ratelimitter import UpdateRateLimmiter
from Config.databaseConnection import engine,BlackListTokens
from sqlmodel import Session
from Config.redisConnection import redisConnect
from fastapi.responses import RedirectResponse,JSONResponse
from datetime import timezone,timedelta,datetime
import json

userId = ""

async def Authenticatetoken(request: Request,response:Response):

    isRefreshTokenAvailable = request.cookies.get("RefreshToken")
    print("avail",isRefreshTokenAvailable)

    if isRefreshTokenAvailable == None:
        response.delete_cookie("AccessToken")
        response.delete_cookie("RefreshToken")

        res = RedirectResponse(url="/login")
        return res
    
    val = redisConnect.get(str(request.cookies.get("AccessToken")))
    print("val - ",val)
    if val == 'expired'.encode():
        pass



    elif val == None:

        with Session(engine) as session:
            result = session.query(BlackListTokens).filter(BlackListTokens.token == str(request.cookies.get("AccessToken"))).first()
            print("fetch-",result)
            if result != None:
                redisConnect.set(str(request.cookies.get("AccessToken")),'expired')
                pass
            session.close()

    env: Settings = get_settings()
    decoded_token = await DecodeToken(token= request.cookies.get("AccessToken"), env=env)
    if type(decoded_token) == jwt.exceptions.ExpiredSignatureError:
        print("Expired")
        Insert = BlackListTokens(token= request.cookies.get("AccessToken"))
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()

        refreshToken = request.cookies.get("RefreshToken")

        if refreshToken == None:
            # # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token Expired")
            # response.delete_cookie("AccessToken")
            # response.delete_cookie("RefreshToken")

            res = RedirectResponse(url="/login")
            return res

        decode_refresh_token = await DecodeToken(token=request.cookies.get("RefreshToken"), env=env)
        print(decode_refresh_token)

        exp_time = datetime.now(timezone.utc) + timedelta(seconds=120)
        
        accessData = dict(exp=int(exp_time.timestamp())+120,userid=decode_refresh_token['userid'],role="customer",type="access")
        json.dumps(accessData)


        accesstoken = await EncodeToken(Data=accessData,env=env)
        jsonResponse = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content="Token Recreated"
        )
        jsonResponse.set_cookie(key="AccessToken",value=str(accesstoken),httponly=True,expires=str(datetime.now() + timedelta(minutes=2)))
        return jsonResponse
        
    
    elif type(decoded_token) == jwt.exceptions.InvalidTokenError:
        print("Invalid")

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


router = APIRouter(
    prefix="/api/users",
    dependencies=[Depends(Authenticatetoken)],
)

@router.get("/me")
async def GetMyProfile():
    return {"user":"admin"}


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
    response.delete_cookie("AccessToken")
    response.delete_cookie("RefreshToken")

    res = RedirectResponse(url="/login")
    return res


