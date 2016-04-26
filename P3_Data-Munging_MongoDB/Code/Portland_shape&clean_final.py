#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
"""
Shape the data and save as a JSON dictionary for import into MongoDB:
Reference:  Problem Set 6:4

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

process data
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}
- clean addr:street
- add add:city where addr:postcode matches '606'

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]

In addition to course instructions, the following cleaning steps are implemented:  Update street address suffix,
update street address directional, update zip codes to 5 digit

"""

#OSMFILE = "sample_data50.osm"
OSMFILE = "portland_oregon.osm"

#regex for suffix (Street, etc)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) #suffix (Street, etc)
street_pre_re = re.compile(r'^[NS][EW]') #prefix (NE, etc)
add_zip_re = re.compile(r'^972') #zipcode (972)
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

###initialize audit dictionaries

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


def is_street(elem):
    return (elem.attrib['k'] == "addr:street")

def is_zip(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_city(elem):
    return (elem.attrib['k'] == 'addr:city')

def is_num(s):
    try:
        float(s)
        return float(s)
    except ValueError:
        return None


#cleaning step for street name
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

#cleaning step for zipcode
def update_zip(zip):
    old_zip = zip
    if len(old_zip) > 5:
        zip = zip[:5]
    return zip


#List for created key
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    if element.tag == "way" or element.tag == "node":
        
        #keys w no processing required:  
        if 'id' in element.attrib.keys():
            node['id'] = element.attrib['id']
        if 'visible' in element.attrib.keys():
            node['visible'] = element.attrib['visible']
        node['type'] = element.tag
        # create 'created' dictionary and populate with keys in CREATED
        created = {}
        for c in CREATED:
            created[c] = element.attrib[c]
        node['created'] = created

        #process lat & long into pos
        pos = []
        if 'lon' in element.attrib.keys() and 'lat' in element.attrib.keys():
            pos.append(is_num(element.attrib['lat']))
            pos.append(is_num(element.attrib['lon']))
            node['pos'] = pos
            
        #process keys
        address = {}
        for elem in element.iter('tag'):
            try: 
                key = elem.attrib['k']
                variable = elem.attrib['v']
                #eliminate keys with problem characters:
                if problemchars.search(key) != None:
                    pass
                #process lower colon (not address, address)
                elif lower_colon.match(key) != None:
    #process address (no cleaning required)
                    if key[:4] != 'addr' and key[:4] != 'postcode':
                        node[key] = variable
    #clean and process street and zip
                    elif key == 'addr:street':
                        variable = update_name(elem.attrib['v'], mapping, map_prefix)
                        address[key[5:]] = variable
                        node['address'] = address
                        
                    else:
                        if key == 'addr:postcode':
                            variable = update_zip(elem.attrib['v'])
                        address[key[5:]] = variable
                        node['address'] = address

                #remove addr w > 1 ':'
                elif key[:4] == 'addr':
                    pass
                else:
                    node[key] = variable
            except KeyError:
                pass
        #add node ref
            if element.tag == 'way':
                node_ref = []        
                for n in element.iter('nd'):
                    node_ref.append(n.attrib['ref'])
                node['node_refs'] = node_ref
        return node
    else:
        return None

#REFERENCE: http://stackoverflow.com/questions/12160418/why-is-lxml-etree-iterparse-eating-up-all-my-memory


def process_map(file_in, pretty = False):
    # You do not need to change this file
    #Ref lesson 6
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        try:
            for _, element in ET.iterparse(file_in):
                el = shape_element(element)
                if el:
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
                    #element.clear() #el.clear()

        except ET.ParseError:
            pass
    return data


if __name__ == "__main__":
    data = process_map(OSMFILE, False)
