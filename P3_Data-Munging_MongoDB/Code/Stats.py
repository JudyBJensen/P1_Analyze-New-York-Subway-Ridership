#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
"""
import xml.etree.cElementTree as ET
from xml.etree.cElementTree import ParseError
import pprint

#filename = 'portland_oregon.osm'
#filename = 'sample_data.osm'
filename = 'portland_oregon.osm'

def count_tags(filename):
    tag_dict = {}
    count = 0
    event_count = 0
    try:
#        for event, element in ET.iterparse(filename, events = ('start', )):
        for event, element in ET.iterparse(filename, events = ('start', )):
            tag_entry = element.tag
            if tag_entry not in tag_dict:
                tag_dict[tag_entry] = 1
            else:
                tag_dict[tag_entry] +=1
            event_count +=1
            element.clear()
    except ET.ParseError:
        pass
    return tag_dict

if __name__ == "__main__":
    tag_dict, count, event_count = {}, 0, 0
    tag_dict = count_tags(filename)
    print filename, tag_dict
    
