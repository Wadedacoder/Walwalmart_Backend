from fastapi import FastAPI
import mysql.connector
import json

app = FastAPI()
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='dev21038',
    database='a',
    )
cursor = cnx.cursor(dictionary=True)
query_select = ("SELECT * FROM persons")
query_select2 = ("SELECT * FROM persons WHERE name = %s")

@app.get("/")
async def root():
    cursor.execute(query_select)
    tmp = cursor.fetchall()
    tmp = json.dumps(tmp)
    # print(tmp)
    sh = json.loads(tmp)
    print(sh)
    return tmp


@app.get("/hello/{name}")
async def say_hello(name: str):
    cursor.execute(query_select2, (name,))
    tmp = cursor.fetchall()
    tmp = json.dumps(tmp)
    # return {"message": f"Hello {name}"}
    return tmp