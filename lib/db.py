from decouple import config
from pymongo import MongoClient

def get_database():
    client = MongoClient(config('CONNECTION_STRING'))
    return client[config('DB_NAME')]