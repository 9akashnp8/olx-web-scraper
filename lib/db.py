from decouple import config
from pymongo import MongoClient

def get_database():
    client = MongoClient(config('CONNECTION_STRING'))
    return client['polo_api_db']