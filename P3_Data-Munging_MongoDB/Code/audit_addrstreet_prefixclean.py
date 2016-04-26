import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_data50.osm"
street_pre_re = re.compile(r'^[NS][EW]')
street_pres = defaultdict(set)

#mapping dictionary - update directional abbreviations to full name
map_prefix = { 'NE': 'Northeast',
            'NW': 'Northwest',
            'SE': 'Southeast',
            'SW': 'Southwest'
            }
def audit_street_pre(street_pres, street_name):
    m = street_pre_re.search(street_name)
    if m:
        street_pre = m.group()
        street_pres[street_pre].add(street_name)

#returns streets only for processing.  no changes.  
def is_street(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    
    try:
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street(tag):
                        #directions to audit
                        audit_street_pre(street_pres, tag.attrib['v'])
    except ET.ParseError:
        pass
##    print street_pres
    return street_pres


def update_name(name, map_prefix):
    dirty_name = name
##    print 'name', name
    for map_ in map_prefix:
        print map_, map_prefix[map_]
        if re.search(map_, dirty_name):
            name = re.sub(map_, map_prefix[map_], dirty_name)
            print 'name', name
##        if re.search(re.escape(map)+ r'$', dirty_name):
##            print 'test', re.escape(map), r'$', dirty_name
##            name = re.sub(re.escape(map)+r'$', map_prefix[map], dirty_name)
    return name

#update with new variable names
def process_name():
    pre_types = audit(OSMFILE)

    for pre_type, ways in pre_types.iteritems():
        for name in ways:
            better_name = update_name(name, map_prefix)
            print name, "=>", better_name
            


if __name__ == '__main__':
    process_name()
#    audit(OSMFILE)
