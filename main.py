from fastapi import FastAPI
import uvicorn
import os
# from config import settings
import mysql.connector
import json
#
app = FastAPI()
# cnx = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='dev21038',
#     database='Walwalmart',
#     )
# cursor = cnx.cursor(dictionary=True)
# query_select = ("SELECT * FROM admins")
# query_select2 = ("SELECT * FROM users WHERE username = %s")

@app.get("/")
async def root():
    # cursor.execute(query_select)
    # tmp = cursor.fetchall()
    # tmp = json.dumps(tmp)
    # print(tmp)
    # sh = json.loads(tmp)
    # print(sh)
    return "hi"


# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     cursor.execute(query_select2, (name,))
#     tmp = cursor.fetchall()
#     tmp = json.dumps(tmp)
#     # return {"message": f"Hello {name}"}
#     return tmp

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=5000), log_level="info")

