from fastapi import APIRouter, HTTPException
from config import database
import hashlib
import json

router = APIRouter()


@router.post("/users/signup", tags=["users"])
async def sign_up(form_data: dict):
    """Sign up a new user.
    Form data:
    - username: str
    - password: str
    - display_name: str
    - amount: int (optional)
    """
    try:
        username = form_data['username']
        password = form_data['password']
        hashed = hashlib.sha256(password.encode()).hexdigest()
        display_name = form_data['display_name']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    amount = form_data.get('amount', 0)
    print(display_name, type(display_name), amount)
    # print()
    query1 = f"INSERT INTO users (DisplayName, Username, Password, AddressID, Amount) VALUES " \
             f"('{display_name}', '{username}', '{hashed}', 1, {amount});"

    database.run_insert_query(query1)
    return {"message": "success"}


@router.post("/users/login", tags=["users"])
async def login(form_data: dict):
    """Login a user.
    Form data:
    - username: str
    - password: str
    """
    username = form_data['username']
    password = form_data['password']
    print(username, password)
    hashed = hashlib.sha256(password.encode()).hexdigest()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}';"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    curr_user = result[0]["UserID"]
    # return true
    return {"status": "success", "message": "Logged in successfully", "user_id": curr_user}


@router.get("/users/profile", tags=["users"])
async def get_user_profile(user_id: int):
    """Get user profile.
    Query parameters:
    - user_id: int
    """
    query = f"SELECT * FROM users WHERE UserID = {user_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="User not found")
    address_id = result[0]["AddressID"]
    query = f"SELECT * FROM addresses WHERE AddressID = {address_id};"
    result2 = database.run_select_query(query)
    result[0]["Address"] = result2[0]
    return result[0]


@router.post("/users/profile", tags=["users"])
async def update_user_profile(form_data: dict):
    """Update user profile. if user_id is not provided, Error will be raised.
    Form data:
    User_id: int
    - display_name: str (optional)
    - amount: int (optional)
    - Phone: str (optional)
    - Address: dict (optional) ||
    Address:
    - Building: str (optional)
    - Street: str (optional)
    - City: str (optional)
    - State: str (optional)
    """
    try:
        user_id = form_data['user_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    display_name = form_data.get('display_name', None)
    amount = form_data.get('amount', None)
    phone = form_data.get('phone', None)
    address = form_data.get('address', None)
    print(display_name, type(display_name), amount, type(amount), phone, type(phone), address, type(address))
    if display_name and amount and phone:
        query = f"UPDATE users SET DisplayName = '{display_name}', Amount = {amount}, Phone = '{phone}' WHERE UserID = {user_id};"
        database.run_update_query(query)
    elif display_name and amount:
        query = f"UPDATE users SET DisplayName = '{display_name}', Amount = {amount} WHERE UserID = {user_id};"
    elif display_name and phone:
        query = f"UPDATE users SET DisplayName = '{display_name}', Phone = '{phone}' WHERE UserID = {user_id};"
    elif amount and phone:
        query = f"UPDATE users SET Amount = {amount}, Phone = '{phone}' WHERE UserID = {user_id};"
    elif display_name:
        query = f"UPDATE users SET DisplayName = '{display_name}' WHERE UserID = {user_id};"
    elif amount:
        query = f"UPDATE users SET Amount = {amount} WHERE UserID = {user_id};"
    elif phone:
        query = f"UPDATE users SET Phone = '{phone}' WHERE UserID = {user_id};"
    if database.run_update_query(query):
        print("success")
    else:
        raise HTTPException(status_code=400, detail="Update failed")
    if address:
        query1 = f"INSERT INTO address (Building, Street, City, State) VALUES "
        query = f"UPDATE users SET AddressID = (SELECT AddressID FROM address WHERE Building = '{address.get('Building',None)}' AND Street = '{address.get('Street',None)}' AND City = '{address.get('City',None)}' AND State = '{address.get('State',None)}') WHERE UserID = {user_id};"



