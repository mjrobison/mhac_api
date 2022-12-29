--ROLLBACK
BEGIN TRANSACTION;

UPDATE mhac.standings
SET wins = sums.wins, losses = sums.losses, games_played = (sums.wins + sums.losses), win_percentage = CASE WHEN sums.wins <> 0 THEN (sums.wins/(sums.wins + sums.losses)::decimal) ELSE 0.000 END
FROM (
SELECT 
    season_teams_with_names.id, season_teams_with_names.team_name, season_teams_with_names.level_name,
    COALESCE(
    (
        SELECT SUM (CASE WHEN games.home_team_id = season_teams_with_names.id AND games.final_home_score > games.final_away_score THEN 1
                WHEN games.away_team_id = season_teams_with_names.id AND games.final_home_score < games.final_away_score THEN 1
                END) AS wins

        FROM mhac.games
    ), 0
    ) AS wins,
    COALESCE(
        (
        SELECT SUM (CASE WHEN games.home_team_id = season_teams_with_names.id AND games.final_home_score < games.final_away_score THEN 1
                WHEN games.away_team_id = season_teams_with_names.id AND games.final_home_score > games.final_away_score THEN 1
                END) AS losses

        FROM mhac.games
        ), 0
    ) AS losses

FROM mhac.season_teams_with_names
WHERE archive is null
) AS sums
WHERE standings.team_id = sums.id

BEGIN TRANSACTION;



SELECT season_teams_with_names.team_name, season_teams_with_names.level_name, standings.* FROM mhac.standings INNER JOIN mhac.season_teams_with_names ON standings.team_id = season_teams_with_names.id  WHERE archive is null ORDER BY 2, standings_rank;


SELECT standings.season_id, SUM(games_played)
FROM mhac.standings 
INNER JOIN mhac.season_teams_with_names 
    ON standings.team_id = season_teams_with_names.id  
WHERE archive is null
GROUP BY standings.season_id;

SELECT standings.*, ROW_NUMBER() OVER (PARTITION BY standings.season_id ORDER BY win_percentage desc) as rn
FROM mhac.standings 
INNER JOIN mhac.season_teams_with_names 
    ON standings.team_id = season_teams_with_names.id  
WHERE archive is null
GROUP BY standings.season_id;



UPDATE mhac.standings                                                                                                                                       
SET standings_rank = rn
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY standings.season_id ORDER BY win_percentage desc) as rn, standings.season_id, standings.team_id FROM mhac.standings
INNER JOIN mhac.season_teams_with_names 
    ON standings.team_id = season_teams_with_names.id WHERE archive is null) as r
WHERE standings.season_id = r.season_id 
AND standings.team_id = r.team_id;
