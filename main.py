from fastapi import FastAPI
import uvicorn
import os
import json
from database import Database
# from config import settings

#
app = FastAPI()
database = Database()
query_select = ("SELECT * FROM admins ; ")
query_select2 = ("SELECT * FROM users WHERE username = %s;")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/admins")
async def say_hello():
    result = database.run_select_query(query_select)
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
