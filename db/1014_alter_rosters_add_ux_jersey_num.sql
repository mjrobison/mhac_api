
ALTER TABLE mhac.team_rosters
    ADD CONSTRAINT ux_season_team_player_id UNIQUE (season_team_id, player_id);

ALTER TABLE mhac.team_rosters
ADD COLUMN jersey_number int;