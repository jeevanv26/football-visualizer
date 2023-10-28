import psycopg2
import requests
from time import sleep

conn = psycopg2.connect(host="localhost",port="5432",dbname="football",user="postgres",password="placeholder")
conn.autocommit = True

if(conn):
    print(conn)
    print("successfully connected")

cur=conn.cursor()

leagues=[]
venues=[]
teams=[]
players=[]
coaches=[]
trophies=[]

headers = {
	"placeholder"
}

def get_league_info(response):
    response=response.json()

    league_id=response['response'][0]['league']['id']
    league_name=response['response'][0]['league']['name']
    league_description="This league is played in " + response['response'][0]['country']['name']
    leagues.append([league_id,league_name,league_description])

def populate_league_list():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    querystring = {"name":"premier league","country":"england","season":"2021"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    get_league_info(response)

    querystring = {"name":"la liga","country":"spain","season":"2021"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    get_league_info(response)

    querystring = {"name":"Serie A","country":"italy","season":"2021"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    get_league_info(response)

    querystring = {"name":"Ligue 1","country":"france","season":"2021"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    get_league_info(response)


    querystring = {"name":"Bundesliga","country":"germany","season":"2022"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    get_league_info(response)


def populate_team_list_and_venue_list(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    querystring = {"league":league_id,"season":"2021"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    response=response.json()

    print(len(response['response']))
    for value in response['response']:
        team_id=value['team']['id']
        team_name=value['team']['name']
        venue_id=value['venue']['id']
        venue_capacity=value['venue']['capacity']
        venue_name=value['venue']['name']
        venue_city=value['venue']['city']

        url_2 = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
        querystring = {"league":league_id,"season":"2021","team":team_id}
        response = requests.request("GET", url_2, headers=headers, params=querystring)
        print("l-id",league_id)
        print("t-id",team_id)
        response=response.json()
        print(response)
        if(response['response']):
            print(len(response['response']))
            r=response['response']
            form=r['form']
            wins=r['fixtures']['wins']['total']
            draws=r['fixtures']['draws']['total']
            loses=r['fixtures']['loses']['total']
            goals_scored=r['goals']['for']['total']['total']
            goals_conceded=r['goals']['against']['total']['total']
            longest_winning_streak=r['biggest']['streak']['wins']
            longest_losing_streak=r['biggest']['streak']['loses']

        teams.append([team_id,team_name,league_id,venue_id,wins,draws,loses,goals_scored,goals_conceded,
            longest_winning_streak,longest_losing_streak,form])
        
        venues.append([venue_id,venue_capacity,venue_city,venue_name])


def populate_players_list(team_id,page):
    url = "https://api-football-v1.p.rapidapi.com/v3/players"
    querystring = {"team":team_id,"season":"2021","page":page}
    response = requests.request("GET", url, headers=headers, params=querystring)
    response=response.json()
    print("getting players")
    for values in response['response']:
        player_id=values['player']['id']
        player_name=values['player']['name']
        goals=values['statistics'][0]['goals']['total']
        assists=values['statistics'][0]['goals']['assists']
        position=values['statistics'][0]['games']['position']
        date_of_birth=values['player']['birth']['date']
        nationality=values['player']['nationality']
        image=values['player']['photo']
        rating=values['statistics'][0]['games']['rating']
        games_played=values['statistics'][0]['games']['appearences']
        team_id=values['statistics'][0]['team']['id']

        players.append([player_id,player_name,goals,assists,position,date_of_birth,nationality,image,rating,games_played,team_id])


def populate_coach_list(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/coachs"
    querystring = {"team":team_id}
    response = requests.request("GET", url, headers=headers, params=querystring)
    response=response.json()
    print("getting coaches")
    count=0
    for values in response['response']:
        # print(response)
        if count>0:
            break

        coach_id=values['id']
        coach_name=values['name']
        date_of_birth=values['birth']['date']
        nationality=values['nationality']

        coaches.append([coach_id,coach_name,team_id,date_of_birth,nationality])
        count+=1
    
# populate_league_list()
# print(leagues)

#populate_team_list_and_venue_list(39)
#populate_team_list_and_venue_list(140)
#populate_team_list_and_venue_list(135)
#populate_team_list_and_venue_list(61)
# populate_team_list_and_venue_list(78)

# print(len(teams))
# print(teams)
# print(len(venues))
# print(venues)

# for n in [33,34,38,39,40,41,42,44,45,46,47,48,49,50,51,52,55,63,66,71]:
#     populate_players_list(n,1)
#     sleep(1)
# print(len(players))
# print(players)
        


    
# for n in [33,34,38,39,40,41,42,44,45,46,47,48,49,50,51,52,55,63,66,71]:
#     populate_coach_list(n)
#     sleep(1)


# print(len(coaches))
# print(coaches)
        
cur.execute("select team_id from team_contains_hosts")

team_ids=cur.fetchall()

for id in team_ids:
    populate_players_list(id,3)
    sleep(2)

#print(players)

# for id in team_ids:
#     populate_coach_list(id)
#     sleep(2)

#print(len(coaches))
        
def insert_into_leagues(leagues):
    for league in leagues:
        #print(league)
        cur.execute("insert into leagues (league_id,name,description) values (%s,%s,%s)",league)

def insert_into_venues(venues):
    for venue in venues:
        cur.execute("insert into venues (id,capacity,city,venue_name) values(%s,%s,%s,%s)",venue)

def insert_into_teams(teams):
    for team in teams:
        cur.execute("insert into team_contains_hosts (team_id,team_name,league_id,venue_id,wins,draws,loses,"+
            "goals_scored,goals_against,biggest_winning_streak,biggest_losing_streak,form) values"+
            "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",team)

def insert_into_players(players):
    for player in players:
        cur.execute("insert into player_plays (player_id,name,goals,assists,position,date_of_birth,"+
            "nationality,image,rating,games_played,team_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict (player_id) do nothing",player)

def insert_into_coaches(coaches):
    for coach in coaches:
        cur.execute("insert into coach_coaches (coach_id,name,team_id,date_of_birth,nationality) values (%s,%s,%s,%s,%s) on conflict (coach_id) do nothing",coach)

#insert_into_leagues(leagues)
#insert_into_venues(venues)
#insert_into_teams(teams)
#insert_into_players(players)
#insert_into_coaches(coaches)
        
 
conn.close()