import json
from fastapi import APIRouter, BackgroundTasks,Request
from pydantic import BaseModel,EmailStr
from Config.redisConnection import redisConnect
from utils.EmailFunction import EmailFunction


class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str

emailRouter = APIRouter()


@emailRouter.post("/api/email")
async def SendEmail(EmailCred:EmailCred,Req:Request,background_tasks:BackgroundTasks):
    new_obj = {
        "email": EmailCred.model_dump(),
        "clientIp": Req.client.host
    }
    redisConnect.rpush("email",json.dumps(new_obj))
    background_tasks.add_task(EmailFunction)
    return "The email queued And will be sent shortly."
