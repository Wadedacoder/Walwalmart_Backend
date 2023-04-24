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

    Testcase:
    {
        "username": "test",
        "password": "test",
        "display_name": "test"
    }
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

    Testcase:
    {
        "username": "test",
        "password": "test"
    }
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
    # print(display_name, type(display_name), amount, type(amount), phone, type(phone), address, type(address))
    query = f"UPDATE users SET"
    if display_name:
        query += f" DisplayName = '{display_name}',"
    if amount:
        query += f" Amount = {amount},"
    if phone:
        query += f" Phone = '{phone}',"
    query = query[:-1] + f" WHERE UserID = {user_id};"
    if database.run_update_query(query):
        print("success")
    else:
        raise HTTPException(status_code=400, detail="Update failed")
    if address:
        query1 = f"INSERT INTO address (Building, Street, City, State) VALUES "
        query1 += f"('{address.get('Building', None)}', '{address.get('Street', None)}', '{address.get('City', None)}', '{address.get('State', None)}');"
        database.run_insert_query(query1)
        query = f"UPDATE users SET AddressID = (SELECT AddressID FROM address WHERE Building = '{address.get('Building', None)}' AND Street = '{address.get('Street', None)}' AND City = '{address.get('City', None)}' AND State = '{address.get('State', None)}') WHERE UserID = {user_id};"
        if database.run_update_query(query):
            print("success update address")
        else:
            raise HTTPException(status_code=400, detail="Update failed")
    return {"message": "success"}


