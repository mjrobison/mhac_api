ALTER TABLE mhac.tournamentgames
ADD COLUMN season_id UUID;

ALTER TABLE mhac.tournamentgames
ALTER COLUMN game_time type time;

ALTER TABLE mhac.tournamentgames
ADD COLUMN winner_to int;

ALTER TABLE mhac.tournamentgames
ADD COLUMN loser_to int;

--Need to add few constraints
