from sqlmodel import Field,SQLModel, create_engine
import uuid
from Config.envConfig import Settings,get_settings




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

env:Settings = get_settings()

mysql_url = f"mysql+pymysql://{env.mysql_user}:{env.mysql_pass}@{env.mysql_host}/{env.mysql_db}"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")

