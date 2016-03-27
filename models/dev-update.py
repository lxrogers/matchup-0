#!/usr/bin/python

import requests
import psycopg2
from operator import itemgetter
import db_constants

anthro_features = ("FIRST_NAME", "LAST_NAME", "PLAYER_NAME", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH")

# Create a temporary table for each separate data source, merge tables, and then drop temporary tables
# Not supposed to use %?

def create_combine_anthro_table(cursor):
    cursor.execute("""CREATE TABLE temp_combine_anthro (%s varchar(20) NOT NULL, %s varchar(40) NOT NULL, 
                        %s varchar(60), %s numeric(4,2), %s numeric(4,2), %s numeric(5,2), %s numeric(4,2), 
                        %s numeric(5,2), %s numeric(4,2), %s numeric(4,2), %s numeric(4,2));""" % anthro_features)
    return 0
    
def drop_combine_anthro_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS temp_combine_anthro')
    return 0
    
def insert_combine_anthro_table(cursor, seasonyear_str):
    requests_headers = {'user-agent': db_constants.USER_AGENT}
    combine_anthro_url = "http://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=%s" % seasonyear_str
    response = requests.get(combine_anthro_url, headers = requests_headers)
    headers = response.json()['resultSets'][0]['headers']
    anthro_feature_index = [i for i,anthro_feature in enumerate(headers) if anthro_feature in anthro_features]
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