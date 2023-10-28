import streamlit as st
import psycopg2
from streamlit_extras.switch_page_button import switch_page
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

cur.execute("select * from leagues")
leagues=cur.fetchall()

st.title("Leagues")

col1,col2=st.columns(2)
with col1:
    for league in leagues:
        st.write(league[1])
        st.write("")


with col2:
    st.markdown("""

    <h4>
        Query for leagues
    </h4>
    """,unsafe_allow_html=True)


    option = st.radio(
        """Select the information you want to retrieve""",
        ('Highest points acheived by a team', 
        'Player that has the most goal contributions (goals+assists)', 
        'Team that has won most trophies'))

    print(option)
    on_clicked=st.button("Submit")

    if(on_clicked):
        if option == "Highest points acheived by a team":
            print("executing qeury 1")
            cur.execute("""SELECT DISTINCT ON (L.name) L.name, T.team_name,(T.wins*3+T.draws) as Points
            FROM team_contains_hosts as T 
            inner join leagues as L 
            on T.league_id=L.league_id
            ORDER BY L.name,(T.wins*3+T.draws) DESC;""")
            res=cur.fetchall()
            for r in res:
                st.write("League: {} Team: {} Total Points: {}".format(r[0],r[1],r[2]))
        
        elif option =="Player that has the most goal contributions (goals+assists)":
            print("executing query 2")
            cur.execute("""
            select L.name,GC.team_name,GC.name,GC.goal_contributions
            from leagues as L
            inner join (
            select distinct on (T.league_id)
            T.league_id,P.team_id,T.team_name,P.player_id,P.name,coalesce(goals,0)+coalesce(assists,0) as goal_contributions
            from team_contains_hosts as T
            inner join player_plays as P
            on T.team_id=P.team_id
            order by T.league_id,coalesce(goals,0)+coalesce(assists,0) desc ) 
            as GC
            on L.league_id=GC.league_id;
            """)
            res=cur.fetchall()
            for r in res:
                st.write("League: {} Team:{} Player:{} Goal Contributions: {}".format(r[0],r[1],r[2],r[3]))
        
        elif option == "Team that has won most trophies":
            print("executing query 3")
            cur.execute("""
            select distinct on (PLT.league_name)
            PLT.league_name,PLT.team_name,count(trophy_id)
            from awarded as A
            inner join
            (select PL.name as league_name,P.player_id,P.name as player_name,PL.team_name
            from
            player_plays as P
            inner join
            (select L.league_id,L.name,T.team_id,T.team_name
            from leagues as L
            inner join team_contains_hosts as T
            on L.league_id=T.league_id) as PL
            on P.team_id=PL.team_id) as PLT
            on A.player_id=PLT.player_id
            group by (PLT.league_name,PLT.team_name)
            order by PLT.league_name,count desc;
            """)
            res=cur.fetchall()
            for r in res:
                st.write("League: {} Team: {} Trophies won: {}".format(r[0],r[1],r[2]))

