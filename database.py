import os

import certifi
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "avaliacao_sono"


def connect_mongodb():
    client = pymongo.MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
    db = client[DATABASE_NAME]
    return client, db
