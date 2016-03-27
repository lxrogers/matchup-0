#!/usr/bin/python

import requests
import psycopg2
from operator import itemgetter

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/601.4.4 (KHTML, like Gecko) Version/9.0.3 Safari/601.4.4'

# Connect to data base
conn_string = "host='localhost' dbname='development' user='postgres' password='steph43'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

anthro_features = ("FIRST_NAME", "LAST_NAME", "PLAYER_NAME", "HEIGHT_WO_SHOES", "HEIGHT_W_SHOES", "WEIGHT", "WINGSPAN", "STANDING_REACH", "BODY_FAT_PCT", "HAND_LENGTH", "HAND_WIDTH")

# Create a temporary table for each separate data source, merge tables, and then drop temporary tables
# Not supposed to use %?
cursor.execute('DROP TABLE IF EXISTS temp_combine_anthro')

cursor.execute('CREATE TABLE temp_combine_anthro (%s varchar(20) NOT NULL, %s varchar(40) NOT NULL, %s varchar(60), %s numeric(4,2), %s numeric(4,2), %s numeric(5,2), %s numeric(4,2), %s numeric(5,2), %s numeric(4,2), %s numeric(4,2), %s numeric(4,2));' % anthro_features)

requests_headers = {'user-agent': USER_AGENT}
combine_anthro_url = "http://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2015-16"
response = requests.get(combine_anthro_url, headers = requests_headers)
headers = response.json()['resultSets'][0]['headers']
anthro_feature_index = [i for i,anthro_feature in enumerate(headers) if anthro_feature in anthro_features]
player_anthro_stats = response.json()['resultSets'][0]['rowSet']
# Insert data in temporary postgres table

for row in player_anthro_stats:
    cursor.execute("""INSERT INTO temp_combine_anthro VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", itemgetter(*anthro_feature_index)(row))

conn.commit()