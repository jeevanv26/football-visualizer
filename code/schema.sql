drop table if exists League cascade;
drop table if exists Venue cascade;
drop table if exists Team_Contains_Hosts cascade;
drop table if exists Player_plays cascade;
drop table if exists Coach_coaches cascade;
drop table if exists Trophy cascade;
drop table if exists awarded cascade;
drop table if exists receives cascade;
drop table if exists Odds cascade;
drop table if exists Date_Game cascade;
drop table if exists Match_play cascade;
drop table if exists Events cascade;
drop table if exists has cascade;

create table League(
league_id integer primary key,
name varchar(20) not null,
description varchar(100) not null
);

create table Venue(
id integer primary key,
capacity integer not null,
city varchar(50) not null,
name varchar(50) not null
);

create table Team_Contains_Hosts(
team_id integer primary key,
name varchar(100) not null,
league_id integer not null,
wins integer not null,
loses integer not null,
draws integer not null,
venue_id integer not null,
goals_scored integer not null, 
goals_against integer not null,
biggest_winning_streak integer not null,
biggest_losing_streak integer not null,
form varchar(50) not null,
foreign key(league_id) references League(league_id),
foreign key(venue_id) references Venue(id)
);

create table Player_plays(
player_id integer primary key,
name varchar(100) ,
goals integer,
assists integer,
position varchar(20),
date_of_birth varchar(50),
nationality varchar(50),
image varchar(100),
rating double precision,
games_played integer,
team_id integer not null,
foreign key(team_id) references Team_Contains_Hosts(team_id)
);

create table Coach_coaches(
coach_id integer primary key,
name varchar(100) not null,
team_id integer not null unique,
date_of_birth varchar(50) not null,
nationality varchar(50) not null,
foreign key(team_id) references Team_Contains_Hosts(team_id)
);

create table Trophy(
id integer primary key,
name varchar(100) not null
);

create table awarded(
trophy_id integer,
player_id integer,
primary key(trophy_id, player_id),
foreign key (trophy_id) references Trophy( id),
foreign key(player_id) references Player_plays(player_id)
);

create table receives(
trophy_id integer,
coach_id integer,
primary key(trophy_id, coach_id),
foreign key (trophy_id) references Trophy(id),
foreign key (coach_id) references Coach_coaches(coach_id) 
);

create table Odds(
id integer primary key,
match_winner varchar(50),
final_score_home integer not null, 
final_score_away integer not null
);

create table Date_Game(
date_game varchar(50) primary key,
round varchar(50) not null
);

create table Match_play(
match_id integer primary key,
team1_id integer not null,
team2_id integer not null, 
date_game varchar(50) not null,
odds_id integer not null,
referee_name varchar(50) not null,
foreign key (team1_id) references Team_Contains_Hosts(team_id),
foreign key (team2_id) references Team_Contains_Hosts(team_id),
foreign key (odds_id) references Odds(id),
foreign key (date_game) references Date_Game(date_game)
);

create table Events(
event_type varchar(50),
event_detail varchar(50),
time_elapsed varchar(50),
player_name varchar(50),
team_name varchar(50),
primary key(event_type,time_elapsed,player_name)
);

create table has(
match_id integer,
event_type varchar(50),
event_time_elapsed varchar(50),
event_player_name varchar(50),
primary key(match_id,event_type,event_time_elapsed,event_player_name),
foreign key(event_type,event_time_elapsed,event_player_name) references Events(event_type,time_elapsed,player_name),
foreign key(match_id) references Match_play(match_id)
);