
import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import item_coaches

class CoachSpider(scrapy.Spider): 
    name = "Coach"
    
    # Read in data
    file_in = 'teaminfolinks.csv'
    data = pd.read_csv(os.path.join("Links",file_in))
    df = data[data.key == 'people'].drop_duplicates()
    df.sort_values(['team'], inplace = True)
    _list = df.to_dict(orient='record')
    
    def start_requests(self): 
        
        for url in self._list: 
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse, 
                                 meta={'name':url['txt']}
                                )
    
    def parse(self, response):         
        # Create table 
        tables = pd.read_html(response.body)
        # Stop index
        tables[1]['Name'] = response.meta['name']
        tables[1].rename(columns={"WL%":"WL"}, inplace = True)
        stop_index = [1 if 'Unnamed: ' in column  else 0 for idx, column in enumerate(tables[1].columns)]
        if sum(stop_index) > 1: 
            stop_index = stop_index.index(1)
        else: 
            stop_index = len(tables[1].columns)
        tables[1] = tables[1][:-1].iloc[:,:stop_index]
        for record in tables[1].to_dict(orient='record'): 
            yield item_coaches(record)        
