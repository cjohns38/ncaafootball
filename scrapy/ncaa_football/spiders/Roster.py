import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import item_roster

class rosterSpider(scrapy.Spider): 
    name = "Roster"
    file_in = 'teaminfolinks.csv'
    
    # Read in data
    data = pd.read_csv(os.path.join("Links", file_in))
    df = data[data.key == 'roster'].drop_duplicates()
    df.sort_values(['team'], inplace = True)
    _list = df.to_dict(orient='record')
    
    
    def start_requests(self): 
        
        for url in self._list: 
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse, 
                                 meta={'team':url['team']}
                                )
    
    def parse(self, response):
        # year 
        year = response.selector.xpath("//body//div[@id='contentarea']//fieldset//div/" +
                 "/form[@id='change_sport_form']//select[@id='year_list']//option[@select" +
                 "ed='selected']//text()").extract()

        # Create tables 
        tables = pd.read_html(response.body)
        tables[0].columns = tables[0].columns.droplevel(0)
        tables[0]['Year'] = year[0]
        tables[0]['Team'] = response.meta['team']

        for record in tables[0].to_dict(orient='record'): 
            yield item_roster(record)
