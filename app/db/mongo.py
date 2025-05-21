# app/db/mongo.py
from pymongo import MongoClient
from app.core.config import settings

client: MongoClient = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db]

def get_collection(name: str = "cryptocurrencies"):
    return db[name]