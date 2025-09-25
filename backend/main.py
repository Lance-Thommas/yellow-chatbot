from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from routes import users, login, projects
from database import engine, Base


app = FastAPI()

origins = [
    "http://localhost:3000", # react port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(projects.router)


Base.metadata.create_all(bind=engine)

# TODO: check bcrypt.__about__ error later