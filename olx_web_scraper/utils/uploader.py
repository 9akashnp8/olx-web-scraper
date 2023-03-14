from .db import get_database
from pymongo.errors import DuplicateKeyError
from decouple import config

dbname = get_database()

collection = dbname[config('COLLECTION_NAME')]

def uploader(data):
    for item in data:
        document = {
            "_id": item[0],
            "ad_price": item[1],
            "model_year": item[2],
            "kms_driven": item[3],
            "ad_title": item[4],
            "ad_location": item[5],
            "ad_link": item[6],
        }
        try:
            collection.insert_one(document)
        except DuplicateKeyError:
            pass
            # collection.update_one({
            #     "_id": document["_id"]
            # }, {
            #     "$set": {
            #         "ad_price": item[1],
            #         "model_year": item[2],
            #         "kms_driven": item[3],
            #         "ad_title": item[4],
            #         "ad_location": item[5],
            #         "ad_link": item[6],
            #     }
            # })
