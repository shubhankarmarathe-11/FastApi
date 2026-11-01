from sqlmodel import Field,SQLModel, create_engine
import uuid




class ClientDetails(SQLModel,table=True):
    id: uuid.UUID =Field(default_factory=uuid.uuid4,primary_key=True)
    username: str
    email: str = Field(unique=True)
    password: str 
    role: str = Field(default="customer")
    sub: str = Field(default="")
    picture: str = Field(default="")
    createdAt: str
    emailVerified:bool = Field(default=False)

mysql_url = "mysql+pymysql://root:Abcd1234@127.0.0.1:3306/URLSHORTNER"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")

