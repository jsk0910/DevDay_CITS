# import modules & connect to MongoDB Atlas
import certifi
from pymongo import MongoClient

client = MongoClient('mongodb+srv://admin:admin1234@cits.wpznlau.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.cits

#example insert
examples = {
    "firstCode" : "A",
    "secondCode" : "A",
    "thirdCode" : "A",
    "fourthCode" : "AA",
    "Code" : 1,
    "description" : "15세 이상, 물질오용/중독, 중증 호흡곤란",
    "matchCode" : "물질오용"
}
db.codeTable.insert_one(examples)
