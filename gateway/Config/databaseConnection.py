from sqlmodel import create_engine,SQLModel,Field
import uuid
from Config.envconfig import Settings,get_settings


class BlackListTokens(SQLModel,table=True):
    id:uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    token:str



env:Settings = get_settings()

mysql_url = f"mysql+pymysql://{env.mysql_user}:{env.mysql_pass}@{env.mysql_host}/{env.mysql_db}"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")




