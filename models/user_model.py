import os
from pymongo import MongoClient

mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['jungle8_63']
users_collection = db['users']