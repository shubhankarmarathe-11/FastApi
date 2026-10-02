from sqlmodel import Field,SQLModel, create_engine
import uuid

class EmailLogs(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    emailTo: str
    type: str
    clientIp: str | None = None
    in_retry: bool
    createAt: str

class ClientDetails(SQLModel,table=True):
    id: uuid.UUID =Field(default_factory=uuid.uuid4,primary_key=True)
    name: str
    email: str = Field(unique=True)
    number: str
    password: str
    address: str
    role: str = Field(default="client")
    createdAt: str



class empDetails(SQLModel,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(unique=True)
    number: str = Field(unique=True)
    password: str = Field(min_length=8,max_length=12,nullable=False)
    role: str = Field(default='emp',nullable=False)
    address: str
    startingDate: str
    payrollDate: str
    createdAt: str

class adminDetails(SQLModel,table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(unique=True)
    number: str = Field(unique=True)
    password: str = Field(min_length=8,max_length=12,nullable=False)
    role: str = Field(default='admin',nullable=False)



mysql_url = "mysql+pymysql://root:Abcd1234@127.0.0.1:3306/LIBRARY_SYSTEM"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")

