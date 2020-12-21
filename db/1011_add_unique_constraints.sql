CREATE UNIQUE INDEX team_roster 
ON mhac.team_rosters (season_team_id, player_id);

-- CREATE UNIQUE INDEX team_roster 
-- ON mhac.team_rosters (first_name, last_name, birth_date, person_type);