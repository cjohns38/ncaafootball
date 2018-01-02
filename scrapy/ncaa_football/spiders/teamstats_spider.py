import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class StatsSpider(scrapy.Spider): 
    name = "teamstats"
    regex = '.*\/stats\?id\=\d+\&year_stat_category_id\=\d+'
    gamebygameregex = '.*\/player\/game_by_game\?'
    xpath = "//body//div[@id='contentarea']//div[@id='stats_div']//table"
    
    def start_requests(self): 
        file_in = os.path.join("Links", 'links_teaminfo.csv') 
        if os.path.isfile(file_in):
            # Pull in the data 
            data = pd.read_csv()
            stats = data[data.key == 'stats'].drop_duplicates()
            stats.sort_values(['team'], inplace = True)
            stats_list = stats.to_dict(orient='record')
        else: 
            raise Exception("Run PeopleHistoryRosterStats Spider....") 
        # Loop through the links 
        for url in stats_list: 
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse,
                                 meta = {'team':url['team']}
                                )
    
    def parse(self, response): 
        # Year 
        year = response.selector.xpath("//body//div[@id='contentarea']//fieldset//div/" +
                 "/form[@id='change_sport_form']//select[@id='year_list']//option[@select" +
                 "ed='selected']//text()").extract()[0]
        
        # Write out the rushing stats 
        table = self.table_cleaner(html = response.body, 
                           target_table = 2, 
                           stat = 'rushing', 
                           year = year, 
                           team = response.meta['team'],
                           trim_n_rows = 1
                          )
        
        # Create dynamic items
        stat = 'rushing'
        field_list = table.columns
        DynamicItem = create_item_class(stat, field_list)
        item = DynamicItem()
        
        # yield items
        for record in table.to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item
            
        # Write out the game-by-game links 
        gamebygame = LinkExtractor(allow = self.gamebygameregex) 
        gamebygamelinks = gamebygame.extract_links(response)
        
        gamebygameItem = create_item_class('links_gamebygames', ['team', 'year', 'link'])
        gameitem = gamebygameItem()
        
        for link in gamebygamelinks: 
            gameitem['team'] = response.meta['team']
            gameitem['year'] = year
            gameitem['link'] = link.url
            yield gameitem
            
        
        
        # Get all the links on the page
        le = LinkExtractor(restrict_xpaths = (self.xpath,),
                           allow = self.regex
                          ) 
        
        links = le.extract_links(response)
        
        # Build up the output 
        for link in links: 
            yield scrapy.Request(link.url, 
                                 callback=self.parse_stats,
                                 meta = {'year':year, 'team':response.meta['team'], 'stat':link.text}
                                )
    
    def parse_stats(self, response):
        print(response.meta['stat'], response.meta['year'], response.meta['team'])
        # Parse tables 
        table = self.table_cleaner(html = response.body, 
                                   target_table = 2, 
                                   stat = response.meta['stat'], 
                                   year = response.meta['year'], 
                                   team = response.meta['team'],
                                   trim_n_rows = 3
                                  )
        # Create dynamic items
        stat = response.meta['stat'].replace(" ","").replace("/","").replace(".","")
        field_list = table.columns
        DynamicItem = create_item_class(stat, field_list)
        item = DynamicItem()
        
        # yield items
        for record in table.to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item
    
    def table_cleaner(self, html, target_table, stat, year, team, trim_n_rows = 0):
        """Read HTML string and return a table
           html : HTML string
           target_table : Target table number
           trim_n_rows : Trim X number of rows from the end of the table (enter as positive number)
        """
        # Create tables
        tables = pd.read_html(html) 
        # Subset to single table of interest 
        table = tables[target_table] 
        # NCAA kicks out unlabeled columns for some reason. Find the first instance and use it to slice
        stop_index = [1 if 'Unnamed: ' in column  else 0 for idx, column in enumerate(table.columns)].index(1)
        # Fix the column names so no spaces, /'s, or .'s 
        columnNamesFixed = {col:col.replace(" ","").replace("/","").replace(".","") for col in table.iloc[:,:stop_index].columns}
        table.rename(columns = columnNamesFixed, inplace = True)
        # Clean up table 
        table = table[:-trim_n_rows].iloc[:,:stop_index]
        # Add static variables 
        table['stat'] = stat
        table['year'] = year
        table ['team'] = team
        return table 
