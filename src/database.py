# import modules & connect to MongoDB Atlas
import certifi
from pymongo import MongoClient

def connectDB(password):
  client = MongoClient(f'mongodb+srv://admin:{password}@cits.wpznlau.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())
  db = client.cits
  return db
  
