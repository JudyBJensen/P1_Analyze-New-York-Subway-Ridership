import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_data50.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)


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

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    
    try:
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street(tag):
                        audit_street_type(street_types, tag.attrib['v'])
    except ET.ParseError:
        pass
    return street_types
##    pprint.pprint(street_types)
##    print len(street_types)

def update_name(name, mapping):
    dirty_name = name
    for map in mapping:
        if re.search(re.escape(map)+ r'$', dirty_name):
            name = re.sub(re.escape(map)+r'$', mapping[map], dirty_name)
    return name

def process_name():
    st_types = audit(OSMFILE)

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            


if __name__ == '__main__':
    process_name()