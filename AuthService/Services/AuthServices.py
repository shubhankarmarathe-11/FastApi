import bcrypt
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Config.dbConnection import engine, empDetails
from sqlmodel import Session,select
from datetime import datetime
from bcrypt import gensalt

class SignCred(BaseModel):
    username: str
    email: EmailStr
    number: PhoneNumber
    password: str = Field(min_length=8,max_length=16)
    startingDate: datetime = Field(default=datetime.now())
    payrollDate: datetime = Field(default=datetime.now())

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)

async def InsertUser(User:SignCred):

    password_bytes = User.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes,gensalt())
    Insert = empDetails(name=User.username,email=User.email,password=hashed_password,createdAt=datetime.now(),number=User.number,startingDate=User.startingDate,payrollDate=User.payrollDate)

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
            result = session.query(empDetails).filter(empDetails.email == User.email).first()
            if(result == None):
                return "User not found"
            password_bytes = User.password.encode('utf-8')
            actual_password = result.password.encode('utf-8')
            is_correct = bcrypt.checkpw(password_bytes, actual_password)
            if(is_correct==False):
                return "Incorrect Password"
        return {"userid":str(result.id),"message":"Correct Credentials"}
    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def UpdateUser(User:SignCred):
    try:
        password_bytes = User.password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, gensalt())

        with Session(engine) as session:
            statement = select(empDetails).where(empDetails.email == User.email)
            result = session.execute(statement)
            got_one = result.one()

            got_one.username = User.username
            got_one.password = hashed_password
            got_one.number = User.number

            session.add(got_one)
            session.commit()
            session.refresh(got_one)

    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def DeleteUser(UserId:str):
    try:
        with Session(engine) as session:
            statement = select(empDetails).where(str(empDetails.id) == UserId)
            result = session.execute(statement)
            got_one = result.one()
            session.delete(got_one)
            session.commit()
    except Exception as e:
        print(f"error - {e}")
        return "Database Error"