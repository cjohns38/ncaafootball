import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class HistorySpider(scrapy.Spider): 
    name = "History"

    
    def start_requests(self): 
        # Read in data
        file_in = os.path.join("Links", "links_teaminfo.csv")
        if os.path.isfile(file_in): 
            data = pd.read_csv(file_in)
            df = data[data.key == 'history'].drop_duplicates()
            df.sort_values(['team'], inplace = True)
            _list = df.to_dict(orient='record')
        else: 
            raise Exception("Run PeopleHistoryRosterStats Spider....") 
    
        
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

        # Create dynamic items
        field_list = tables[0].columns
        DynamicItem = create_item_class('History', field_list)
        item = DynamicItem()
        
        # yield items
        for record in tables[0][:-1].to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item

