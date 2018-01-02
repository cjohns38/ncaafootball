import scrapy, re, urllib, os
import pandas as pd
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class TeamSpider(scrapy.Spider): 
    name = "teamlinks"
    
    # List of years to build up URLs to crawl 
    years = [2014, 2015, 2016, 2017] 
    
    # Build list of URLs and crawl 
    start_urls = ["http://stats.ncaa.org/team/inst_team_list?academic_year={year}&conf_id=-1&division=11&sport_code=MFB".format(year = year)
            for year in years]
    
    def parse(self, response): 
        """Parse the crawled pages"""
        # Extract current year from the returned object
        curr_year = urllib.parse.parse_qs(urllib.parse.urlparse(response.url).query)['academic_year'][0]
        
        # Get all the links on the page
        le = LinkExtractor() 
        links = le.extract_links(response)
        
        # Regex pattern to find just the team links 
        team_url_pattern = "http\:\/\/stats\.ncaa\.org\/team\/\d+\/\d+"
        
        # Extract the links, put into item object, yield item object to pipeline which saves results 
        for link in links: 
            match = re.search(team_url_pattern, link.url)
            if match != None: 
		
                # Create dynamic items
                field_list = ['Link', 'Team', 'Year']
                DynamicItem = create_item_class('Links_Team', field_list)
                item = DynamicItem()
		
                # yield items
                for k, v in {'Link':link.url, 'Team':link.text, 'Year':curr_year }.items(): 
                    item[k] = v
                yield item

