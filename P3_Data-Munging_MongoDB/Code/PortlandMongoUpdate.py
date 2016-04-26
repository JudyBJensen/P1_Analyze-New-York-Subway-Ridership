#query Portland_final update restaurant types
from pymongo import MongoClient
from datetime import datetime
import pprint

def get_query():
    query = {'name': 'Starbucks', 'amenity' : 'cafe'}
    return query

def get_update():
   #update Starbucks to include 'cuisine' : 'coffee_shop'
    update = {'$set':{'cuisine' : 'coffee_shop'}}
    return update
     
def get_db():
    client = MongoClient('localhost:27017')
    db = client.test
    return db                                          

if __name__ == "__main__":
    # ref Lesson 4
    db = get_db()
    query = get_query()
    update = get_update() 
    portland_oregon = db.portland_oregon.update(query, update, multi = True)
    #check step in query_proj...
    




