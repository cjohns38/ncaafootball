import datetime, re
import pandas as pd

def createvariables(data):
    """Create Opponent, Home, Win/Loss, Overtime, and Scores
    
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
            opponent = data['Opponent'].split("@")[0].strip()
            home = 0
        else: 
            opponent = data['Opponent'].replace("@","").strip()
            home = 0
    else: 
        opponent = data['Opponent']
        home = 1
    
    
    # Win/Loss
    WinLoss = re.search(regexs['WL'], data['Result']).group()
    
    # Overtime 
    Overtime = 0
    re_ot = re.search(regexs['OT'][0], data['Result'])
    if re_ot:
        Overtime = re.search(regexs['OT'][1], re_ot.group()).group()
        
    # Team Score
    team_score = None
    re_team = re.search(regexs['team'][0], data['Result'])
    if re_team:
        team_score = re.search(regexs['OT'][1], re_team.group()).group()
        
    # Opponent Score
    opponent_score = None
    re_opponent = re.search(regexs['opponent_score'][0], data['Result'])
    if re_opponent:
        opponent_score = re.search(regexs['OT'][1], re_opponent.group()).group()
        
    return pd.Series([opponent, home, WinLoss, Overtime, team_score, opponent_score])    


def yrRecode(data): 
    yr = {'Fr':0, 'So':1, 'Jr':2, 'Sr':3}
    return yr[data]


def teamhistory(team, year, duration, history): 
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
    """ Fix time of possession"""
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
    """ Remove slashes from some of the variables"""
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

def previous_yrs(team, year, game, cols, final, debug = False): 
    cols = ['Team', 'year_y', 'count'] + cols
    out = []
    if game != 1: 
        y = final[cols][(final['Team'] == team) & 
                        (final['year_y'] == year) & 
                        (final['count'] <= game)
                       ]

        out.append(y)
    if game <= 3:
        x = final[cols][(final['Team'] == team) & 
                        (final['year_y'] == year - 1)
                       ]
        
        out.append(x)

    if debug == False: 
        mean = pd.concat(out).mean().to_frame().T.to_dict(orient='record')[0]
        mean2 = [mean[var]  for var in cols[3:]]
        return pd.Series(mean2)
    elif debug == True: 
        mean = pd.concat(out)
        return mean



def opponent(data, opponentNameVar):
    regex = '[\w\s]+\.?\s\@\s\w+'

    # Opponent 
    if '@' in data[opponentNameVar]: 
        search = re.search(regex, data[opponentNameVar]) 
        if search: 
            opponent = data[opponentNameVar].split("@")[0].strip()
        else: 
            opponent = data[opponentNameVar].replace("@","").strip()
    else: 
        opponent = data[opponentNameVar]
    return opponent.strip()

def opp(team, date, year, cols, final, debug = False):
    """ Calculate the game-by-game stats for the opponents"""
    game = final[(final['Team'] == team) &  (final['Date'] == date) ]['count'].values[0]
    return previous_yrs(team = team, 
                        year = year, 
                        game = game, 
                        cols = cols, 
                        final = final,
                        debug = False
                       )


def create_variables(data):
    """Create Opponent, Home, Win/Loss, Overtime, and Scores
    
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
