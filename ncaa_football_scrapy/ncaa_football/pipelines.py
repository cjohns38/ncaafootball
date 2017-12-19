# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from scrapy.exporters import CsvItemExporter

class Pipeline(object):
    """Scrapy Pipeline Object"""
    
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
