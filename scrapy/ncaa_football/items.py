# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import DictItem, Field
    
def create_item_class(class_name,field_list):
    """Create item class"""
    field_dict = {}
    for field_name in field_list:
        field_dict[field_name] = Field()

    return type(class_name, (DictItem,), {'fields':field_dict})
