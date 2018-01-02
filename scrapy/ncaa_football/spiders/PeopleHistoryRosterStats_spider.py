import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor 
from ncaa_football.items import create_item_class


class PeopleHistoryRosterStats(scrapy.Spider): 
    name = "PeopleHistoryRosterStats"
    
    # Settings 
    custom_settings = {'DOWNLOAD_DELAY': '.75'}
        
    # Regex patterns 
    patterns = {'people' : ".*/\d+\?sport_code\=MFB",
                'history' : ".*\/teams\/history\/MFB\/\d+",
                'roster' : ".*\/team\/\d+\/roster\/\d+",
                'stats' : ".*\/team\/\d+\/stats\/\d+",
               }
    
    def start_requests(self): 
        """Read in TeamLinks and start crawling""" 
        file_in = os.path.join("Links", "links_team.csv")
        if os.path.isfile(file_in): 
            links = pd.read_csv(file_in)
            links = links.to_dict(orient='record')
        
            for link in links: 
                yield Request(url=link['Link'], 
                              callback=self.parse,
                              meta= {'year':link['Year']}
                             )
        else: 
            raise Exception("Run teamlinks spider...")
    
    def parse(self, response): 
        # Extract Team Name
        team = response.selector.xpath("//body//div//fieldset//legend//a/text()").extract()[0]
        
        # Get all the links on the page
        le = LinkExtractor() 
        links = le.extract_links(response)
                
        # Extract the links pass it to the pipeline for saving
        field_list0 = ['team', 'link', 'txt', 'key', 'year']
        dyn_item0 = create_item_class('links_teaminfo', field_list0)
        for link in links: 
            item0 = dyn_item0()
            for k, pattern in self.patterns.items():
                if re.search(pattern, link.url) != None: 
                    record = {'team':team, 
                              'link':link.url, 
                              'txt':link.text, 
                              'key':k, 
                              'year':response.meta['year']
                             }
                    
                    for k, v in record.items(): 
                        item0[k] = v
                    yield item0
        
        # Find all the tables 
        tables = pd.read_html(response.body)
        
        # Create a results table
        tables[1].rename(columns=tables[1].iloc[1], inplace = True)
        tables[1].drop([0,1], inplace = True)
        tables[1]['Team'] = team
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        field_list1 = tables[1].columns
        print(field_list1)
        dyn_item1 = create_item_class('results', field_list1)
        item1 = dyn_item1()
        for record in tables[1].to_dict(orient='record'):
            for k, v in record.items(): 
                item1[k] = v
            yield item1
                
        # Team stats 
        tables[2].rename(columns=tables[2].iloc[1], inplace = True)
        tables[2].drop([0,1], inplace = True)
        tables[2]['Team'] = team
        tables[2]['Year'] = response.meta['year']
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        field_list2 = tables[2].columns
        dyn_item2 = create_item_class('teamstats', field_list2)
        item2 = dyn_item2()
        for record in tables[2][:-1].to_dict(orient='record'):
            for k, v in record.items(): 
                item2[k] = v
            yield item2
                
        # Individual stats
        tables[3].rename(columns=tables[3].iloc[1], inplace = True)
        tables[3].drop([0,1], inplace = True)
        tables[3]['Team'] = team
        tables[3]['Year'] = response.meta['year']
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        field_list3 = tables[3].columns
        dyn_item3 = create_item_class('individualleaders', field_list3)
        item3 = dyn_item3()
        for record in tables[3][:-1].to_dict(orient='record'):
            for k, v in record.items(): 
                item3[k] = v
            yield item3
            
