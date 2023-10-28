import requests
import psycopg2
import random
from time import sleep

conn = psycopg2.connect(host="localhost",port="5432",dbname="football",user="postgres",password="placeholder")
conn.autocommit = True

if(conn):
   print("successfully connected")

headers = {
	"placeholder"
}
# populating match table
def populate_match_table():
	match_table = []
	odds_table = []
	date_table = []
	match_ids = []
	url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
	odds_id = 381
	league_ids = [140,135,61,78]
	for league_id in league_ids:
		querystring = {"league":league_id,"season":"2021"}
		response = requests.request("GET", url, headers=headers, params=querystring).json()
		matches = response["response"]
		for match in matches:
			match_id = match["fixture"]["id"]
			match_ids.append(match_id)
			teamOne_id = match["teams"]["home"]["id"]
			teamTwo_id = match["teams"]["away"]["id"]
			if match["teams"]["away"]["winner"]:
				winner = match["teams"]["away"]["name"]
			else:
				winner = match["teams"]["home"]["name"]
			home_score = match["goals"]["home"]
			away_score = match["goals"]["away"]
			date = match["fixture"]["date"]
			referee = match["fixture"]["referee"]
			game_round = match["league"]["round"]
			match_table.append((match_id,teamOne_id,teamTwo_id,date,odds_id,referee))
			odds_table.append((odds_id,winner, home_score,away_score))
			date_table.append((date,game_round))
			odds_id+=1

	return match_table,odds_table,date_table, match_ids

def populate_events_table(fixture_id):
	events_table = []
	has_table = []
	url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/events"
	querystring = {"fixture": fixture_id}
	response = requests.request("GET", url, headers=headers, params=querystring).json()
	events = response["response"]
	for event in events:
		time_elapsed = event["time"]["elapsed"]
		team_name = event["team"]["name"]
		player_name = event["player"]["name"]
		event_type = event["type"]
		detail = event["detail"]
		events_table.append((event_type,detail,time_elapsed,player_name,team_name))
		has_table.append((fixture_id,event_type,time_elapsed,player_name))
	
	return events_table,has_table

match_table, odds_table, date_table, match_ids = populate_match_table()

cur=conn.cursor()

def insert_into_matches(match_table):
    for match in match_table:
        cur.execute("insert into match_play (match_id,team1_id,team2_id,date_game,odds_id,referee_name) values (%s,%s,%s,%s,%s,%s)",match)

def insert_into_date(date_table):
    for date in date_table:
        cur.execute("insert into date_game (date_game,round) values(%s,%s) on conflict (date_game) do nothing",date)

def insert_into_odds(odds_table):
	print(odds_table[0])
	for odds in odds_table:
		cur.execute("insert into odds (id, match_winner, final_score_home, final_score_away) values(%s,%s,%s,%s)",odds)

def insert_into_events_and_has_table(match_ids):
	print(len(match_ids))
	for match_id in match_ids:
		events_table , has_table = populate_events_table(match_id)
		for event in events_table:
			cur.execute("insert into events (event_type, event_detail, time_elapsed, player_name, team_name) values(%s,%s,%s,%s,%s) on conflict (event_type,time_elapsed,player_name) do nothing",event)
		for has in has_table:
			cur.execute("insert into has (match_id, event_type, event_time_elapsed, event_player_name) values(%s,%s,%s,%s) on conflict (match_id,event_type,event_time_elapsed,event_player_name) do nothing",has)
		sleep(2)

	
#insert_into_events_and_has_table(match_ids)





#player_ids = [883,19088,153434,282133,17832,18791,18806,49942,151754,180866,18760,18858,19150,138417,2925,283290,19032,156428,19197,144733,18853,18833,350364,1570,2459,2418,6492, 1631,26236,2808,19345, 17676, 315604, 26303, 203040]
#coach_ids = [19,2213,587,16,90,1595,1594,21,1583,1468,8665,2408,1542,959,1347]
#for player_id in player_ids:
	#num_trophies = random.randint(0,4)
	#for i in range(0,num_trophies):
		#trophy_id = random.randint(1,11)
		#cur.execute("insert into awarded (trophy_id,player_id) values(%s,%s) on conflict (trophy_id,player_id) do nothing",(trophy_id,player_id))

#for coach_id in coach_ids:
#	num_trophies = random.randint(0,3)
	#for i in range(0,num_trophies):
	#	trophy_id = random.randint(1,11)
	#	cur.execute("insert into receives (trophy_id,coach_id) values(%s,%s) on conflict (trophy_id,coach_id) do nothing",(trophy_id,coach_id))
	
	
