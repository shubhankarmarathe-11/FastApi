from fastapi import APIRouter,Request,Depends,HTTPException
from Config.envconfig import Settings,get_settings
from Services.tokens import DecodeToken
import jwt
from starlette import status
from Services.Ratelimitter import UpdateRateLimmiter

async def Authenticatetoken(request: Request):
    env: Settings = get_settings()
    decoded_token = await DecodeToken(token=request.cookies["AccessToken"], env=env)
    if type(decoded_token) == jwt.exceptions.ExpiredSignatureError:
        print("Expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token Expired")

    elif type(decoded_token) == jwt.exceptions.InvalidTokenError:
        print("Invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

    ratelimit = await UpdateRateLimmiter(userid=decoded_token['userid'])
    if ratelimit == 'you are rate limited':
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Rate Limited")

router = APIRouter(
    prefix="/api/users",
    dependencies=[Depends(Authenticatetoken)],
)

@router.get("/me")
async def GetMyProfile():
    return {"user":"admin"}



