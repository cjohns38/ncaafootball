
import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class CoachSpider(scrapy.Spider): 
    name = "Coach"
    
    def start_requests(self): 

        # Read in data
        file_in = os.path.join("Links", "links_teaminfo.csv")
        if os.path.isfile(file_in): 
            data = pd.read_csv(file_in)
            df = data[data.key == 'people'].drop_duplicates()
            df.sort_values(['team'], inplace = True)
            _list = df.to_dict(orient='record')
        else:
            raise Exception("Run PeopleHistoryRosterStats Spider....") 

        
        for url in self._list: 
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse, 
                                 meta={'name':url['txt']}
                                )
    
    def parse(self, response):         
        # Create table 
        tables = pd.read_html(response.body)
        # Stop index
        tables[1].rename(columns={"WL%":"WL"}, inplace = True)
        stop_index = [1 if 'Unnamed: ' in column  else 0 for idx, column in enumerate(tables[1].columns)]
        if sum(stop_index) > 1: 
            stop_index = stop_index.index(1)
        else: 
            stop_index = len(tables[1].columns)
        tables[1] = tables[1][:-1].iloc[:,:stop_index].copy()   
        tables[1]['Name'] = response.meta['name']

	# Create dynamic items
        field_list = tables[1].columns
        DynamicItem = create_item_class('Coaches', field_list)
        item = DynamicItem()
        
        # yield items
        for record in tables[1].to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item
