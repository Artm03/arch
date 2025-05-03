import decimal
import os

from bson import decimal128
import pymongo
from pymongo.asynchronous import collection

from models import product as product_models


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
