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
import supplier
# import torch
#

app = FastAPI()
app.include_router(products.router)
app.include_router(users.router)
app.include_router(supplier.router)

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
@app.post("/admin/auth", tags = ["admin"])
async def admin_auth(dict_data: dict):
    """Returns a token for the admin
    Form data:
    - username: str
    - password: str
    Test:
    {
        "username": "admin",
        "password": "admin"
    }
    """
    try:
        username = dict_data["username"]
        password = dict_data["password"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    hashed = hashlib.sha256(password.encode()).hexdigest()
    query = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{hashed}';"
    result = database.run_select_query(query)
    if result == "[]" or len(result) < 1:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # result = json.loads(result)
    curr_admin = result[0]["AdminID"]
    return {"token": curr_admin}

# @app.get("/admin/requests", tags = ["admin"])
# async def admin_users(token: str = Depends(oauth2_scheme)):
#     # Check if token is valid
#     query = f"SELECT * FROM admin_tokens WHERE token = '{token}';"
#     result = database.run_select_query(query)
#     if result == "[]":
#         raise HTTPException(status_code=400, detail="Invalid token")
#     # Get all users
#     query2 = "SELECT * FROM users;"
#     result2 = database.run_select_query(query2)
#     return result2

@app.get("/admin/requests", tags = ["admin"])
async def admin_users():
    """Returns all the suppliedproducts data
    """
    query = "SELECT * FROM suppliedproducts;"
    result = database.run_select_query(query)
    return result

@app.get("/admin/requests/{status}", tags = ["admin"])
async def admin_users(status: str):
    """Returns all the suppliedproducts data
    status: str
    example: status = "Pending"
    """
    query = f"SELECT * FROM suppliedproducts WHERE Status = '{status}';"
    result = database.run_select_query(query)
    return result

# @app.get("/admin/requests/", tags = ["admin"])
# async def admin_users(dict_data: dict):
#     """Returns all the suppliedproducts data
#     status: str
#     example: status = "Accepted"
#     Supplierid: int
#     Productid: int
#
#     testcase:
#     {
#         "status": "Accepted",
#         "Supplierid": 11,
#         "Productid": 71
#     }
#     """
#     try:
#         status = dict_data["status"]
#         supplier_id = dict_data["Supplierid"]
#         product_id = dict_data["Productid"]
#     except KeyError:
#         raise HTTPException(status_code=400, detail="Missing fields")
#     query = f"SELECT * FROM suppliedproducts WHERE Status = '{status}' AND SupplierID = '{supplier_id}' AND ProductID = '{product_id}';"
#     result = database.run_select_query(query)
#     return result

@app.post("/admin/requests", tags = ["admin"])
async def admin_users(dict_data: dict):
    """Returns all the suppliedproducts data
    status: str
    example: status = "Approved"
    Supplierid: int
    Productid: int

    testcase:
    {
        "status": "Accepted",
        "Supplierid": 33,
        "Productid": 58
    }
    """
    try:
        status = dict_data["status"]
        supplier_id = dict_data["Supplierid"]
        product_id = dict_data["Productid"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    #check if the status is accepted or rejected
    query = f"SELECT Status FROM suppliedproducts WHERE SupplierID = '{supplier_id}' AND ProductID = '{product_id}';"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="No such request")
    if result[0]["Status"] != "Pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    if status == "Accepted":
        #Update the product quantity
        query = f"UPDATE products SET ProductQuantity = ProductQuantity + (SELECT ProductQuantity FROM suppliedproducts WHERE SupplierID = '{supplier_id}' AND ProductID = '{product_id}') WHERE ProductID = '{product_id}';"
        if not database.run_update_query(query):
            raise HTTPException(status_code=400, detail="Error in updating the product quantity")
    query = f"UPDATE suppliedproducts SET Status = '{status}' WHERE SupplierID = '{supplier_id}' AND ProductID = '{product_id}';"
    if database.run_update_query(query):
        return {"message": "Success"}
    raise HTTPException(status_code=400, detail="Error in updating the status")

@app.get("/olap/{queryn}")
async def olap(queryn: int):
    # queryn = additional_data.Amount
    if queryn == 1:
        query = f"SELECT p.ProductName,p.ProductPrice,p.ProductQuantity,c.CategoryName, RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceRank, DENSE_RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceDenseRank, PERCENT_RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPricePercentRank, CUME_DIST() OVER (PARTITION BY c.CategoryID ORDER BY p.ProductPrice DESC) AS CategoryPriceCumDist FROM products p JOIN categories c ON p.CategoryID = c.CategoryID ORDER BY c.CategoryName, CategoryPriceRank;"
    elif queryn == 2:
        query = f"SELECT DATE_FORMAT(DATE_ADD(DeliveryDate, INTERVAL 7 DAY), '%Y-%m-%d') AS DeliveryDate_7_days_later, COUNT(*) AS Total_Checkouts FROM checkout WHERE DeliveryDate BETWEEN '2022-06-01' AND '2023-05-01' GROUP BY DeliveryDate_7_days_later ORDER BY DeliveryDate_7_days_later ASC;"
    elif queryn == 3:
        query = f"SELECT c.CategoryName, SUM(p.ProductPrice * ic.Quantity) AS TotalRevenue FROM categories c JOIN products p ON c.CategoryID = p.CategoryID JOIN itemsincarts ic ON p.ProductID = ic.ProductID JOIN cart ct ON ic.CartID = ct.CartID JOIN checkout chk ON ct.CartID = chk.CartID GROUP BY c.CategoryID;"
    elif queryn == 4:
        query = f"SELECT p.ProductName, SUM(ic.Quantity) AS TotalSold FROM products p JOIN itemsincarts ic ON p.ProductID = ic.ProductID GROUP BY p.ProductID ORDER BY TotalSold DESC LIMIT 10;"
    elif queryn == 5:
        query = f"SELECT users.DisplayName AS CustomerName, SUM(p.ProductPrice * ic.Quantity) AS Revenue FROM users JOIN cart ON users.UserID = cart.UserID JOIN itemsincarts ic ON cart.CartID = ic.CartID JOIN products p ON ic.ProductID = p.ProductID GROUP BY users.UserID ORDER BY Revenue DESC LIMIT 5;"
    else:
        query = f"SELECT categories.CategoryName, SUM(itemsincarts.Quantity) AS Quantity FROM categories JOIN products ON categories.CategoryID = products.CategoryID JOIN itemsincarts ON products.ProductID = itemsincarts.ProductID GROUP BY categories.CategoryName WITH ROLLUP;"
    result = database.run_select_query(query)
    return result

#list all orders of a user
@app.get("/user/orders/{userid}")
async def user_orders(userid: int):
    query = f"SELECT * FROM checkout WHERE UserID = {userid};"
    result = database.run_select_query(query)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORTtoc", default=5001), log_level="info")
