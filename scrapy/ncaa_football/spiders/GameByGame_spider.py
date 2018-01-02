import scrapy, re, urllib, os
import pandas as pd
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ncaa_football.items import create_item_class

class GameByGame(scrapy.Spider): 
    name = "GameByGame"
    regex = 'http\:\/\/stats\.ncaa\.org\/player\/index\?id\=\d+\&org_id\=\d+\&stats_player_seq\=\-\d+\&year_stat_category_id\=\d+'
    
    def start_requests(self): 
        file_in = os.path.join("Links", 'links_gamebygames.csv')
        if os.path.isfile(file_in):
            # Pull in the data 
            data = pd.read_csv(file_in)
            _list = data.to_dict(orient='record')
        else: 
            raise Exception("Run teamstats spider")
        
        # Loop through the links 
        for url in _list: 
            print(url['link'])
            yield scrapy.Request(url=url['link'], 
                                 callback=self.parse,
                                 meta = {'team':url['team'], 
                                         'year' :url['year'],
                                        }
                                )
    
    def parse(self, response): 
            
        # Get all the links on the page
        le = LinkExtractor(allow = self.regex) 
        links = le.extract_links(response)
        
        # Build up the output 
        for link in links: 
            stat = link.text.replace(" ", "").replace("/", "").replace(".", "")
            yield scrapy.Request(url = link.url, 
                                 callback = self.parse_data, 
                                 meta = {'team': response.meta['team'], 
                                         'year': response.meta['year'],
                                         'stat': stat
                                        }
                                )
            
            
    def parse_data(self, response): 
        
        # Create tables 
        tables = pd.read_html(response.body)
        
        # Create yearly table 
        yearly = self.yearlystats(tables[2])
        
        # Create dynamic items
        stat = response.meta['stat'].replace(" ","").replace("/","").replace(".","").replace("-", "")
        field_list = yearly.columns
        DynamicItem = create_item_class("yearly_" + stat, field_list)
        item = DynamicItem()
        
        # yield items
        for record in yearly.to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item
        
        # Create game-by-game table 
        gamebygame = self.gamestats(tables[4], response.meta['team'])
        
        # Create dynamic items
        field_list = gamebygame.columns
        DynamicItem = create_item_class('gamebygame_' + stat, field_list)
        item = DynamicItem()
        
        # yield items
        for record in gamebygame.to_dict(orient='record'):
            for k, v in record.items(): 
                item[k] = v
            yield item
        
        
    def yearlystats(self, table):
        """Clean up the yearly game-to-game stats table
            table : pandas DF you want to clean 
        """
        # Drop unneeded header row
        tmp = table.iloc[1:,]
        # Create a header row removing spaces, /'s, and x's
        tmp.columns = [x.replace(" ", "").replace("/","").replace(".","") for x in tmp.iloc[0]]
        # Drop the row used to create header row
        tmp = tmp.drop(tmp.index[0])
        # Forward fill the year for analysis later 
        tmp['Year'].fillna(method='ffill', inplace = True)
        # Create a new offense/defense variable 
        tmp['OffenseDefense'] = tmp['Team']
        # Figure out which team we are working with 
        curr_team = tmp.iloc[:1,1:3].values[0][0]
        # Create a new team variable
        tmp['Team'] = curr_team
        # In the offense defense variable, fill in the offense defense variable 
        tmp['OffenseDefense'] = tmp['OffenseDefense'].apply(lambda x: 'Offense' if x == curr_team else x)
        return tmp 
    
    def gamestats(self, table, curr_team):
        """ Clean up game stats table
            table : pandas DF you want to clean 
            curr_team : team name you want to add 
        """

        # Drop unneeded header 
        tmp = table.iloc[1:,]
        # Fix the column names by reading line 0
        tmp.columns = [x.replace(" ", "").replace("/","").replace(".","") for x in tmp.iloc[0]]
        # Drop row zero which held the header row
        tmp = tmp.drop(tmp.index[0])
        # Forward fill the dates for defensive split later 
        tmp['Date'].fillna(method='ffill', inplace = True)
        # Add in the team 
        tmp['Team'] = curr_team
        # Create an offense/defense variable
        tmp['OffenseDefense'] = tmp['Opponent']
        # If it's not a defensive total then it's offense - set that in the offensedefense variable
        tmp['OffenseDefense'] = tmp['OffenseDefense'].apply(lambda x: "Defense" if x == "Defensive Totals" else "Offense")
        # Set the defensive totals in the opponent varaible to nullls
        tmp['Opponent'] = tmp['Opponent'].apply(lambda x: None if x == "Defensive Totals" else x)
        # Forward fill the opponents in for analysis later
        tmp['Opponent'].fillna(method='ffill', inplace = True)
        # Forward fill the results in for analysis later 
        tmp['Result'].fillna(method='ffill', inplace = True)
        return tmp
        
    

