from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['jungle8_63']
posts_collection = db['posts']