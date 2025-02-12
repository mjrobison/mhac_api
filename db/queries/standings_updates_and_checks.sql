BEGIN TRANSACTION;

UPDATE mhac.standings
SET wins = sums.wins, losses = sums.losses, games_played = sums.games_played, win_percentage = sums.win_percentage
FROM (
SELECT 
    stwn.id AS team_id,
    t.team_name,
    levels.level_name,
    COALESCE(SUM(CASE 
        WHEN g.home_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
        WHEN g.away_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
        ELSE 0 END), 0) AS wins,
    COALESCE(SUM(CASE 
        WHEN g.home_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
        WHEN g.away_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
        ELSE 0 END), 0) AS losses,
    (COALESCE(SUM(CASE 
        WHEN g.home_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
        WHEN g.away_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
        ELSE 0 END), 0)
    + COALESCE(SUM(CASE 
        WHEN g.home_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
        WHEN g.away_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
        ELSE 0 END), 0)) AS games_played,
    CASE 
        WHEN (COALESCE(SUM(CASE 
            WHEN g.home_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
            WHEN g.away_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
            ELSE 0 END), 0)
        + COALESCE(SUM(CASE 
            WHEN g.home_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
            WHEN g.away_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
            ELSE 0 END), 0)) > 0
        THEN COALESCE(SUM(CASE 
            WHEN g.home_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
            WHEN g.away_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
            ELSE 0 END), 0)::decimal 
        / (COALESCE(SUM(CASE 
            WHEN g.home_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
            WHEN g.away_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
            ELSE 0 END), 0)
        + COALESCE(SUM(CASE 
            WHEN g.home_team_id = t.id AND g.final_home_score < g.final_away_score THEN 1
            WHEN g.away_team_id = t.id AND g.final_home_score > g.final_away_score THEN 1
            ELSE 0 END), 0))
        ELSE 0.000 END AS win_percentage
FROM mhac.teams t
INNER JOIN mhac.season_teams AS stwn 
    ON stwn.team_id = t.id
INNER JOIN mhac.seasons s 
    ON stwn.season_id = s.id
INNER JOIN mhac.levels 
    ON s.level_id = levels.id
LEFT JOIN mhac.games g 
    ON g.home_team_id = t.id OR g.away_team_id = t.id
INNER JOIN mhac.schedule
    ON g.game_id = schedule.game_id
    ANd s.id = schedule.season_id
WHERE s.archive is null
--   AND levels.level_name = '12U Boys'
GROUP BY stwn.id, t.team_name, levels.level_name
) AS sums
WHERE standings.team_id = sums.team_id;




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



BEGIN TRANSACTION;

UPDATE mhac.standings
SET wins = sums.wins, losses = sums.losses, games_played = (sums.wins + sums.losses), win_percentage = CASE WHEN sums.wins <> 0 THEN (sums.wins/(sums.wins + sums.losses)::decimal) ELSE 0.000 END
FROM (
    SELECT COALESCE(SUM(CASE WHEN games.home_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7' AND games.final_home_score > games.final_away_score THEN 1
                    WHEN games.away_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7' AND games.final_home_score < games.final_away_score THEN 1
                    END), 0) AS wins,
            COALESCE(SUM(CASE WHEN games.home_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7' AND games.final_home_score < games.final_away_score THEN 1
                    WHEN games.away_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7' AND games.final_home_score > games.final_away_score THEN 1
                    END), 0) AS losses
    FROM mhac.games 
    INNER JOIN mhac.schedule 
        ON games.game_id = schedule.game_id
    INNER JOIN mhac.seasons
        ON schedule.season_id = seasons.id
    INNER JOIN mhac.levels
        ON seasons.level_id = levels.id
    WHERE 
        (home_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7' OR away_team_id = 'a611499e-c596-4d52-8730-d4dc130235d7') 
        AND archive IS NULL AND level_name = '12U Boys'
)
WHERE standings.team_id = sums.id
;