@router.post("/users/cart/add", tags=["users"])
async def add_to_cart(form_data: dict):
    """Add item to cart.
        Form data:
        - user_id: int
        - product_id: int
        - quantity: int (optional) (default: 1)

        Generate a Test Case dict:
            {
                "user_id": 101,
                "product_id": 1,
                "quantity": 1
            }

    """
    try:
        user_id = form_data['user_id']
        product_id = form_data['product_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    quantity = form_data.get('quantity', 1)
    # Check if items already in cart
    query = f"SELECT * FROM itemsincarts WHERE CartID = (SELECT CartID FROM cart WHERE carts.UserID = {user_id}) AND ProductID = {product_id};"
    result = database.run_select_query(query)
    if result != "[]" and len(result) > 0:
        # If item already in cart, update quantity
        quantity += result[0]["Quantity"]
        query = f"UPDATE itemsincarts SET Quantity = {quantity} WHERE CartID = (SELECT CartID FROM cart WHERE carts.UserID = {user_id}) AND ProductID = {product_id};"
        if database.run_update_query(query):
            return {"status": "success", "message": "Item updated in cart"}
    query = f"INSERT INTO itemsincarts (CartID, ProductID, Quantity) VALUES " \
            f"((SELECT CartID FROM cart WHERE cart.UserID = {user_id}), {product_id}, {quantity});"
    if database.run_insert_query(query):
        return {"status": "success", "message": "Item added to cart"}
    else:
        raise HTTPException(status_code=400, detail="Add to cart failed")


@router.post("/users/cart/remove", tags=["users"])
async def remove_from_cart(form_data: dict):
    """
    Remove item from cart.
    Form data:
    - user_id: int
    - product_id: int
    - quantity: int (optional) (default: all)

    Generate a Test Case dict:
        {
            "user_id": 101,
            "product_id": 1,
            "quantity": 1
        }
    """
    try:
        user_id = form_data['user_id']
        product_id = form_data['product_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    quantity = form_data.get('quantity', None)
    # Check if items already in cart
    query = f"SELECT * FROM itemsincarts WHERE CartID = (SELECT CartID FROM cart WHERE carts.UserID = {user_id}) AND ProductID = {product_id};"
    result = database.run_select_query(query)
    if result != "[]":
        # If item already in cart, update quantity
        if quantity is None:
            quantity = result[0]["Quantity"]
        quantity = result[0]["Quantity"] - quantity
        if quantity <= 0:
            query = f"DELETE FROM itemsincarts WHERE CartID = (SELECT CartID FROM cart WHERE carts.UserID = {user_id}) AND ProductID = {product_id};"
        else:
            query = f"UPDATE itemsincarts SET Quantity = {quantity} WHERE CartID = (SELECT CartID FROM cart WHERE carts.UserID = {user_id}) AND ProductID = {product_id};"
        if database.run_update_query(query):
            return {"status": "success", "message": "Item removed from cart"}
    else:
        raise HTTPException(status_code=400, detail="Item not in cart")
    raise HTTPException(status_code=400, detail="Remove from cart failed")


@router.get("/users/cart", tags=["users"])
async def get_cart(user_id: int):
    """Get cart items.
    Query params:
    - user_id: int
    """
    query = f"SELECT CartID as ID FROM cart WHERE cart.UserID = {user_id};"
    cartID = database.run_select_query(query)[0]["ID"]
    # Add product info from products to cart items
    query = f"SELECT * FROM itemsincarts JOIN products ON itemsincarts.ProductID = products.ProductID WHERE CartID = {cartID};"
    result = database.run_select_query(query)
    if result != "[]":
        return result
    else:
        return {"status": "success", "message": "Cart is empty"}


@router.post("/users/cart/checkout", tags=["users"])
async def checkout_cart(form_data: dict):
    """Checkout cart.
    Form data:
    - user_id: int
    - payment_method: str

    Generate a Test Case dict:
        {
            "user_id": 101,
            "payment_method": "cash"
        }
    """
    try:
        user_id = form_data['user_id']
        payment_method = form_data['payment_method']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    query = f"SELECT CartID as ID FROM cart WHERE cart.UserID = {user_id};"
    cart = database.run_select_query(query)
    # Retrieve cart items
    cart_id = cart[0]["ID"]
    query = f"SELECT * FROM itemsincarts WHERE CartID = {cart_id};"
    products_in_cart = database.run_select_query(query)
    if products_in_cart == "[]":
        raise HTTPException(status_code=400, detail="Cart is empty")
    # Check if user has enough money
    query = f"SELECT * FROM users WHERE UserID = {user_id};"
    user = database.run_select_query(query)
    if user == "[]":
        raise HTTPException(status_code=400, detail="User not found")
    query = f"SELECT * FROM products WHERE ProductID IN (SELECT ProductID FROM itemsincarts WHERE CartID = {cart_id});"
    products_info = database.run_select_query(query)
    sorted(products_info, key=lambda k: k['ProductID'])
    sorted(products_in_cart, key=lambda k: k['ProductID'])
    # print("products_info: ",products_info, products_in_cart)
    if products_info == "[]":
        raise HTTPException(status_code=400, detail="No products in cart")
    total_price = 0
    for i in range(len(products_in_cart)):
        total_price += products_info[i]["ProductPrice"] * products_in_cart[i]["Quantity"]
    if total_price > user[0]["Amount"]:
        raise HTTPException(status_code=400, detail="Not enough money")
    # Add all items to orders
    # Create a delivery
    query = f"INSERT INTO delivery (AddressesID, DeliveryStatus) VALUES ({user[0]['AddressID']}, 'Pending');"
    if not database.run_insert_query(query):
        raise HTTPException(status_code=401, detail="Delivery failed")
    # Get delivery id
    query = f"SELECT MAX(DeliveryID) FROM delivery;"
    delivery_id = database.run_select_query(query)
    if delivery_id == "[]":
        raise HTTPException(status_code=401, detail="Delivery failed")
    delivery_id = delivery_id[0]["MAX(DeliveryID)"]
    # Create an checkout
    query = f"INSERT INTO checkout (CartID, DeliveryID, PaymentInfo) VALUES ({cart_id},{delivery_id}, '{payment_method}');"
    if not database.run_insert_query(query):
        raise HTTPException(status_code=401, detail="Checkout failed")
    # Get checkout id
    query = f"SELECT CheckoutID FROM checkout WHERE CartID = {cart_id} AND DeliveryID = {delivery_id} AND PaymentInfo = '{payment_method}';"
    checkout_id = database.run_select_query(query)
    if checkout_id == "[]":
        raise HTTPException(status_code=401, detail="Checkout failed")
    checkout_id = checkout_id[0]["CheckoutID"]
    #Add items of cart to orders
    print(products_in_cart)
    for i in range(len(products_in_cart)):
        # print(products_in_cart[i]['ProductID'])
        query = f"INSERT INTO orders (CheckoutID, ProductID, Quantity) VALUES ({checkout_id},{products_in_cart[i]['ProductID']},{products_in_cart[i]['Quantity']});"
        if not database.run_insert_query(query):
            raise HTTPException(status_code=401, detail="Checkout failed")
    # Update user balance
    query = f"UPDATE users SET Amount = {user[0]['Amount'] - total_price} WHERE UserID = {user_id};"
    if not database.run_update_query(query):
        raise HTTPException(status_code=401, detail="Updation failed")
    # Delete items from cart
    query = f"DELETE FROM itemsincarts WHERE CartID = {cart_id};"
    if not database.run_update_query(query):
        raise HTTPException(status_code=401, detail="Updation failed")
    #return delivery_id and checkout_id along with cost
    return {"status": "success", "message": "Checkout successful", "delivery_id": delivery_id, "checkout_id": checkout_id, "cost": total_price}

