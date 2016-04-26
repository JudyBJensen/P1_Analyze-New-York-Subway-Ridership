#query Portland_final collection in test database and return name
from pymongo import MongoClient
from datetime import datetime
import pprint

def get_query():
    #define key:value or attribute of interest

    query = {'amenity' : 'restaurant', 'amenity' : 'pub', 'amenity' : 'cafe'}
#    query = {'amenity' : 'restaurant', 'amenity' : 'pub', 'amenity' : 'cafe', 'name': {'$ne':'Starbucks'}}
    return query

def get_projection():
    projection = {'_id': 0, 'amenity': 1, 'cuisine' :1, 'name': 1}
    return projection

def get_db():
    client = MongoClient('localhost:27017')
    db = client.test
    return db                                          

if __name__ == "__main__":
    # ref Lesson 4
    db = get_db()
    query = get_query()
    projection = get_projection()
    result = db.portland_oregon.find(query, projection)
    for r in result:
        pprint.pprint(r)
    




