
from fastapi import FastAPI
from routes import users, login

from database import engine, Base
import models.user as user_models  # Ensure models are imported for ORM mapping



app = FastAPI()


app.include_router(users.router)
app.include_router(login.router)


Base.metadata.create_all(bind=engine)