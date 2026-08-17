import emails
from fastapi import APIRouter, BackgroundTasks,Request
from pydantic import BaseModel,EmailStr
from Config.dbConnection import engine,Logs
from sqlmodel import Session
from datetime import datetime


class EmailCred(BaseModel):
    email: EmailStr
    html: str
    subject: str
    type: str


def InsertToDB(EmailCred:EmailCred,clientip:str):
    Insert = Logs(emailTo=EmailCred.email,type=EmailCred.type,clientIp=clientip,createAt=datetime.now())

    with Session(engine) as session:
        session.add(Insert)
        session.commit()
        session.close()

    print("Inserted Into DB")


def EmailFunction(EmailCred:EmailCred,clientip:str,background_task:BackgroundTasks):
    try:
        message = emails.html(
            subject=EmailCred.subject,
            html=EmailCred.html,
            mail_from=("fastAPi","shubhamkarmarathe2@gmail.com")
        )
        response = message.send(
            to=EmailCred.email,
            smtp={
                "host": "smtp.gmail.com",
                "port": 587,
                "tls": True,
                "user": "shubhamkarmarathe2@gmail.com",
                "password":"zskm vqpo wbmp llgr"
            }
        )
        background_task.add_task(InsertToDB,EmailCred,clientip)
    except Exception as e:
        print(e) 


emailRouter = APIRouter()


@emailRouter.post("/api/email")
async def SendEmail(EmailCred:EmailCred,background_tasks: BackgroundTasks,Req:Request):
    background_tasks.add_task(EmailFunction,EmailCred,Req.client.host,background_tasks)
    return "The email will be sent shortly."