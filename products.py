from fastapi import APIRouter, HTTPException
from config import database
import json

router = APIRouter()


@router.get("/products", tags=["products"])
async def get_products():
    """Get all products."""
    query = "SELECT * FROM products;"
    result = database.run_select_query(query)
    return json.dumps(result)


@router.get("/products/{product_id}", tags=["products"])
async def get_product(product_id: int):
    """Get a product.
    Path parameters:
    - product_id: int
    """
    query = f"SELECT * FROM products WHERE ProductID = {product_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Product not found")
    return json.dumps(result)


@router.get("/products/category/{category_id}", tags=["products"])
async def get_products_by_category(category_id: int):
    """Get all products in a category.
    Path parameters:
    - category_id: int
    """
    query = f"SELECT * FROM products WHERE CategoryID = {category_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Category not found")
    return json.dumps(result)


@router.post("/products", tags=["products"])
async def add_product(form_data: dict):
    """Add a new product.
    Form data:
    - name: str
    - description: str
    - price: int
    - category_id: int (optional)
    - Rating: int (optional)
    - Quantity: int (optional)
    """
    try:
        name = form_data['name']
        description = form_data['description']
        price = form_data['price']
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    category_id = form_data.get('category_id', 1)
    Rating = form_data.get('Rating', 0)
    Quantity = form_data.get('Quantity', 0)
    query = f"INSERT INTO products (Name, Description, Price, CategoryID, Rating, Quantity) VALUES '{name}', '{description}', {price}, {category_id}, {Rating}, {Quantity};"
    if database.run_insert_query(query):
        return {"message": "success"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add product")
