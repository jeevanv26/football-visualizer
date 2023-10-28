-- // Highest points for team in each league 
SELECT DISTINCT ON (L.name) L.name, T.team_name,(T.wins*3+T.draws) as Points
FROM team_contains_hosts as T 
inner join leagues as L 
on T.league_id=L.league_id
ORDER BY L.name,(T.wins*3+T.draws) DESC;

-- player with most goal contributions

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

-- team with the most trophies
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

-- get team rating
select T.team_name,P.avg
from team_contains_hosts as T
inner join
(select team_id,avg(coalesce(rating,0))
from player_plays
group by team_id) as P
on T.team_id=P.team_id
where T.team_id=50;

-- get rated player from team for each position
select
T.team_name,P.name,P.position,P.rating
from team_contains_hosts as T
inner join 
(select distinct on (team_id,position)
team_id,name,rating,position
from player_plays
order by team_id,position,rating desc nulls last) as P
on T.team_id=P.team_id
where T.team_id=49;

-- get description of the team.
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
where PT.team_name='Chelsea';

-- number of trophies for a team.
select count(TR.trophy_id)
from team_contains_hosts as T
inner join
(select P.team_id,A.trophy_id
from awarded as A
inner join player_plays as P
on A.player_id=P.player_id
where P.team_id=33) as TR
on T.team_id=TR.team_id;

-- get average age of the team
select T.team_name,
avg(date_part('year',age(TO_DATE(date_of_birth, 'YYYY-MM-DD')))) AS  player_age
from team_contains_hosts as T
inner join player_plays as P
on T.team_id=P.team_id
where P.team_id=49
group by team_name;