import bcrypt
from pydantic import BaseModel,EmailStr,Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from Config.dbConnection import engine, ClientDetails
from sqlmodel import Session,select
from datetime import datetime
from bcrypt import gensalt
from uuid import UUID

class SignCred(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(default="",min_length=8,max_length=16)
    sub: str = Field(default="")
    picture: str = Field(default="")

class LoginCred(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=16)



class GoogleCred(BaseModel):
    username: str
    email: EmailStr
    sub: str = Field(default="")
    picture: str = Field(default="")


async def Is_Authenticated(userid:str):
    try:
        with Session(engine) as session:
            result = session.query(ClientDetails).filter(ClientDetails.id == UUID(userid)).first()
            if(result.emailVerified == 1 or result.emailVerified == True):
                return "verified"
            elif(result.emailVerified == 0 or result.emailVerified == False):
                return "not verified"
            session.close()


    except Exception as e:
        print(f"error - {e}")
        return "Database Error"


async def Is_Password_Added(userid:str):
    try:
        with Session(engine) as session:
            result = session.query(ClientDetails).filter(ClientDetails.id == UUID(userid)).first()
            if(result.password == ""):
                session.close()
                return "not added"
            else:
                session.close()
                return "added"


    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def Add_Account_Password(userid:str,password:str):
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes,gensalt())

    try:
        with Session(engine) as session:
            query = select(ClientDetails).where(ClientDetails.id == UUID(userid))
            execute_it = session.exec(query)
            result = execute_it.one()

            result.password = hashed_password

            session.add(result)
            session.commit()
            session.refresh(result)
        return "Password Added"

    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def Update_Email_Status(userid:str):

    try:
        with Session(engine) as session:
            query = select(ClientDetails).where(ClientDetails.id == UUID(userid))
            execute_it = session.exec(query)
            result = execute_it.one()

            result.emailVerified = True

            session.add(result)
            session.commit()
            session.refresh(result)
        return "Status Updated"

    except Exception as e:
        print(f"error - {e}")
        return "Database Error"


async def VerifyIsUser(email:str):
    try:
        with Session(engine) as session:
            query = select(ClientDetails).where(ClientDetails.email == email)

            execute_query = session.exec(query)

            result = execute_query.first()

            if(result == None):
                return {"userid":"","message":"User not found"}
            session.close()

        # return "User found"
        return {"userid":str(result.id),"message":"User found"}

    except Exception as e:
        print(f"error - {e}")
        return {"userid":"","message":"Database Error"}

async def InsertUser(User:SignCred):

    password_bytes = User.password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes,gensalt())
    Insert = ClientDetails(username=User.username,email=User.email,password=hashed_password,createdAt=datetime.now(),emailVerified=False)
    userid = str(Insert.id)
    try:
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()

        return {"userid":userid,"message":"Data Inserted"}
    except Exception as e:
        print(f"error - {e}")
        if "Duplicate entry" in str(e):
            return "Duplicate entry"
        else:
            return "Database Error"
        
async def InsertUserGoogle(User:GoogleCred):
    
    Insert = ClientDetails(username=User.username,email=User.email,password="",createdAt=datetime.now(),sub=User.sub,picture=User.picture,emailVerified=False)
    userid = str(Insert.id)
    try:
        with Session(engine) as session:
            session.add(Insert)
            session.commit()
            session.close()

        return {"userid":userid,"message":"Data Inserted"}
    except Exception as e:
        print(f"error - {e}")
        if "Duplicate entry" in str(e):
            return "Duplicate entry"
        else:
            return "Database Error"


async def GetUserDetailsGoogle(User:GoogleCred):
    try:
        with Session(engine) as session:
            result = session.query(ClientDetails).filter(ClientDetails.email == User.email).first()
            if(result == None):
                return "User not found"

            if (result.sub == ''):
                result.sub = User.sub
                result.picture = User.picture

                session.add(result)
                session.commit()
                session.refresh(result)
            
            if(result.sub != User.sub):
                return "Incorrect token id"
        return {"userid":str(result.id),"message":"Correct Credentials"}
    except Exception as e:
        print(f"error - {e}")
        return "Database Error"


async def GetUserDetails(User:LoginCred):
    try:
        with Session(engine) as session:
            result = session.query(ClientDetails).filter(ClientDetails.email == User.email).first()
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
            statement = select(ClientDetails).where(ClientDetails.email == User.email)
            result = session.exec(statement)
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

async def UpdatePassword(User:LoginCred):
    try:
        password_bytes = User.password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, gensalt())

        with Session(engine) as session:
            statement = select(ClientDetails).where(ClientDetails.email == User.email)
            result = session.exec(statement)
            got_one = result.one()
            got_one.password = hashed_password
            got_one.emailVerified=True

            session.add(got_one)
            session.commit()
            session.refresh(got_one)

        return "Password Updated"

    except Exception as e:
        print(f"error - {e}")
        return "Database Error"

async def DeleteUser(UserId:str):
    try:
        with Session(engine) as session:
            statement = select(ClientDetails).where(ClientDetails.id == UUID(UserId))
            result = session.exec(statement)
            got_one = result.one_or_none()
            session.delete(got_one)
            session.commit()
        return "Account Removed"
    except Exception as e:
        print(f"error - {e}")
        return "Database Error"
    

    