from sqlmodel import create_engine,SQLModel,Field
import uuid


class BlackListTokens(SQLModel,table=True):
    id:uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    token:str




mysql_url = "mysql+pymysql://root:Abcd1234@127.0.0.1:3306/URLSHORTNER"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")




