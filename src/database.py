# import modules & connect to MongoDB Atlas
import certifi
from pymongo import MongoClient

# connection to database
def connectDB(password):
  client = MongoClient(f'mongodb+srv://admin:{password}@cits.wpznlau.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())
  db = client.cits
  return db
  
# use hospital collection Create
def createHospitalInformation(hospitalName, address, lat, lon, tel, bed, room, dep, realbed):
  pass

def updateHospitalInformation():
  pass

def deleteHospitalInformation():
  pass
