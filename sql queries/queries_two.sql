# get player description per team
select P.name,P.nationality, P.date_of_birth, P.position, P.goals, P.assists,P.rating, P.games_played, P.image, T.team_name
from player_plays P, team_contains_hosts T
where P.team_id = T.team_id and T.team_id = 33

# highest player rating per team
select P.name
from (select P.team_id, MAX(P.rating) as rating
from player_plays P
group by P.team_id) as R, player_plays P
where P.team_id = R.team_id and P.rating = R.rating and P.team_id = 33

#player with most  goals per team
select P.name
from (select P.team_id, MAX(P.goals) as goals
from player_plays P
group by P.team_id) as R, player_plays P
where P.team_id = R.team_id and P.goals = R.goals and P.team_id = 33

# player with most trophies per team
select P.name, R.num_awards from
(select  P.player_id, COUNT(P.player_id) as num_awards
from player_plays P, awarded A
where A.player_id = P.player_id and P.team_id = 33
group by P.player_id) as R, player_plays P
where P.player_id = R.player_id
order by R.num_awards desc

# get coach description per team
select C.name,C.nationality, C.date_of_birth
from coach_coaches C, team_contains_hosts T
where C.team_id = T.team_id and T.team_id = 33

# match description per team
select D.round, T1.team_name as home , T2.team_name as away, O.final_score_home, O.final_score_away, M.referee_name, V.venue_name
from team_contains_hosts T1, team_contains_hosts T2, odds O, match_play M, venues V, date_game D
where M.team1_id = T1.team_id and M.team2_id = T2.team_id and O.id = M.odds_id and V.id = T1.venue_id and M.date_game = D.date_game
and (T1.team_id = 33 or T2.team_id = 33)

# number of red cards or yellow cards per team
select count(*), E.event_type
from events E, has H, team_contains_hosts T, match_play M
where  M.match_id = H.match_id and E.event_type = H.event_type 
and E.time_elapsed = H.event_time_elapsed and E.player_name = H.event_player_name
and (T.team_id = M.team1_id or T.team_id = M.team2_id) and T.team_id = 33
and E.event_type = 'Card'



