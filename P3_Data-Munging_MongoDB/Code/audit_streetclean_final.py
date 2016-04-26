import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_data50.osm"
#regex for suffix (Street, etc)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#regex for prefix (NE, etc)
street_pre_re = re.compile(r'^[NS][EW]')

#initialize audit dictionaries
street_types = defaultdict(set)

#dictionaries for suffix (Street, etc)
expected = ['Street', "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", 'Way', 'Terrace', 'Circle', 'Highway', 'Crest'] #remove "Street"
#Add Crest, Circle, Highway to expected
mapping = { "St": "Street",
            "St.": "Street",
            'street': 'Street',
            'Dr': 'Drive',
            "Ave.":  "Avenue",
            "Rd.": "Road", 
            "Ave": "Avenue",
            "Hwy": "Highway"
            }
#Add HWY to cleaning dictionary

#mapping dictionary - update directional abbreviations to full name
map_prefix = { 'NE': 'Northeast',
            'NW': 'Northwest',
            'SE': 'Southeast',
            'SW': 'Southwest'
            }

#build dictiionary for audits (Street type and directional abbreviations)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    mp = street_pre_re.search(street_name)
    if mp:
        street_pre = mp.group()
        street_types[street_pre].add(street_name)

##def audit_street_pre(street_pres, street_name):
##    m = street_pre_re.search(street_name)
##    if m:
##        street_pre = m.group()
##        street_pres[street_pre].add(street_name)

# no changes
def is_street(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    
    try:
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
               #update defaultdict:
                    if is_street(tag):
                        audit_street_type(street_types, tag.attrib['v'])

    except ET.ParseError:
        pass
    print 'street_types: ', street_types 
    return street_types
               

def update_name(name, mapping, map_prefix):
    dirty_name = name
    for map in mapping:
        if re.search(re.escape(map)+ r'$', dirty_name):
            name = re.sub(re.escape(map)+r'$', mapping[map], dirty_name)
    dirty_name = name
    for map_ in map_prefix:
        if re.search(map_, dirty_name):
            name = re.sub(map_, map_prefix[map_], dirty_name)
            
    return name

def process_street():
    st_types = audit(OSMFILE)
    print type(st_types)

    for st_type, ways in st_types.iteritems():
        
        for name in ways:
            better_name = update_name(name, mapping, map_prefix)
            print name, "=>", better_name
            


if __name__ == '__main__':
    #process_street()
    audit(OSMFILE)
