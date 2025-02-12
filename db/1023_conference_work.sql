SELECT * FROM mhac.season_teams_with_names 


ALTER TABLE mhac.games ADD COLUMN away_id UUID
-- ALTER TABLE mhac.games ADD CONSTRAINT games_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES mhac.season_teams(id);
-- ALTER TABLE mhac.games ADD CONSTRAINT games_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES mhac.season_teams(id);
ALTER TABLE mhac.games DROP CONSTRAINT games_home_team_id_fkey
ALTER TABLE mhac.games DROP CONSTRAINT games_away_team_id_fkey

ROLLBACK
BEGIN TRANSACTION;
UPDATE mhac.games
SET home_id = home_team_id, away_id = away_team_id

SELECT * FROM mhac.games

UPDATE mhac.games
SET away_team_id = (SELECT teams.id FROM mhac.season_teams INNER JOIN mhac.teams ON teams.id = season_teams.team_id WHERE season_teams.id = games.away_id)

UPDATE mhac.games
SET away_team_id = (SELECT teams.id FROM mhac.season_teams INNER JOIN mhac.teams ON teams.id = season_teams.team_id WHERE season_teams.id = games.away_id)

SELECT teams.id, teams.team_name 
FROM mhac.season_teams 
INNER JOIN mhac.teams 
ON teams.id = season_teams.team_id 
WHERE season_teams.id = 'f184cc70-0d06-4b41-a64b-917b82439b2b'


SELECT * FROM mhac.games

SELECT * FROM mhac.teams

ALTER TABLE mhac.teams
ADD COLUMN conference BOOLEAN

--COMMIT
BEGIN TRANSACTION;
UPDATE mhac.teams
SET conference = False 
WHERE team_name = 'Test'



SELECT DISTINCT team_id, team_name, team_mascot, address_id, main_color, secondary_color, website, logo_color, logo_grey, slug, archive, conference
FROM mhac.season_teams_with_names 
WHERE archive is null

SELECT * FROM mhac.teams
LEFT OUTER JOIN mhac.season_teams
    ON teams.id = season_teams.team_id
LEFT OUTER JOIN mhac.seasons s 
    ON season_teams.season_id = s.id
LEFT OUTER JOIN mhac.levels l 
    ON s.level_id = l.id
WHERE team_name = 'Test'

     JOIN mhac.levels l ON s.level_id = l.id;


SELECT * FROM mhac.games where away_team_id = 'c8606307-e1c2-45c8-a446-a739e38640bf'

SELECT * FROM mhac.teams


SELECT
    schedule.id as schedule_id, 
    games.game_id as game_id,
    schedule.game_date::date as game_date,
    schedule.game_time as game_time, 
    home_team.id as home_team,
    away_team.id as away_team, 
    final_home_score, 
    final_away_score,
    -- {missing_subquery} as missing_stats,
    schedule.season_id
FROM mhac.games
INNER JOIN mhac.schedule 
    ON games.game_id = schedule.game_id
LEFT OUTER JOIN mhac.teams AS home_team
    ON games.home_team_id = home_team.id
LEFT OUTER JOIN mhac.teams AS away_team
    ON games.away_team_id = away_team.id
-- WHERE (home_team.archive is null and away_team.archive is null)
WHERE games.away_team_id = 'c8606307-e1c2-45c8-a446-a739e38640bf'
ORDER BY schedule.game_date

SELECT * FROM mhac.teams WHERE active and conference

SELECT seasons.id as season_id, 
    seasons.name, 
    seasons.start_date::date, 
    seasons.roster_submission_deadline::date, 
    seasons.tournament_start_date::date,
    sports.sport_name, 
    seasons.slug, 
    levels.level_name,
    levels.id as level_id, 
    seasons.year,
    seasons.archive
    FROM mhac.seasons 
    INNER JOIN mhac.levels 
        ON seasons.level_id = levels.id 
    INNER JOIN mhac.sports 
        ON seasons.sport_id = sports.id
WHERE seasons.id = '1e5f829b-1858-46d4-bea5-0d3b64191814'

SELECT
schedule.id as schedule_id, 
   games.game_id as game_id,
   schedule.game_date::date as game_date,
   schedule.game_time as game_time, 
   home_team.id as home_team,
   away_team.id as away_team, 
   final_home_score, 
   final_away_score,
   '' as missing_stats,
   seasons.id, 
   levels.level_name
