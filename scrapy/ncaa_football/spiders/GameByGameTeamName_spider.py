import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class TeamNameSpider(scrapy.Spider): 
    name = "TeamNameSpider"
    
    def start_requests(self): 
        file_in = 'links_gamebygame.csv'

        # Pull in the data 
        data = pd.read_csv(os.path.join("Links", file_in))
        _list = data.to_dict(orient='record')
        
        # Loop through the links 
        for url in _list: 
            print(url['link'])
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse,
                                 meta = {'team':url['team'], 
                                         'year':url['year'],
                                        }
                                )
    
    def parse(self, response): 
        regex = "http\:\/\/stats\.ncaa\.org\/team\/\d+\/\d+"

        # Get all the links on the page
        le = LinkExtractor(allow = regex) 
        links = le.extract_links(response)
        
        # Build up the output 
        for link in links:   
            yield scrapy.Request(url = link.url, 
                                 callback = self.parse_data, 
                                 meta = {'team': link.text,}
                                )
            
            
    def parse_data(self, response): 
        
        teamName = response.xpath('//*[@id="contentarea"]/fieldset/legend/a/text()').extract_first()
        record = {'shortName': response.meta['team'], 
                  'longName':teamName
                 }
        
        # Create dynamic items
        field_list = record.keys()
        DynamicItem = create_item_class('gamebygame_teamNames', field_list)
        item = DynamicItem()
        
        # yield items
        for k, v in record.items(): 
            item[k] = v
        yield item
        
        
    

