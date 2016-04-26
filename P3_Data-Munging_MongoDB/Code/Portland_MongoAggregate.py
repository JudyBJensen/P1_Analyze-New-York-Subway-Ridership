#aggregate data from portland_final
from pymongo import MongoClient
from datetime import datetime
import pprint

client = MongoClient('localhost:27017')
db = client.test


match = {'created.user' : {'$exists' :1}}
group = {'_id': '$type', 'count': {'$sum' : 1}}
result= db.portland_oregon.aggregate([{'$match': match},{'$group' : group}, {'$sort': {'count': -1}}])
#result= db.**.aggregate([{'$match': match},{'$group' : group}, {'$sort': {'count': -1}}])


print result 
for r in result:
    pprint.pprint(r)
                                                







