# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import DictItem, Field


class item_teamlinks(scrapy.Item):
    """Scrapy Item for Team Links for 2014-2017"""
    Link = scrapy.Field()
    Team = scrapy.Field()
    Year = scrapy.Field()

class item_TeamInfoLinks(scrapy.Item):
    """Scrapy Item for Team Links for 2014-2017"""
    team = scrapy.Field()
    link = scrapy.Field()
    txt = scrapy.Field()
    key = scrapy.Field()
    year = scrapy.Field()

class item_Results(scrapy.Item):
    """Scrapy Item yearly team results"""
    Team = scrapy.Field()
    Date = scrapy.Field()
    Opponent = scrapy.Field()
    Result = scrapy.Field()

class item_TeamStats(scrapy.Item):
    """Scrapy Item yearly team stats"""
    Team = scrapy.Field()
    Stat = scrapy.Field()
    Rank = scrapy.Field()
    Value = scrapy.Field()
    Year = scrapy.Field()

class item_IndividualLeaders(scrapy.Item):
    """Scrapy Item yearly individual leaders"""
    Team = scrapy.Field()
    Stat = scrapy.Field()
    Player = scrapy.Field()
    Value = scrapy.Field()
    Year = scrapy.Field()

class item_coaches(scrapy.Item):
    """Scrapy Item for Coaching Profiles"""
    Year = scrapy.Field()
    Org = scrapy.Field()
    Division = scrapy.Field()
    Wins = scrapy.Field()
    Losses = scrapy.Field()
    Ties = scrapy.Field()
    WL = scrapy.Field()
    Notes = scrapy.Field()
    Name = scrapy.Field()


class item_roster(scrapy.Item):
    """Scrapy Item for yearly roster"""
    Year = scrapy.Field()
    Team = scrapy.Field()
    Jersey = scrapy.Field()
    Player = scrapy.Field()
    Pos = scrapy.Field()
    Yr = scrapy.Field()
    GP = scrapy.Field()
    GS = scrapy.Field()
    
class item_history(scrapy.Item):
    """Scrapy Item Team History"""
    Team = scrapy.Field()
    Year = scrapy.Field()
    HeadCoaches = scrapy.Field()
    Division = scrapy.Field()
    Conference = scrapy.Field()
    Wins = scrapy.Field()
    Losses = scrapy.Field()
    Ties = scrapy.Field()
    WL = scrapy.Field()
    Notes = scrapy.Field()


def create_item_class(class_name,field_list):
    field_dict = {}
    for field_name in field_list:
        field_dict[field_name] = Field()

    return type(class_name, (DictItem,), {'fields':field_dict})
