
from fastapi import FastAPI
from routes import users, login

from database import engine, Base


app = FastAPI()


app.include_router(users.router)
app.include_router(login.router)


Base.metadata.create_all(bind=engine)