import decimal
import os
import typing as tp

import bson
from bson import decimal128
import fastapi
import pymongo
from pymongo.asynchronous import collection

from models import product as product_models

router = fastapi.APIRouter(prefix="/products", tags=["products"])


def get_mongo_collection() -> collection.AsyncCollection:
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://mongo-db:27017/")
    db_name = os.environ.get("MONGO_DB_NAME", "products_db")

    client = pymongo.AsyncMongoClient(mongo_uri)
    db = client.get_database(db_name)
    collection_name = os.environ.get("MONGO_COLLECTION", "products")
    
    return db.get_collection(collection_name)


def decimal_to_decimal128(value):
    if isinstance(value, decimal.Decimal):
        return decimal128.Decimal128(str(value))
    return value


def decimal128_to_decimal(value):
    if hasattr(value, 'to_decimal'):
        return value.to_decimal()
    return value


def mongo_to_product(product_doc):
    product_dict = dict(product_doc)

    if 'price' in product_dict:
        product_dict['price'] = decimal128_to_decimal(product_dict['price'])

    if '_id' in product_dict:
        product_dict['id'] = str(product_dict.pop('_id'))

    return product_models.Product(**product_dict)


# GET /products/list - Получить все продукты с возможностью фильтрации
@router.get("/list", response_model=tp.List[product_models.Product])
async def get_products(
    name: tp.Optional[str] = None,
    category: tp.Optional[str] = None,
    min_price: tp.Optional[float] = None,
    max_price: tp.Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)
):
    filter_query = {}

    if name is not None:
        filter_query['name'] = {'$regex': name, '$options': 'i'}
    if category is not None:
        filter_query['category'] = {'$regex': category, '$options': 'i'}
    
    price_filter = {}
    if min_price is not None:
        price_filter['$gte'] = decimal_to_decimal128(decimal.Decimal(str(min_price)))
    if max_price is not None:
        price_filter['$lte'] = decimal_to_decimal128(decimal.Decimal(str(max_price)))
    if price_filter:
        filter_query['price'] = price_filter
    
    products: tp.List[product_models.Product] = []
    async for item in collection.find(filter_query).skip(offset).limit(limit):
        products.append(mongo_to_product(item))

    return products



@router.get("/details", response_model=product_models.Product)
async def get_product(product_id: str, collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)):
    try:
        object_id = bson.ObjectId(product_id)
        product_doc = await collection.find_one({"_id": object_id})
    except Exception:
        raise fastapi.HTTPException(status_code=404, detail="Invalid product ID format")

    if not product_doc:
        raise fastapi.HTTPException(status_code=404, detail="Product not found")

    return mongo_to_product(product_doc)


# POST /products/create - Создать новый продукт
@router.post("/create", response_model=product_models.Product, status_code=201)
async def create_product(
    product: product_models.ProductCreate, 
    collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)
):
    product_dict = product.model_dump()
    product_dict['price'] = decimal_to_decimal128(product_dict['price'])

    result = await collection.insert_one(product_dict)
    created_product = await collection.find_one({"_id": result.inserted_id})
    
    return mongo_to_product(created_product)


# PUT /products/update - Обновить продукт по ID
@router.put("/update", response_model=product_models.Product)
async def update_product(
    product_id: str, 
    product_update: product_models.ProductBase, 
    collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)
):
    try:
        object_id = bson.ObjectId(product_id)
    except Exception:
        raise fastapi.HTTPException(status_code=404, detail="Invalid product ID format")

    existing_product = await collection.find_one({"_id": object_id})
    if not existing_product:
        raise fastapi.HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.model_dump()
    update_data['price'] = decimal_to_decimal128(update_data['price'])

    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )

    updated_product = await collection.find_one({"_id": object_id})
    
    return mongo_to_product(updated_product)


# DELETE /products/delete - Удалить продукт по ID
@router.delete("/delete", response_model=product_models.Product)
async def delete_product(product_id: str, collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)):
    try:
        object_id = bson.ObjectId(product_id)
    except Exception:
        raise fastapi.HTTPException(status_code=404, detail="Invalid product ID format")

    product_doc = await collection.find_one({"_id": object_id})
    if not product_doc:
        raise fastapi.HTTPException(status_code=404, detail="Product not found")

    await collection.delete_one({"_id": object_id})

    return mongo_to_product(product_doc)


# /create/bulk - массовое добавление продуктов
@router.post("/create/bulk", response_model=tp.List[product_models.Product])
async def create_products_bulk(
    products: tp.List[product_models.ProductCreate], 
    collection: collection.AsyncCollection = fastapi.Depends(get_mongo_collection)
):
    product_dicts = []
    
    for product in products:
        product_dict = product.model_dump()
        product_dict['price'] = decimal_to_decimal128(product_dict['price'])
        product_dicts.append(product_dict)

    if product_dicts:
        result = await collection.insert_many(product_dicts)
        inserted_products: tp.List[product_models.Product] = []
        async for item in collection.find({"_id": {"$in": result.inserted_ids}}):
            inserted_products.append(mongo_to_product(item))
        
        return inserted_products
    
    return []
