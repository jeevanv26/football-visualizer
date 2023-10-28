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

query_res=[]
if(conn):
    print(conn)
    print("succesfully connected")

cur=conn.cursor()

cur.execute("select name from Leagues")
league_rows=cur.fetchall()
league=[]
for lr in league_rows:
    league.append(lr[0])



st.title("Teams")

col1,col2=st.columns(2)

with col1:
    selected_league=st.selectbox("Select a league",league)
    print(selected_league)
    if selected_league:
        cur.execute("""
        select * 
        from team_contains_hosts T
        inner join leagues L
        on L.league_id=T.league_id
        where L.name='{}'
        order by T.team_name
        """.format(selected_league))
        team_rows=cur.fetchall()

    teams=[]
    for tr in team_rows:
        teams.append(tr[1])

    selected_team=st.selectbox("Select a Team",teams)
    print(selected_team)


with col2:
    option = st.radio(
        """Select the information you want to retrieve""",
        ('Get the rating of the team', 
        'Get Team Descripton', 
        'Highest rated player in each position',
        'Average age of the team'
        ))
    print(option)
    on_clicked=st.button("Submit")

    if on_clicked:
        if option == "Get the rating of the team":
            cur.execute("""
            select T.team_name,P.avg
            from team_contains_hosts as T
            inner join
            (select team_id,avg(coalesce(rating,0))
            from player_plays
            where rating is not null
            group by team_id) as P
            on T.team_id=P.team_id
            where T.team_name='{}'
            """.format(selected_team))
            res=cur.fetchall()
            print(res)
            for r in res:
                st.write("Team: {}  Rating: {:.2f}".format(r[0],r[1]))
        
        elif option == "Get Team Descripton":
            description_list=[]
            cur.execute("""
            select distinct on(PT.team_name)
            PT.team_name,PT.wins,PT.loses,PT.draws,PT.goals_scored,PT.goals_against,V.venue_name,V.city,V.capacity,PT.form,PT.biggest_winning_streak,PT.biggest_losing_streak
            from
            venues as V
            inner join
            (select *
            from team_contains_hosts as T
            inner join
            (select *
            from player_plays) as P
            on T.team_id=P.team_id) as PT
            on V.id=PT.venue_id
            where PT.team_name='{}';
            """.format(selected_team))
            res=cur.fetchall()
            for r in res:
                for value in r:
                    description_list.append(value)
            print("Selected",selected_team)
            cur.execute("""
            select T.team_name,count(TR.trophy_id)
            from team_contains_hosts as T
            inner join
            (select P.team_id,A.trophy_id
            from awarded as A
            inner join player_plays as P
            on A.player_id=P.player_id) as TR
            on T.team_id=TR.team_id
            where T.team_name='{}'
            group by T.team_name;
            """.format(selected_team))
            res=cur.fetchall()
            print("Trophies",res)
            for r in res:
                for value in r:
                    description_list.append(value)

            print(description_list)
            print(len(description_list))
            
            description="""{} has won {} drew {} and lost {} games during the season they scored {} goals and conceded {} goals
            Their home ground is named {} which is location in {} having capacity of {}.
            {} has had the longest winning streak of {} and losing streak of {} with their match form looking like {}.
            """.format(description_list[0],description_list[1],description_list[2],description_list[3],description_list[4],description_list[5],description_list[6],
                    description_list[7],description_list[8],description_list[0],description_list[10],description_list[11],description_list[9]) 
        
            if len(description_list)==14:
                description+="""Also , {} have won {} Trophies""".format(description_list[12],description_list[13])
            
            st.write(description)


        elif option == "Highest rated player in each position":
            cur.execute("""
            select
            T.team_name,P.name,P.position,P.rating
            from team_contains_hosts as T
            inner join 
            (select distinct on (team_id,position)
            team_id,name,rating,position
            from player_plays
            order by team_id,position,rating desc nulls last) as P
            on T.team_id=P.team_id
            where T.team_name='{}';
            """.format(selected_team))
            res=cur.fetchall()
            print(res)
            for r in res:
                st.write("Player Name: {} Position: {} Rating of the Player:{:.1f}".format(r[1],r[2],r[3]))
        
        elif option =="Average age of the team":
            cur.execute("""
            select T.team_name,
            avg(date_part('year',age(TO_DATE(date_of_birth, 'YYYY-MM-DD')))) AS  player_age
            from team_contains_hosts as T
            inner join player_plays as P
            on T.team_id=P.team_id
            where T.team_name='{}'
            group by team_name;
            """.format(selected_team))
            res=cur.fetchall()
            for r in res:
                st.write("Average age of {} is {:.1f}".format(r[0],r[1]))

