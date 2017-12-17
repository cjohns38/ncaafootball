# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from scrapy.exporters import CsvItemExporter

class TeamLinksCSVPipeline(object):
    """Scrapy Pipeline Object for Team Links 2014-2017"""
    def __init__(self):
        fileName = "TeamLinks.csv"
        self.file = open(os.path.join("Links", fileName), 'wb')
        self.exporter = CsvItemExporter(self.file, fields_to_export=['Team', 'Year', 'Link'])
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class LinksResultsTeamIndividualCSVPipeline(object):
    """Scrapy Pipeline Object for Links, Results, Team, Individual"""
    types = ['teaminfolinks', 'results', 'teamstats', 'individualleaders']
    
    def open_spider(self, spider):
        # CreateFiles 
        self.files = {t: open(os.path.join("Data", t + '.csv'), 'wb') for t in self.types[1:]}
        # Send links to link folder 
        self.files[self.types[0]] = open(os.path.join("Links", self.types[0] + '.csv'), 'wb')
        # Create exporters 
        self.exporters = {t:CsvItemExporter(self.files[t]) for t in self.types}
        [e.start_exporting() for e in self.exporters.values()]
    
    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]
 
    def process_item(self, item, spider):
        # Define what item type it is 
        itemType = type(item).__name__.replace("item_", "").lower()
        
        # Export 
        self.exporters[itemType].export_item(item)
        
        return item


class CoachesCSVPipeline(object):
    """Scrapy Pipeline Object for Coaching Profiles"""
    def open_spider(self,spider):
        fileName = "Coaches.csv"
        self.file = open(os.path.join("Data", fileName), 'wb')
        self.exporter = CsvItemExporter(self.file, fields_to_export=["Name", "Year", "Org", "Division", "Wins", "Losses", "Ties", "WL", "Notes"])
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class RosterCSVPipeline(object):
    """Scrapy Pipeline Object for yearly roster"""
    def open_spider(self,spider):
        fileName = "Roster.csv"
        self.file = open(os.path.join("Data", fileName), 'wb')
        self.exporter = CsvItemExporter(self.file, fields_to_export=["Year", "Team", "Jersey","Player","Pos","Yr","GP","GS"])
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class HistoryCSVPipeline(object):
    """Scrapy Pipeline Object for History"""
    
    def open_spider(self,spider):
        fileName = "History.csv"
        self.file = open(os.path.join("Data", fileName), 'wb')
        self.exporter = CsvItemExporter(self.file, fields_to_export=["Team","Year","Head Coaches","Division","Conference","Wins","Losses","Ties","WL","Notes"])
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class Pipeline(object):
    """Scrapy Pipeline Object for Links, Results, Team, Individual"""
    
    def __init__(self):
        self.files = {}
        self.exporters = {}
    
    def create_file(self, file, _dir): 
        # if the file doesn't exist create it 
        if file not in self.files:
            self.files[file] = open(os.path.join(_dir, file + '.csv'), 'wb')
            self.exporters[file] = CsvItemExporter(self.files[file])
            self.exporters[file].start_exporting()
    
    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]
 
    def process_item(self, item, spider):
        # Define what item type it is 
        file = type(item).__name__.replace("item_", "").lower()
        if "link" in file: 
            _dir = "Links" 
        else: 
            _dir = "Data"
        
        self.create_file(file, _dir)
        
        # Export 
        self.exporters[file].export_item(item)
        
        return item