FROM mhac.games
INNER JOIN mhac.schedule 
   ON games.game_id = schedule.game_id
INNER JOIN mhac.seasons
    ON schedule.season_id = seasons.id
INNER JOIN mhac.levels
    ON seasons.level_id = levels.id
LEFT OUTER JOIN mhac.teams AS home_team
   ON games.home_team_id = home_team.id
LEFT OUTER JOIN mhac.teams AS away_team
   ON games.away_team_id = away_team.id

WHERE (home_team.slug = 'tennessee_heat'
    OR away_team.slug = 'tennessee_heat')
ORDER BY game_date, game_time

SELECT
    schedule.id as schedule_id, 
    games.game_id as game_id,
    schedule.game_date::date as game_date,
    schedule.game_time as game_time, 
    home_team.id as home_team,
    away_team.id as away_team, 
    final_home_score, 
    final_away_score,
    0 as missing_stats,
    seasons.id as season_id, 
    levels.level_name
FROM mhac.games
INNER JOIN mhac.schedule 
    ON games.game_id = schedule.game_id
INNER JOIN mhac.seasons
    ON schedule.season_id = seasons.id
INNER JOIN mhac.levels
    ON seasons.level_id = levels.id
LEFT OUTER JOIN mhac.teams AS home_team
    ON games.home_team_id = home_team.id
LEFT OUTER JOIN mhac.teams AS away_team
    ON games.away_team_id = away_team.id
WHERE seasons.archive is null
ORDER BY schedule.game_date

SELECT * FROM mhac.seasons

BEGIN TRANSACTION;
DELETE FROM mhac.schedule

SELECT * FROM mhac.schedule where id = 211

SELECT * FROM mhac.games where game_id = 'b526c231-9549-497a-8084-617d35dd42d0'

SELECT * FROM mhac.season_teams_with_names where id = '1a638187-01fc-44f0-b0af-77bb6ad1b58a'
--COMMIT
BEGIN TRANSACTION;
UPDATE mhac.games
SET home_team_id = (SELECT team_id FROM mhac.season_teams_with_names where id = home_team_id),away_team_id = (SELECT team_id FROM mhac.season_teams_with_names where id = away_team_id) 
WHERE game_id = '809d31d8-a99c-41db-9646-f52748cf8104'

SELECT * FROM mhac.games

SELECT
    schedule.id as schedule_id, 
    games.game_id as game_id,
    schedule.game_date::date as game_date,
    schedule.game_time as game_time, 
    home_team.id as home_team,
    away_team.id as away_team, 
    final_home_score, 
    final_away_score,
    0 as missing_stats,
    seasons.id as season_id, 
    levels.level_name
FROM mhac.games
INNER JOIN mhac.schedule 
    ON games.game_id = schedule.game_id
INNER JOIN mhac.seasons
    ON schedule.season_id = seasons.id
INNER JOIN mhac.levels
    ON seasons.level_id = levels.id
LEFT OUTER JOIN mhac.teams AS home_team
    ON games.home_team_id = home_team.id
LEFT OUTER JOIN mhac.teams AS away_team
    ON games.away_team_id = away_team.id
WHERE seasons.archive is null
ORDER BY schedule.game_date

SELECT * FROM mhac.teams


--COMMIT
BEGIN TRANSACTION;
UPDATE mhac.games
SET away_team_id = 'c8606307-e1c2-45c8-a446-a739e38640bf'
WHERE game_id in ('bc6220d1-dd98-4d90-b141-19ba59de826a',
'e4625f8e-c20c-4a24-a69d-e942a008ef90')






SELECT COALESCE(expected_periods.period, game_results.period) as quarter, home_score, away_score, game_order 
FROM mhac.game_results 
FULL OUTER JOIN (
    SELECT '1' AS period 
    -- , :game_id AS game_id
    UNION
    SELECT '2' AS period
    -- , :game_id AS game_id
    UNION
    SELECT '3' AS period
    -- , :game_id AS game_id
    UNION
    SELECT '4' AS period
    -- , :game_id AS game_id
    
) as expected_periods
    ON game_results.game_id = expected_periods.game_id
    AND game_results.period = expected_periods.period
-- where (expected_periods.game_id = :game_id
-- OR game_results.game_id = :game_id)
ORDER BY game_order