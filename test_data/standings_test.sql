SELECT * FROM mhac.standings WHERE season_id IN (SELECT id FROM mhac.seasons where archive is null);

BEGIN TRANSACTION;
UPDATE mhac.standings
SET wins = floor(random() * 10)::int, losses = floor(random() * 10 + 1)::int
WHERE season_id IN (SELECT id FROM mhac.seasons where archive is null);
--COMMIT

BEGIN TRANSACTION;
UPDATE mhac.standings
SET games_played = wins + losses, win_percentage = CASE WHEN wins <> 0 THEN (wins/(wins + losses)::decimal) ELSE 0.000 END
WHERE season_id IN (SELECT id FROM mhac.seasons where archive is null);

UPDATE mhac.standings                                                                                                                                       
SET standings_rank = rn
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY standings.season_id ORDER BY win_percentage desc) as rn, standings.season_id, standings.team_id FROM mhac.standings
INNER JOIN mhac.season_teams_with_names 
    ON standings.team_id = season_teams_with_names.id WHERE archive is null) as r
WHERE standings.season_id = r.season_id 
AND standings.team_id = r.team_id;
