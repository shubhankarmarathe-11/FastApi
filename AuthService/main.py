from fastapi import FastAPI, Request, Depends
from Routes import authRoute
from Routes import emailRoute
from fastapi.middleware.cors import CORSMiddleware
from Config.dbConnection import engine
from sqlmodel import SQLModel

app = FastAPI()

app.add_middleware(CORSMiddleware,allow_origins="*",allow_methods=["GET","POST","PUT","DELETE"],allow_credentials=True,allow_headers="*")

SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(authRoute.authroute)
app.include_router(emailRoute.emailRouter)
