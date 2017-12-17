import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import item_TeamInfoLinks, item_Results, item_TeamStats, item_IndividualLeaders 


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
        links = pd.read_csv(os.path.join("Links", "TeamLinks.csv"))
        links = links.to_dict(orient='record')
        
        for link in links: 
            yield Request(url=link['Link'], 
                          callback=self.parse,
                          meta= {'REDIRECT_ENABLED': True, 'year':link['Year']}
                         )
    
    def parse(self, response): 
        # Extract Team Name
        team = response.selector.xpath("//body//div//fieldset//legend//a/text()").extract()[0]
        
        # Get all the links on the page
        le = LinkExtractor() 
        links = le.extract_links(response)
                
        # Extract the links pass it to the pipeline for saving
        linksOut = []
        for link in links: 
            for k, pattern in self.patterns.items():
                if re.search(pattern, link.url) != None: 
                    yield item_TeamInfoLinks({'team':team, 
                                              'link':link.url, 
                                              'txt':link.text, 
                                              'key':k, 
                                              'year':response.meta['year']
                                             })
        
        # Find all the tables 
        tables = pd.read_html(response.body)
        
        # Create a results table
        tables[1].rename(columns=tables[1].iloc[1], inplace = True)
        tables[1].drop([0,1], inplace = True)
        tables[1]['Team'] = team
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        for record in tables[1].to_dict(orient='record'):
            yield item_Results(record)
                
        # Team stats 
        tables[2].rename(columns=tables[2].iloc[1], inplace = True)
        tables[2].drop([0,1], inplace = True)
        tables[2]['Team'] = team
        tables[2]['Year'] = response.meta['year']
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        for record in tables[2][:-1].to_dict(orient='record'):
            yield item_TeamStats(record)
                
        # Individual stats
        tables[3].rename(columns=tables[3].iloc[1], inplace = True)
        tables[3].drop([0,1], inplace = True)
        tables[3]['Team'] = team
        tables[3]['Year'] = response.meta['year']
        
        # Convert to table to a list, use dict to create scrapy item, send item to pipeline 
        for record in tables[3][:-1].to_dict(orient='record'):
            yield item_IndividualLeaders(record)
            
