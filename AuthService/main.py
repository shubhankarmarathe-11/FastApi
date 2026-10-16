from fastapi import FastAPI, Request, Depends
from Routes import authRoute
from fastapi.middleware.cors import CORSMiddleware
from Config.dbConnection import engine
from sqlmodel import SQLModel

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=[],
    allow_methods=[],
    allow_credentials=False,
    allow_headers=[]
)


SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(authRoute.authroute)
