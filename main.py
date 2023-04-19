from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from typing import Annotated
import uvicorn
import hashlib
import json
from forms import AdditionalUserDataForm, OlapForm
import os
from config import database
import users
import products
#

app = FastAPI()
app.include_router(products.router)
app.include_router(users.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
query_select = ("SELECT * FROM admins ; ")
query_select2 = ("SELECT * FROM users WHERE username = %s;")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

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

# @app.post("/users/signup")
# async def sign_up(form_data: OAuth2PasswordRequestForm = Depends(),
#                   additional_data: AdditionalUserDataForm = Depends()):
#     username = form_data.username
#     password = form_data.password
#     hashed = hashlib.sha256(password.encode()).hexdigest()
#     display_name = additional_data.name
#     Amount = additional_data.Amount
#     print(display_name, type(display_name) ,Amount)
#     # print()
#     query1 = f"INSERT INTO users (DisplayName, Username, Password, AddressID, Amount) VALUES " \
#              f"('{display_name}', '{username}', '{hashed}', 1, {Amount});"
#     # query2 = f"INSERT INTO users (DisplayName, Username, Password, AddressID, Amount) VALUES ('abr', 'abr', 'abr', 1, 0);"
#     database.run_insert_query(query1)
#     return {"message": hashed}
#
# @app.post("/users/login")
# async def login(form_data: dict):
#     username = form_data['username']
#     password = form_data['password']
#     print(username, password)
#     hashed = hashlib.sha256(password.encode()).hexdigest()
#     query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}';"
#     result = database.run_select_query(query)
#     if result == "[]":
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     result = json.loads(result)
#     curr_user = result[0]["UserID"]
#     # return true
#     return {"status": "success", "message": "Logged in successfully", "user_id": curr_user}

@app.post("/olap")
async def olap(additional_data: AdditionalUserDataForm = Depends()):
    queryn = additional_data.Amount
    if(queryn == 1):
        query = f"SELECT p.ProductName,p.ProductPrice,p.ProductQuantity,c.CategoryName, RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceRank, DENSE_RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceDenseRank, PERCENT_RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPricePercentRank, CUME_DIST() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceCumDist FROM products p JOIN categories c ON p.CategoryID = c.CategoryID ORDER BY c.CategoryName, CategoryPriceRank;"
    elif(queryn == 2):
        query = f"SELECT DATE_FORMAT(DATE_ADD(DeliveryDate, INTERVAL 7 DAY), '%Y-%m-%d') AS DeliveryDate_7_days_later, COUNT(*) AS Total_Checkouts FROM checkout WHERE DeliveryDate BETWEEN '2022-06-01' AND '2023-05-01' GROUP BY DeliveryDate_7_days_later ORDER BY DeliveryDate_7_days_later ASC;"
    elif(queryn == 3):
        query = f"SELECT c.CategoryName, SUM(p.ProductPrice * ic.Quantity) AS TotalRevenue FROM categories c JOIN products p ON c.CategoryID = p.CategoryID JOIN itemsincarts ic ON p.ProductID = ic.ProductID JOIN cart ct ON ic.CartID = ct.CartID JOIN checkout chk ON ct.CartID = chk.CartID GROUP BY c.CategoryID;"
    elif(queryn == 4):
        query = f"SELECT p.ProductName, SUM(ic.Quantity) AS TotalSold FROM products p JOIN itemsincarts ic ON p.ProductID = ic.ProductID GROUP BY p.ProductID ORDER BY TotalSold DESC LIMIT 10;"
    elif(queryn == 5):
        query = f"SELECT users.DisplayName AS CustomerName, SUM(p.ProductPrice * ic.Quantity) AS Revenue FROM users JOIN cart ON users.UserID = cart.UserID JOIN itemsincarts ic ON cart.CartID = ic.CartID JOIN products p ON ic.ProductID = p.ProductID GROUP BY users.UserID ORDER BY Revenue DESC LIMIT 5;"
    else:
        query = f"SELECT categories.CategoryName, SUM(itemsincarts.Quantity) AS Quantity FROM categories JOIN products ON categories.CategoryID = products.CategoryID JOIN itemsincarts ON products.ProductID = itemsincarts.ProductID GROUP BY categories.CategoryName WITH ROLLUP;"
    result = database.run_select_query(query)
    return result





if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORTtoc", default=5001), log_level="info")
