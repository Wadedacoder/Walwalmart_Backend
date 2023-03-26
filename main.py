from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
import uvicorn
from database import Database
import hashlib
import json
from forms import AdditionalUserDataForm

# from config import settings

#
app = FastAPI()
database = Database()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
query_select = ("SELECT * FROM admins ; ")
query_select2 = ("SELECT * FROM users WHERE username = %s;")


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Authentication route for admin
@app.post("/admin/auth")
async def admin_auth(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    query = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{password}';"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    result = json.loads(result)
    curr_admin = result[0]["AdminID"]
    # print(curr_admin)
    # Generate token and store in database
    token = hashlib.sha256(str(curr_admin).encode()).hexdigest()
    # print(token)
    query2 = f"INSERT INTO admin_tokens (admin_id, token) VALUES ('{curr_admin}','{token}');"
    database.run_insert_query(query2)
    return {"access_token": token, "token_type": "bearer"}

    # Generate token and store in database


@app.get("/admin/auth/users")
async def admin_users(token: str = Depends(oauth2_scheme)):
    # Check if token is valid
    query = f"SELECT * FROM admin_tokens WHERE token = '{token}';"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Invalid token")
    # Get all users
    query2 = "SELECT * FROM users;"
    result2 = database.run_select_query(query2)
    return result2

@app.post("/users/signup")
async def sign_up(form_data: OAuth2PasswordRequestForm = Depends(),
                  additional_data: AdditionalUserDataForm = Depends()):
    username = form_data.username
    password = form_data.password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    display_name = additional_data.display_name
    Amount = additional_data.Amount
    query1 = f"INSERT INTO users (DisplayName, Username, Password, AddressID, Amount) VALUES (`{display_name}`, `{username}`, `{hashed}`, `{Amount});"
    database.run_insert_query(query1)
    return {"message": hashed}

@app.post("/users/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}';"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    result = json.loads(result)
    curr_user = result[0]["UserID"]
    # print(curr_user)
    # Generate token and store in database
    token = hashlib.sha256(str(curr_user).encode()).hexdigest()
    # print(token)
    query2 = f"INSERT INTO user_tokens (user_id, token) VALUES ('{curr_user}','{token}');"
    database.run_insert_query(query2)
    return {"access_token": token, "token_type": "bearer"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
