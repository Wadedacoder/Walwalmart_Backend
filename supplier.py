from fastapi import APIRouter, HTTPException
from config import database

# import hashlib
# import json

router = APIRouter()


@router.get("/suppliers", tags=["suppliers"])
async def get_suppliers():
    """Get all suppliers."""
    query = "SELECT * FROM suppliers;"
    result = database.run_select_query(query)
    return result


@router.get("/suppliers/{supplier_id}", tags=["suppliers"])
async def get_supplier(supplier_id: int):
    """Get a supplier.
    Path parameters:
    - supplier_id: int
    """
    query = f"SELECT * FROM suppliers WHERE SupplierID = {supplier_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Supplier not found")
    return result


@router.post("/suppliers", tags=["suppliers"])
async def add_supplier(form_data: dict):
    """Add a new supplier.
    Form data:
    - name: str
    - phone: str (optional)
    - Address: optional
    Address:
    - Building: str (optional)
    - Street: str (optional)
    - City: str (optional)
    - State: str (optional)
    """
    try:
        name = form_data['name']

    except KeyError:
        raise HTTPException(status_code=400, detail="Missing fields")
    phone = form_data.get('phone', "")
    Building = form_data.get('Building', "")
    Street = form_data.get('Street', "")
    City = form_data.get('City', "")
    State = form_data.get('State', "")
    query = f"INSERT INTO addresses (Building, Street, City, State) VALUES ('{Building}', '{Street}', '{City}', '{State}');"
    if not database.run_insert_query(query):
        raise HTTPException(status_code=500, detail="Failed to add address")
    query = f"INSERT INTO suppliers (Name, Phone, AddressID) VALUES ('{name}', '{phone}', (SELECT AddressID FROM addresses WHERE Building = '{Building}' AND Street = '{Street}' AND City = '{City}' AND State = '{State}'));"
    if not database.run_insert_query(query):
        raise HTTPException(status_code=500, detail="Failed to add supplier")
    if phone != "":
        query = f"INSERT INTO phones (Phone) VALUES ('{phone}');"
        if not database.run_insert_query(query):
            raise HTTPException(status_code=500, detail="Failed to add phone")
    return {"message": "Supplier added successfully"}

@router.put("/suppliers/{supplier_id}", tags=["suppliers"])
async def update_supplier(supplier_id: int, form_data: dict):
    """Update a supplier.
    Path parameters:
    - supplier_id: int
    Form data:
    - name: str (optional)
    - phone: str (optional)
    - Address: optional
    Address:
    - Building: str (optional)
    - Street: str (optional)
    - City: str (optional)
    - State: str (optional)
    """
    name = form_data.get('name', "")
    phone = form_data.get('phone', "")
    Building = form_data.get('Building', "")
    Street = form_data.get('Street', "")
    City = form_data.get('City', "")
    State = form_data.get('State', "")
    if name != "":
        query = f"UPDATE suppliers SET Name = '{name}' WHERE SupplierID = {supplier_id};"
        if not database.run_update_query(query):
            raise HTTPException(status_code=500, detail="Failed to update supplier")
    if phone != "":
        query = f"UPDATE suppliers SET Phone = '{phone}' WHERE SupplierID = {supplier_id};"
        if not database.run_update_query(query):
            raise HTTPException(status_code=500, detail="Failed to update supplier")
        query = f"INSERT INTO phones (Phone) VALUES ('{phone}');"
        if not database.run_insert_query(query):
            raise HTTPException(status_code=500, detail="Failed to add phone")
    if Building != "" or Street != "" or City != "" or State != "":
        query = f"INSERT INTO addresses (Building, Street, City, State) VALUES ('{Building}', '{Street}', '{City}', '{State}');"
        if not database.run_insert_query(query):
            raise HTTPException(status_code=500, detail="Failed to add address")
        query = f"UPDATE suppliers SET AddressID = (SELECT AddressID FROM addresses WHERE Building = '{Building}' AND Street = '{Street}' AND City = '{City}' AND State = '{State}') WHERE SupplierID = {supplier_id};"
        if not database.run_update_query(query):
            raise HTTPException(status_code=500, detail="Failed to update supplier")
    return {"message": "Supplier updated successfully"}

@router.delete("/suppliers/{supplier_id}", tags=["suppliers"])
async def delete_supplier(supplier_id: int):
    """Delete a supplier.
    Path parameters:
    - supplier_id: int
    """
    query = f"DELETE FROM suppliers WHERE SupplierID = {supplier_id};"
    if not database.run_delete_query(query):
        raise HTTPException(status_code=500, detail="Failed to delete supplier")
    return {"message": "Supplier deleted successfully"}

@router.get("/suppliers/{supplier_id}/products", tags=["suppliers"])
async def get_supplier_products(supplier_id: int):
    """Get all products of a supplier.
    Path parameters:
    - supplier_id: int
    """
    query = f"SELECT * FROM suppliedproducts WHERE SupplierID = {supplier_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Supplier not found")
    return result

@router.get("/suppliers/{supplier_id}/products/{product_id}", tags=["suppliers"])
async def get_supplier_product(supplier_id: int, product_id: int):
    """Get a product of a supplier.
    Path parameters:
    - supplier_id: int
    - product_id: int
    """
    query = f"SELECT * FROM suppliedproducts WHERE SupplierID = {supplier_id} AND ProductID = {product_id};"
    result = database.run_select_query(query)
    if result == "[]":
        raise HTTPException(status_code=400, detail="Product not found")
    return result

@router.post("/suppliers/{supplier_id}/products/{product_id}", tags=["suppliers"])
async def add_supplier_product(supplier_id: int, product_id: int, form_data: dict):
    """Add a product to a supplier.
    Path parameters:
    - supplier_id: int
    - product_id: int
    Form data:
    - quantity: float
    """
    quantity = form_data.get('price', "")
    if quantity == "":
        raise HTTPException(status_code=400, detail="Missing fields")
    query = f"INSERT INTO suppliedproducts (SupplierID, ProductID, ProductQuantity) VALUES ({supplier_id}, {product_id}, {quantity});"
    if not database.run_insert_query(query):
        raise HTTPException(status_code=500, detail="Failed to add product")
    return {"message": "Product added successfully"}

@router.put("/suppliers/{supplier_id}/products/{product_id}", tags=["suppliers"])
async def update_supplier_product(supplier_id: int, product_id: int, form_data: dict):
    """Update a product of a supplier.
    Path parameters:
    - supplier_id: int
    - product_id: int
    Form data:
    - price: float (optional)
    """
    price = form_data.get('price', "")
    if price != "":
        query = f"UPDATE suppliedproducts SET ProductQuantity = {price} WHERE SupplierID = {supplier_id} AND ProductID = {product_id};"
        if not database.run_update_query(query):
            raise HTTPException(status_code=500, detail="Failed to update product")
    return {"message": "Product updated successfully"}

@router.delete("/suppliers/{supplier_id}/products/{product_id}", tags=["suppliers"])
async def delete_supplier_product(supplier_id: int, product_id: int):
    """Delete a product of a supplier.
    Path parameters:
    - supplier_id: int
    - product_id: int
    """
    query = f"DELETE FROM suppliedproducts WHERE SupplierID = {supplier_id} AND ProductID = {product_id};"
    if not database.run_delete_query(query):
        raise HTTPException(status_code=500, detail="Failed to delete product")
    return {"message": "Product deleted successfully"}



