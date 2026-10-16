from fastapi import FastAPI, HTTPException
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel,EmailStr
from Routes import router,authroute,shortnerRouter
from sqlmodel import SQLModel
from Config.databaseConnection import engine



class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str

app = FastAPI()

SQLModel.metadata.create_all(engine)

app.add_middleware(CORSMiddleware,allow_origins="*",allow_methods=["GET","POST","PUT","DELETE"],allow_credentials=True,allow_headers="*")
@app.get("/")
def root():
    raise HTTPException(status_code=status.HTTP_200_OK,detail="Hello World")

@app.post("/api/email")
async def emailService(emailCred:EmailCred):
    url = "http://192.168.5.32:8002/api/email"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"email": emailCred.email,"html": emailCred.html,"subject": emailCred.subject,"type": emailCred.type})
    return response.json()




app.include_router(router.router)
app.include_router(authroute.authrouter)
app.include_router(shortnerRouter.shortner)