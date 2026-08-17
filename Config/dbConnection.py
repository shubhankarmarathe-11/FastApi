from sqlmodel import Field,SQLModel, create_engine


class Logs(SQLModel, table=True):
    id: int | None = Field(default=None,primary_key=True)
    emailTo: str
    type: str
    clientIp: str | None = None
    createAt: str


mysql_url = "mysql+pymysql://root:Abcd1234@127.0.0.1:3306/EMAIL"
engine = create_engine(mysql_url)


with engine.connect() as connection:
    print("Connection successful")

