from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Config.dbConnection import engine, UserDetails
from sqlmodel import Session
from datetime import datetime

class SignCred(BaseModel):
    username: str
    email: EmailStr
    number: PhoneNumber
    password: str = Field(min_length=8,max_length=16)

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)

async def InsertUser(User:SignCred):

    Insert = UserDetails(username=User.username,email=User.email,password=User.password,createdAt=datetime.now(),number=User.number)

    try:
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()
        return "Data Inserted"
    except Exception as e:
        print(f"error - {e}")
        if "Duplicate entry" in str(e):
            return "Duplicate entry"


async def GetUserDetails(User:LoginCred):
    try:
        with Session(engine) as session:
            result = session.query(UserDetails).filter(UserDetails.email == User.email).first()
            if(result == None):
                return "User not found"
            if(result.password != User.password):
                return "Incorrect Password"
        return "Correct Credentials"
    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def UpdateUser(User:SignCred):
    pass