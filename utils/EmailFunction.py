import time
from Config.redisConnection import redisConnect
import json
import emails
from utils.Email_DB_Functions import InsertToDB


def EmailFunction():
    new_obj = json.loads(redisConnect.rpop("email"))
    EmailCred = new_obj["email"]
    time.sleep(3)
    message = emails.html(
        subject=EmailCred["subject"],
        html=EmailCred["html"],
        mail_from=("fastAPi","shubhamkarmarathe2@gmail.com")
    )
    try:
        response = message.send(
            to=EmailCred["email"],
            smtp={
                "host": "smtp.gmail.com",
                "port": 587,
                "tls": True,
                "user": "shubhamkarmarathe2@gmail.com",
                "password":"zskm vqpo wbmp llgr"
            }
        )

        if response.status_code == 250:
            InsertToDB(new_obj["email"],new_obj['clientIp'],False)
    except Exception as e:
        print(f"error - {e}")
        InsertToDB(new_obj["email"],new_obj['clientIp'],True)
