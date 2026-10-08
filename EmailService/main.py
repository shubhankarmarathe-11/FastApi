from fastapi import FastAPI,HTTPException, BackgroundTasks,Request
from starlette import status
import json
from pydantic import BaseModel,EmailStr
from Config.redisConnection import redisConnect
from utils.EmailFunction import EmailFunction


class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str


app = FastAPI()



@app.get("/")
def mainRoute():
    raise HTTPException(status_code=status.HTTP_200_OK,detail="Working Email service")




@app.post("/api/email")
async def SendEmail(EmailCred:EmailCred,Req:Request,background_tasks:BackgroundTasks):
    new_obj = {
        "email": EmailCred.model_dump(),
        "clientIp": Req.client.host
    }
    redisConnect.rpush("email",json.dumps(new_obj))
    background_tasks.add_task(EmailFunction)
    return "The email queued And will be sent shortly."
