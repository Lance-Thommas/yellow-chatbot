from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from routes import users, login, projects, prompts, files
from database import engine, Base

from logger import init_sentry
init_sentry()

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
app.include_router(prompts.router)
app.include_router(files.router, prefix="/api")


Base.metadata.create_all(bind=engine)

# TODO: check bcrypt.__about__ error later