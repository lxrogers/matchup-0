#!/usr/bin/python

import requests
import psycopg2
from operator import itemgetter
import db_constants

ANTHRO_FEATURES = ("FIRST_NAME", "LAST_NAME", "PLAYER_NAME", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH")
PLAYER_ID_FEATURES = ("PERSON_ID", "DISPLAY_LAST_COMMA_FIRST", "DISPLAY_FIRST_LAST")
PLAYER_BACKGROUND_FEATURES = ("PERSON_ID", "BIRTHDATE", "SCHOOL", "COUNTRY", "HEIGHT", "WEIGHT", "SEASON_EXP", "POSITION")
BOX_SCORE_PER_GAME_FEATURES = [u'PLAYER_ID', u'AGE', u'GP', u'MIN', u'FGM', u'FGA', u'FG_PCT', 
    u'FG3M', u'FG3A', u'FG3_PCT', u'FTM', u'FTA', u'FT_PCT', u'OREB', u'DREB', u'AST', u'TOV', u'PTS', u'PLUS_MINUS']
LINEUP_BOX_SCORE_PER_GAME_FEATURES = [u'GROUP_NAME', u'GP', u'MIN', u'FGM', u'FGA', u'FG_PCT', 
    u'FG3M', u'FG3A', u'FG3_PCT', u'FTM', u'FTA', u'FT_PCT', u'OREB', u'DREB', u'AST', u'TOV', u'PTS', u'PLUS_MINUS']
    
# Create a temporary table for each separate data source, merge tables, and then drop temporary tables
# Not supposed to use %?

def create_player_background_table(cursor):
    cursor.execute("""
    CREATE TABLE temp_player_background (PLAYER_ID integer NOT NULL, BIRTHDATE varchar(40) NULL, SCHOOL varchar(40) NULL, 
    COUNTRY varchar(60) NULL, HEIGHT varchar(5) NULL, WEIGHT integer NULL, SEASON_EXP integer NULL, POSITION varchar(40) NULL) 
    """)
    return 0
    
def drop_player_background_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS temp_player_background')
    return 0

def insert_player_background_table(cursor, player_ids):
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    for player_id in player_ids:
        print player_id
        url = "http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID=%s&SeasonType=Regular+Season" % player_id
        response = requests.get(url, headers = requests_headers)
        headers = response.json()['resultSets'][0]['headers']
        background_feature_index = [i for i, background_feature in enumerate(headers) if background_feature in PLAYER_BACKGROUND_FEATURES]
        row = response.json()['resultSets'][0]['rowSet'][0]
        insert_row = itemgetter(*background_feature_index)(row)
        insert_row = tuple(None if x == '' else x for x in insert_row) 
        cursor.execute(cursor.mogrify("""INSERT INTO temp_player_background VALUES %s""",(insert_row,)))
    return 0
    
def update_player_background(cursor, drop = False):
    if drop:
        drop_player_background_table(cursor)
        create_player_background_table(cursor)
    cursor.execute("SELECT player_id FROM temp_player_id;")
    active_player_ids = cursor.fetchall()
    active_player_ids = [x[0] for x in active_player_ids]
    cursor.execute("SELECT player_id FROM temp_player_background;")
    curr_player_ids = cursor.fetchall()
    curr_player_ids = [x[0] for x in curr_player_ids]
    player_ids_to_add = []
    for active_player_id in active_player_ids:
        if active_player_id not in curr_player_ids:
            player_ids_to_add.append(active_player_id)
    insert_player_background_table(cursor, player_ids_to_add)
    return 0

def create_combine_anthro_table(cursor):
    cursor.execute("""CREATE TABLE temp_combine_anthro (%s varchar(20) NOT NULL, %s varchar(40) NOT NULL, 
                        %s varchar(60), %s numeric(4,2), %s numeric(4,2), %s numeric(5,2), %s numeric(4,2), 
                        %s numeric(5,2), %s numeric(4,2), %s numeric(4,2), %s numeric(4,2));""" % ANTHRO_FEATURES)
    return 0
    
def drop_combine_anthro_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS temp_combine_anthro')
    return 0
    
def insert_combine_anthro_table(cursor, seasonyear_str):
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    combine_anthro_url = "http://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=%s" % seasonyear_str
    response = requests.get(combine_anthro_url, headers = requests_headers)
    headers = response.json()['resultSets'][0]['headers']
    anthro_feature_index = [i for i,anthro_feature in enumerate(headers) if anthro_feature in ANTHRO_FEATURES]
    player_anthro_stats = response.json()['resultSets'][0]['rowSet']
    for row in player_anthro_stats:
        cursor.execute("""INSERT INTO temp_combine_anthro VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", itemgetter(*anthro_feature_index)(row))
    return 0

def update_combine_anthro_table(cursor):
    drop_combine_anthro_table(cursor)
    create_combine_anthro_table(cursor)
    for seasonyear_str in db_constants.STATSNBA_SEASONYEAR:
        insert_combine_anthro_table(cursor, seasonyear_str)
    return 0
    
def drop_active_nba_player_id_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS temp_player_id')
    return 0

def create_active_nba_player_id_table(cursor):
	cursor.execute("""
	CREATE TABLE temp_player_id (PLAYER_ID integer NOT NULL, LAST_COMMA_FIRST varchar(40) NOT NULL, 
	FIRST_LAST varchar (40) NOT NULL)
	""")
	return 0

def insert_active_nba_player_id_table(cursor):
    player_id_url = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16"
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    response = requests.get(player_id_url, headers = requests_headers)
    player_id_data = response.json()['resultSets'][0]['rowSet']
    headers = response.json()['resultSets'][0]['headers']
    player_id_feature_index = [i for i, player_id_feature in enumerate(headers) if player_id_feature in PLAYER_ID_FEATURES]
    player_ids = []
    for row in player_id_data:
        cursor.execute("""INSERT INTO temp_player_id VALUES (%s, %s, %s)""", itemgetter(*player_id_feature_index)(row))
        player_ids.append(row[0])
    return player_ids # return list of IDs

def update_active_nba_player_id_table(cursor):
    drop_active_nba_player_id_table(cursor)
    create_active_nba_player_id_table(cursor)
    insert_active_nba_player_id_table(cursor)
    return 0

# Box score - get season box score once and then update each day
# Get initial table and then update by adding each day to season totals

def drop_player_data(cursor):
    cursor.execute('DROP TABLE IF EXISTS player_data')
    return 0
    
def create_player_data(cursor):
    cursor.execute("""
    CREATE TABLE player_data (player_id integer NOT NULL, first_last varchar (40) NOT NULL,
    height varchar(5) NULL, weight integer NULL, season_exp integer NULL, position varchar(40) NULL, height_w_shoes numeric(4,2),
    standing_reach numeric(5,2), age integer NULL, gp integer NULL,
    min numeric(3,1) NULL, fgm numeric(3,1) NULL, fga numeric(3,1) NULL, fg_pct numeric(4,3) NULL, fg3m numeric (3,1) NULL, 
    fg3a numeric(3,1) NULL, fg3_pct numeric(4,3) NULL, ftm numeric(3,1) NULL, fta numeric(3,1) NULL , ft_pct numeric(4,3) NULL, 
    oreb numeric(3,1) NULL, dreb numeric(3,1) NULL, ast numeric(3,1) NULL, tov numeric(2,1) NULL, pts numeric(3,1) NULL, 
    plus_minus numeric(3,1))
    """)
    return 0

def insert_player_data(cursor):
    cursor.execute("""
    INSERT INTO player_data 
    SELECT id.player_id, id.first_last, 
    background.height, background.weight, background.season_exp, background.position,
    anthro.height_w_shoes, anthro.standing_reach, 
    bs.age, bs.gp, bs.min, bs.fgm, bs.fga, bs.fg_pct, bs.fg3m, bs.fg3a, bs.fg3_pct,
    bs.ftm, bs.fta, bs.ft_pct, bs.oreb, bs.dreb, bs.ast, bs.tov, bs.pts, bs.plus_minus
    FROM 
    temp_player_id id 
    LEFT JOIN
    temp_player_background background
    ON id.player_id = background.player_id
    LEFT JOIN
    temp_combine_anthro anthro
    ON id.first_last = anthro.player_name
    LEFT JOIN
    player_traditional_stats bs
    ON id.player_id = bs.player_id
    """)
    return 0

def update_player_data(cursor):
    drop_player_data(cursor)
    create_player_data(cursor)
    insert_player_data(cursor)
    return 0
    
def drop_player_traditional_stats(cursor):
    cursor.execute('DROP TABLE IF EXISTS player_traditional_stats')
    return 0

def create_player_traditional_stats(cursor):
    cursor.execute("""
    CREATE TABLE player_traditional_stats (player_id integer NOT NULL, age integer NOT NULL, gp integer NOT NULL,
    min numeric(3,1) NULL, fgm numeric(3,1) NULL, fga numeric(3,1) NULL, fg_pct numeric(4,3) NULL, fg3m numeric (3,1) NULL, 
    fg3a numeric(3,1) NULL, fg3_pct numeric(4,3) NULL, ftm numeric(3,1) NULL, fta numeric(3,1) NULL , ft_pct numeric(4,3) NULL, 
    oreb numeric(3,1) NULL, dreb numeric(3,1) NULL, ast numeric(3,1) NULL, tov numeric(2,1) NULL, pts numeric(3,1) NULL, 
    plus_minus numeric(3,1))
    """)
    return 0
    
def insert_box_score_per_game(cursor):
    # There's a parameter for LastN games!!!!
    stats_url_per_game = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
    #stats_url_total = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
    # individual percentage and lineup percentage - return individual + lineup stat 
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    response = requests.get(stats_url_per_game, headers = requests_headers)
    headers = response.json()['resultSets'][0]['headers']
    box_score_data = response.json()['resultSets'][0]['rowSet']
    box_score_per_game_feature_index = [i for i, box_score_feature in enumerate(headers) if box_score_feature in BOX_SCORE_PER_GAME_FEATURES]
    for row in box_score_data:
        insert_string = ("""INSERT INTO player_traditional_stats VALUES (%s)""" % ",".join(str(x) for x in itemgetter(*box_score_per_game_feature_index)(row)))
        cursor.execute(insert_string)
    return 0

def update_player_traditional_stats(cursor):
    drop_player_traditional_stats(cursor)
    create_player_traditional_stats(cursor)
    insert_box_score_per_game(cursor)
    return 0

def drop_lineup_traditional_stats(cursor):
    cursor.execute('DROP TABLE IF EXISTS lineup_traditional_stats')
    return 0

def create_lineup_traditional_stats(cursor):
    cursor.execute("""
    CREATE TABLE lineup_traditional_stats (group_name varchar(200) NOT NULL, team_id integer NOT NULL, gp integer NOT NULL,
    min numeric(3,1) NULL, fgm numeric(3,1) NULL, fga numeric(3,1) NULL, fg_pct numeric(4,3) NULL, fg3m numeric (3,1) NULL, 
    fg3a numeric(3,1) NULL, fg3_pct numeric(4,3) NULL, ftm numeric(3,1) NULL, fta numeric(3,1) NULL , ft_pct numeric(4,3) NULL, 
    oreb numeric(3,1) NULL, dreb numeric(3,1) NULL, ast numeric(3,1) NULL, tov numeric(2,1) NULL, pts numeric(3,1) NULL, 
    plus_minus numeric(3,1))
    """)
    return 0    

def insert_lineup_traditional_stats(cursor):
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    cursor.execute("SELECT team_id FROM team_overview;")
    team_ids = [x[0] for x in cursor.fetchall()]
    for team_id in team_ids:
        print team_id
        team_lineup_url = "http://stats.nba.com/stats/teamdashlineups?DateFrom=&DateTo=&GameID=&GameSegment=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=%s&VsConference=&VsDivision=" % team_id
        while True:
            try:
                response = requests.get(team_lineup_url, headers = requests_headers)
            except ValueError:
                print 'Decoding JSON has failed'
                continue
            break
        headers = response.json()['resultSets'][1]['headers']
        box_score_data = response.json()['resultSets'][1]['rowSet']
        lineup_box_score_feature_index = [i for i, box_score_feature in enumerate(headers) if box_score_feature in LINEUP_BOX_SCORE_PER_GAME_FEATURES]
        for row in box_score_data:
            #print headers
            #print row
            data = list(itemgetter(*lineup_box_score_feature_index)(row))
            data.insert(1, team_id)
            data = tuple(data)
            #print LINEUP_BOX_SCORE_PER_GAME_FEATURES
            #print data
            cursor.execute(cursor.mogrify("""INSERT INTO lineup_traditional_stats VALUES %s""", (data,)))
    return 0
'''
requests_headers = {'user-agent': db_constants.USER_AGENT}
cursor.execute("SELECT team_id FROM team_overview;")
team_ids = [x[0] for x in cursor.fetchall()]
for team_id in team_ids:
    team_lineup_url = "http://stats.nba.com/stats/teamdashlineups?DateFrom=&DateTo=&GameID=&GameSegment=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PaceAdjust=N&PerMode=PerGame&Period=0&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&TeamID=%s&VsConference=&VsDivision=" % team_id
    response = requests.get(team_lineup_url, headers = requests_headers)
    headers = response.json()['resultSets'][1]['headers']
    box_score_data = response.json()['resultSets'][1]['rowSet']
    lineup_box_score_feature_index = [i for i, box_score_feature in enumerate(headers) if box_score_feature in LINEUP_BOX_SCORE_PER_GAME_FEATURES]
    for row in box_score_data:
        data = tuple(itemgetter(*lineup_box_score_feature_index)(row))
        cursor.execute(cursor.mogrify("""INSERT INTO lineup_traditional_stats VALUES %s""", (data,)))
'''        
def update_lineup_traditional_stats(cursor):
    drop_lineup_traditional_stats(cursor)
    create_lineup_traditional_stats(cursor)
    insert_lineup_traditional_stats(cursor)
    return 0

def drop_team_overview(cursor):
    cursor.execute("DROP TABLE IF EXISTS team_overview")
    return 0
    
def create_team_overview(cursor):
    cursor.execute("CREATE TABLE team_overview (team_id integer NOT NULL, team_name varchar(40) NOT NULL)")
    return 0

def insert_team_overview(cursor):
    team_url = "http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision="
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    response = requests.get(team_url, headers = requests_headers)
    headers = response.json()['resultSets'][0]['headers']
    team_data = response.json()['resultSets'][0]['rowSet']
    for row in team_data:
        data = tuple(itemgetter(0,1)(row)) 
        cursor.execute("INSERT INTO team_overview VALUES %s", (data,))
    return 0

def update_team_overview(cursor):
    drop_team_overview(cursor)
    create_team_overview(cursor)
    insert_team_overview(cursor)
    
# Don't drop lineup_traditional_stats
# Don't drop player_background for now (regular season over so no need for updating)
def main():
    # Connect to data base
    conn_string = "host='localhost' dbname='development' user='postgres' password='steph43'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print "Updating player data"
    update_active_nba_player_id_table(cursor)
    print "Active NBA player completed"
    update_player_background(cursor)
    print "Player background completed"
    update_combine_anthro_table(cursor)
    update_player_traditional_stats(cursor)
    update_player_data(cursor)
    drop_active_nba_player_id_table(cursor)
    #drop_player_background_table(cursor)
    drop_combine_anthro_table(cursor)
    drop_player_traditional_stats(cursor)
    print "Updating lineup data"
    update_team_overview(cursor)
    update_lineup_traditional_stats(cursor)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

'''
conn_string = "host='localhost' dbname='development' user='postgres' password='steph43'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
create_player_data(cursor)
insert_player_data(cursor)
'''

'''
    stats_url = "http://stats.nba.com/stats/leaguedashlineups?Conference=&DateFrom=&DateTo=&Division=&GameID=&GameSegment=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&TeamID=0&VsConference=&VsDivision="
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    response = requests.get(stats_url, headers = requests_headers)
    headers = response.json()['resultSets'][0]['headers']
    box_score_data = response.json()['resultSets'][0]['rowSet']
    lineup_box_score_feature_index = [i for i, box_score_feature in enumerate(headers) if box_score_feature in LINEUP_BOX_SCORE_PER_GAME_FEATURES]
    for row in box_score_data:
        data = tuple(itemgetter(*lineup_box_score_feature_index)(row))
        cursor.execute(cursor.mogrify("""INSERT INTO lineup_traditional_stats VALUES %s""", (data,)))
'''