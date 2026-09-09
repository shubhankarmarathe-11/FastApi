from sqlmodel import Field,SQLModel, create_engine
import uuid

class EmailLogs(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    emailTo: str
    type: str
    clientIp: str | None = None
    in_retry: bool
    createAt: str

class UserDetails(SQLModel,table=True):
    id: uuid.UUID =Field(default_factory=uuid.uuid4,primary_key=True)
    username: str
    email: str = Field(unique=True)
    number: str
    password: str
    createdAt: str



# 


mysql_url = "mysql+pymysql://root:Abcd1234@127.0.0.1:3306/EMAIL"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")

