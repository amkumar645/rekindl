from flask import Flask
from flask_pymongo import pymongo
from app import app

CONNECTION_STRING = "mongodb+srv://amkumar:amkumar@rekindl.ixsatdr.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('rekindl')
user_collection = pymongo.collection.Collection(db, 'users')