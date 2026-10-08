import jwt
from fastapi import Depends
from pydantic import BaseModel
from Config.envconfig import Settings


class TokenData(BaseModel):
    exp: int
    userid: str
    role: str


async def EncodeToken(Data:TokenData,env:Settings):
    try:
        encoded_jwt = jwt.encode(Data,env.secret_key,algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        print("error this- ",e)
        return "Error"


async def DecodeToken(token:str,env:Settings):
    print(token)
    try:
        decoded_jwt = jwt.decode(token,env.secret_key,algorithms=["HS256"])
        return decoded_jwt
    except Exception as e:
        return e


