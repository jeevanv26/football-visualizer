import streamlit as st
import psycopg2
from configparser import ConfigParser


config = ConfigParser()
config.read('database.ini')


host=config.get('postgresql','host')
port=config.get('postgresql','port')
dbname=config.get('postgresql','dbname')
user=config.get('postgresql','user')

conn = psycopg2.connect(host=host,port=port,dbname=dbname,user=user)
if(conn):
    print(conn)
    print("succesfully connected")

cur=conn.cursor()
st.set_page_config(layout="wide")
tab1, tab2, tab3 = st.tabs(["Roster","Matches","More Info"])

def roster_page():
	st.title("Check Team Roster")
	team_name = st.text_input('Enter Team Name')


	if team_name:
		player_query = """select P.name,P.nationality, P.date_of_birth, P.position, P.goals, P.assists,P.rating, P.games_played, P.image
				 from player_plays P, team_contains_hosts T 
				 where P.team_id = T.team_id and T.team_name = '{}'""".format(team_name)
		cur.execute(player_query)
		player_list = cur.fetchall()
		st.header("Players")
		col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.6, 3, 2, 2, 1.5, 1, 1, 1.5, 1.5])
		col1.write("Image")
		col2.write("Name")
		col3.write("Nationality")
		col4.write("Date of Birth")
		col5.write("Position")
		col6.write("Goals")
		col7.write("Assists")
		col8.write("Rating")
		col9.write("Games Played")

		for player in player_list:
			col1.image(player[8], width = 42)
			col2.write("")
			col2.write(player[0])
			col3.write("")
			col3.write(player[1])
			col4.write("")
			col4.write(player[2])
			col5.write("")
			col5.write(player[3])
			col6.write("")
			col6.write(player[4])
			if player[5]:
				col7.write("")
				col7.write(player[5])
			else:
				col7.write("")
				col7.write(0)
			
			if player[6]:
				col8.write("")
				col8.write(player[6])
			else:
				col8.write("")
				col8.write("N/A")

			col9.write("")
			col9.write(player[7])
	
		st.write("")
		st.write("")
		st.write("")
		st.header("Coach")
		coach_query =""" select C.name,C.nationality, C.date_of_birth
						from coach_coaches C, team_contains_hosts T
						where C.team_id = T.team_id and T.team_name = '{}'""".format(team_name)
		cur.execute(coach_query)
		coach = cur.fetchall()
		c1, c2 ,c3 = st.columns(3)
		c1.write("Name")
		c2.write("Nationality")
		c3.write("Date of Birth")
		if len(coach) != 0:
			c1.write(coach[0][0])
			c2.write(coach[0][1])
			c3.write(coach[0][2])




def more_info():
	st.title("More Information")
	team_name = st.text_input('Choose Team')
	if team_name:
		query_for_id = """select T.team_id
	             	 from team_contains_hosts T
	              	where T.team_name = '{}'""".format(team_name)
		cur.execute(query_for_id) 
		improper_team_id = cur.fetchall()
		if(len(improper_team_id)!=0):
			team_id = improper_team_id[0][0]
		else:
			team_id = -1
		print(team_id)
	choices = st.radio(
        """Select the information you want to retrieve""",
        ('Player with highest rating on team', 
        'Player with most goals on team', 
        'Number of red cards and yellow cards on team during season', 
        'Player with most trophies on team'
      ))


	button =st.button("Submit")
	if button and team_name:
		if choices == 'Player with highest rating on team':
			query = """select P.name 
	 		        from (select P.team_id, MAX(P.rating) as rating
	 		        	  from player_plays P
                          group by P.team_id) as R, player_plays P
                    where P.team_id = R.team_id and P.rating = R.rating and P.team_id = '{}'""".format(team_id)
			cur.execute(query)
			players = cur.fetchall()
			if(len(players)!=0):
				st.write(players[0][0])

		elif choices == 'Player with most goals on team':
			query = """select P.name 
	 		        from (select P.team_id, MAX(P.goals) as goals
	 		        	  from player_plays P
                          group by P.team_id) as R, player_plays P
                    where P.team_id = R.team_id and P.goals = R.goals and P.team_id = '{}'""".format(team_id)
			cur.execute(query)
			players = cur.fetchall()
			if len(players) != 0:
				st.write(players[0][0])

		elif choices == 'Number of red cards and yellow cards on team during season':
			query = """select count(*), E.event_type
					   from events E, has H, team_contains_hosts T, match_play M
                       where  M.match_id = H.match_id and E.event_type = H.event_type 
                       and E.time_elapsed = H.event_time_elapsed and E.player_name = H.event_player_name
                       and (T.team_id = M.team1_id or T.team_id = M.team2_id) and T.team_id = '{}'
                       and E.event_type = 'Card'
                       group by E.event_type """.format(team_id)
			cur.execute(query)
			count = cur.fetchall()
			if len(count) != 0:
				st.write(str(count[0][0]))

		else:
			query = """select P.name, R.num_awards from
						(select  P.player_id, COUNT(P.player_id) as num_awards
						 from player_plays P, awarded A
						 where A.player_id = P.player_id and P.team_id = '{}'
						 group by P.player_id) as R, player_plays P
						 where P.player_id = R.player_id
						 order by R.num_awards desc""".format(team_id)
			cur.execute(query)
			players = cur.fetchall()
			if len(players) != 0:
				st.write(players[0][0])

			else:
				st.write("No player on the team won an award")



def match_page():
	st.title("Find Team Matches")
	team_name = st.text_input('Input Team Name')
	if team_name:
		match_query = """select D.round,T1.team_name as home , T2.team_name as away, O.final_score_home, O.final_score_away, M.referee_name, V.venue_name
						  from team_contains_hosts T1, team_contains_hosts T2, odds O, match_play M, venues V, date_game D
                          where M.team1_id = T1.team_id and M.team2_id = T2.team_id and O.id = M.odds_id and V.id = T1.venue_id and M.date_game = D.date_game
                          and (T1.team_name = '{}' or T2.team_name = '{}')""".format(team_name,team_name)
		cur.execute(match_query)
		match_list = cur.fetchall()
		st.header("Matches")
		col1, col2, col3, col4, col5,col6,col7 = st.columns([2,3, 3, 2, 2, 3, 6.5])
		col1.write("Game")
		col2.write("Home (Team1)")
		col3.write("Away (Team2)")
		col4.write("Team1 Score")
		col5.write("Team2 Score")
		col6.write("Referee")
		col7.write("Venue ")
		
		for match in match_list:
			col1.write("")
			if len(match[0]) == 16:
				col1.write(match[0][len(match[0])-1])
			else:
				col1.write(match[0][len(match[0])-2:])
			col2.write("")
			col2.write(match[1])
			col3.write("")
			col3.write(match[2])
			col4.write("")
			col4.write(match[3])
			col5.write("")
			col5.write(match[4])
			col6.write("")
			col6.write(match[5])
			col7.write("")
			col7.write(match[6])
	




with tab1:
	roster_page()

with tab2:
	match_page()


with tab3:
	more_info()
