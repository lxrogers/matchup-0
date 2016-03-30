#!/usr/bin/python

import requests
import psycopg2
from operator import itemgetter
import db_constants

ANTHRO_FEATURES = ("FIRST_NAME", "LAST_NAME", "PLAYER_NAME", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH")
PLAYER_ID_FEATURES = ("PERSON_ID", "DISPLAY_LAST_COMMA_FIRST", "DISPLAY_FIRST_LAST")
PLAYER_BACKGROUND_FEATURES = ("PERSON_ID", "BIRTHDATE", "SCHOOL", "COUNTRY", "HEIGHT", "WEIGHT", "SEASON_EXP")
# Create a temporary table for each separate data source, merge tables, and then drop temporary tables
# Not supposed to use %?

def create_player_background_table(cursor):
    cursor.execute("""
    CREATE TABLE temp_player_background (PLAYER_ID integer NOT NULL, BIRTHDATE varchar(40) NULL, SCHOOL varchar(40) NULL, 
    COUNTRY varchar(60) NULL, HEIGHT varchar(5) NULL, WEIGHT integer NULL, SEASON_EXP integer NULL) 
    """)
    return 0
    
def drop_player_background_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS temp_player_background')
    return 0

def insert_player_background_table(cursor, player_ids):
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    for player_id in player_ids:
        url = "http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID=%s&SeasonType=Regular+Season" % player_id
        response = requests.get(url, headers = requests_headers)
        headers = response.json()['resultSets'][0]['headers']
        background_feature_index = [i for i, background_feature in enumerate(headers) if background_feature in PLAYER_BACKGROUND_FEATURES]
        row = response.json()['resultSets'][0]['rowSet'][0]
        insert_row = itemgetter(*background_feature_index)(row)
        insert_row = tuple(None if x == '' else x for x in insert_row) 
        cursor.execute("""INSERT INTO temp_player_background VALUES (%s,%s,%s,%s,%s,%s,%s)""",insert_row)
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
def create_box_scores(cursor):
	cursor.execute("""
	CREATE TABLE temp_box_scores (PLAYER_ID integer NOT NULL, LAST_COMMA_FIRST varchar(40) NOT NULL, 
	FIRST_LAST varchar (40) NOT NULL)
	""")
	return 0
    
def main():
    # Connect to data base
    conn_string = "host='localhost' dbname='development' user='postgres' password='steph43'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print "Running"
    #drop_combine_anthro_table(cursor)
    update_combine_anthro_table(cursor)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
    