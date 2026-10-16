from fastapi import APIRouter,HTTPException,Depends
from starlette import status
from Routes.router import Authenticatetoken
import httpx
from Config.envconfig import get_settings,Settings
from pydantic import BaseModel
import json
from fastapi.responses import JSONResponse,RedirectResponse

userId = ""

class InsertLink(BaseModel):
    slug:str
    longlink:str 
    expiretime:str

shortner = APIRouter(
    prefix="/api/short"
)


@shortner.post("/link")
async def InsertLink(InsertCred:InsertLink,userId = Depends(Authenticatetoken)):
    env:Settings = get_settings()
    print(userId)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{env.shorturl}/link",json={"slug":InsertCred.slug,"longlink":InsertCred.longlink,"expiretime":InsertCred.expiretime,"userId":userId},headers={
            "x-internal-secret":env.internal_token
        })

        jsonResponse = JSONResponse(
            status_code=response.status_code,
            content=response.content.decode('utf-8')
        )
        return jsonResponse

@shortner.get("/link")
async def RetriveLink(userId = Depends(Authenticatetoken)):
    env:Settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{env.shorturl}/link/user/{userId}",headers={
            "x-internal-secret":env.internal_token
        })
        
        jsonResponse = JSONResponse(
            status_code=response.status_code,
            content=response.content.decode('utf-8')
        )
        return jsonResponse


@shortner.get("/link/{analytics_id}")
async def LinkAnalytics(analytics_id:str,userId = Depends(Authenticatetoken)):
    print(analytics_id)
    env:Settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{env.shorturl}/link/{analytics_id}",headers={
            "x-internal-secret":env.internal_token
        })
            
        jsonResponse = JSONResponse(
            status_code=response.status_code,
            content=response.content.decode('utf-8')
        )
        return jsonResponse

# @shortner.get("/{userid}/{slug}")
# async def RedirectLink(userid:str,slug:str):
#     env:Settings = get_settings()
#     async with httpx.AsyncClient() as client:
#         response = await client.get(f"{env.shorturl}/{userid}/{slug}")
#         return RedirectResponse(
#             url=response.content.decode('utf-8')
#         )
        

@shortner.delete("/link/{link_id}")
async def DeleteLink(link_id:str):
    env:Settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{env.shorturl}/link/{link_id}",headers={
            "x-internal-secret":env.internal_token
        })
        
        jsonResponse = JSONResponse(
            status_code=response.status_code,
            content=response.content.decode('utf-8')
        )
        return jsonResponse


