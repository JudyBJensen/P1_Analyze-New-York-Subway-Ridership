#query Portland_final collection in test database
from pymongo import MongoClient
from datetime import datetime
import pprint


client = MongoClient('localhost:27017')
db = client.test
variable = ("_id")

exists = db.portland_oregon.find({variable : {"$exists" : 1}}).count()
unexists = db.portland_oregon.find({variable : {"$exists" : 0}}).count()
print "exists, not exist: ", variable, exists, unexists


    




