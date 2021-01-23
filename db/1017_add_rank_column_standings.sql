ALTER TABLE mhac.standings
ADD COLUMN standings_rank int;


ALTER TABLE mhac.tournamentgames
ADD COLUMN season_id UUID;

ALTER TABLE mhac.tournamentgames
ALTER COLUMN game_time type time;

ALTER TABLE mhac.tournamentgames
ALTER COLUMN game_time type time;

ALTER TABLE mhac.tournamentgames
ALTER COLUMN game_time type time;

