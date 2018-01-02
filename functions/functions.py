import datetime, re
import pandas as pd

def yrRecode(data): 
    """ Returns a numeric value for Fr, So, Jr, Sr

        Keyword arguments: 

        data : Pandas ROW (series) 
    """
    yr = {'Fr':0, 'So':1, 'Jr':2, 'Sr':3}
    return yr[data]

def teamhistory(team, year, duration, history): 
    """ Calcuates wins, losses and wins/(wins+losses) 
        
        Keyword arguments: 

        team : team name 
        year : four digit year 
        duration : how many years of history to look at 
        history : history data frame 

    """
    team = team
    target_year = year
    out = []
    # Individual 
    for yr in duration: 
        target_year_min = target_year - yr
        # Wins/Losses
        wins, losses = list(history[(history.Team == team) & 
                                    (history.year <= target_year) & 
                                    (history.year >= target_year_min)][['Wins', 'Losses']].sum()
                           )
        out.extend([wins, losses, wins/(wins+losses)])
    # Max 
    wins, losses = list(history[(history.Team == team)][['Wins', 'Losses']].sum())
    out.extend([wins, losses, wins/(wins+losses)])
    return pd.Series(out)


def fixTOP(row):
    """ Standardize the time of possession so it's all hh:mm:ss time delta format 
        
        Keyword arguments: 

        row : row data 
    """
    if isinstance(row, str) == True and ":" in row: 
        _all = row.split(":")
        _min = int(_all[0]) * 60 
        _sec = int(_all[1]) 
        total_seconds = _min + _sec
    else: 
        total_seconds = int(row)
    val = "{}".format(datetime.timedelta(seconds=total_seconds))
    return pd.Series([val])



def removeSlashes(row, cols):
    """ Remove slashes from variables

        Keyword arguments: 
 
        row : row data 
        cols : cols to remove slashes from 

    """
    out = []
    for cell in cols[3:]:
        if cell == 'TOP': 
            out.append(row[cell])
        elif isinstance(row[cell], str) and '/' in row[cell]:
            tmp = row[cell].replace("/", "")
            out.append(float(tmp))
        else: 
            out.append(row[cell])
    return pd.Series(out)

def coach_history(data, year, coaches): 
    """ Create coach history  
 
        Keyword arguments: 

        data : data
        year : year of interest
        coaches : coaches dataframe 

    """

    t = []
    if isinstance(data, list) and len(data) >=1 :
        for coach in data: 
            coach_record = coaches[(coaches.coach == coach) & 
                                   (coaches.year < year)
                                  ][["coach","Wins","Losses","WL","year"]].groupby("coach").agg(['sum', 'count', 'mean'])
            coach_record.columns = [x[0] + "_" + x[1]  for x in coach_record.columns.values]
            coach_record.drop(['Wins_count', 'Wins_mean', 'Losses_count', 'Losses_mean', 'WL_sum', 'WL_count', 
                                     'year_sum', 'year_mean'], axis=1, inplace = True)
            coach_record.rename(columns = {'Wins_sum':"Coach_wins", 
                                           "Losses_sum":"Coach_losses", 
                                           "WL_mean":"Coach_WL", 
                                           "year_count":"Coach_years"
                                          },
                                inplace = True
                               )
            t.append(coach_record.to_dict(orient='record')[0])
    
        out = pd.Series(pd.DataFrame(t).mean().to_dict())
    else: 
        out = pd.Series({'Coach_wins':None, 
                         "Coach_losses":None, 
                         "Coach_WL":None, 
                         "Coach_years":None
                        })
    return out

def previous_yrs(team, year, game, cols, gamestats, debug = False): 
    """ Calculate the previous years 

        Keyword arguments: 

        team : team of interest
        year : year of interest
        cols : columns of interest 
        gamestats : gamestats dataframe 
        debug: if Debug = True then return a DF, if false return the average 

    """
    cols = ['Team', 'year', 'gamenumber'] + cols
    out = []
    if game != 1: 
        y = gamestats[cols][(gamestats['Team'] == team) & 
                        (gamestats['year'] == year) & 
                        (gamestats['gamenumber'] <= game)
                       ]

        out.append(y)
    if game <= 3:
        x = gamestats[cols][(gamestats['Team'] == team) & 
                        (gamestats['year'] == year - 1)
                       ]
        
        out.append(x)

    if debug == False: 
        mean = pd.concat(out).mean().to_frame().T.to_dict(orient='record')[0]
        mean2 = [mean[var]  for var in cols[3:]]
        return pd.Series(mean2)
    elif debug == True: 
        mean = pd.concat(out)
        return mean



def extract_name(data, varname):
    """ Extract team name from variable 
        
        Keyword arguments: 
        data : df
        varname : variable name of interest
        
    """
  
    regex = '[\w\s]+\.?\s\@\s\w+'

    # Opponent 
    if '@' in data[varname]: 
        search = re.search(regex, data[varname]) 
        if search: 
            opponent = data[varname].split("@")[0].strip()
        else: 
            opponent = data[varname].replace("@","").strip()
    else: 
        opponent = data[varname]
    return opponent.strip()

def opponent_stats(team, date, year, cols, gamestats, debug = False):
    """ Calculate the game-by-game stats for the opponents

        Keyword arguments: 

        team : team of interest
        date : date of itnerest
        year : year of interest
        cols : columns of interest 
        gamestats : gamestats dataframe 
        debug: if Debug = True then return a DF, if false return the average 

    """
    game = gamestats[(gamestats['Team'] == team) &  (gamestats['Date'] == date) ]['gamenumber'].values[0]
    return previous_yrs(team = team, 
                        year = year, 
                        game = game, 
                        cols = cols, 
                        gamestats = gamestats,
                        debug = False
                       )


def create_variables(data):
    """Create Home, Win/Loss variables 

       Keyword arguments: 

       data : target variable 
    
    """
    regexs = {'WL': "[WL]",
              'team': ["\d+\s\-", "\d+"],
              'opponent_score':["\-\s\d+", '\d+'],
              'OT':["\(\d+OT\)", "\d+"], 
              'opponent':['[\w\s]+\.?\s\@\s\w+']
             }
    
    # Opponent 
    if '@' in data['Opponent']: 
        search = re.search(regexs['opponent'][0], data['Opponent']) 
        if search: 
            home = 0
        else: 
            home = 0
    else: 
        home = 1
    
    
    # Win/Loss
    WinLoss = re.search(regexs['WL'], data['Result']).group()
    if WinLoss == 'W': 
        WinLoss = 1
    else: 
        WinLoss = 0
        
    return pd.Series([home, WinLoss])    
