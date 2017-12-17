import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import item_history

class HistorySpider(scrapy.Spider): 
    name = "History"
    file_in = 'teaminfolinks.csv'
    
    # Read in data
    data = pd.read_csv(os.path.join("Links", file_in))
    df = data[data.key == 'history'].drop_duplicates()
    df.sort_values(['team'], inplace = True)
    _list = df.to_dict(orient='record')
    
    def start_requests(self): 
        
        for url in self._list:
 
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse, 
                                 meta={'team':url['team']}
                                )
    
    def parse(self, response):         
        # Create tables 
        tables = pd.read_html(response.body)
        tables[0]['Team'] = response.meta['team']
        tables[0].rename(columns={"WL%":"WL", "Head Coaches":"HeadCoaches"}, inplace = True)
        
        for record in tables[0][:-1].to_dict(orient='record'): 
            yield item_history(record)
