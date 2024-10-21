from fastapi import FastAPI
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


@app.get("/")
async def root():
    return {"message": "Hello World"}
