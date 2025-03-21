import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_PORT = os.getenv("MONGODB_PORT")
MONGO_DB = os.getenv("MONGODB_DB")
MONGO_USER = os.getenv("MONGODB_USER")
MONGO_PASSWORD = os.getenv("MONGODB_PASSWORD")


def get_mongo_client():
    client = MongoClient("mongodb://" + MONGO_USER + ":" + MONGO_PASSWORD + "@" + MONGO_URI + ":" + MONGO_PORT + "/" + MONGO_DB + "?retryWrites=true")
    return client
