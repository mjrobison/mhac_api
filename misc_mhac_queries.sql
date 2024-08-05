 SELECT ROW_NUMBER() OVER (PARTITION BY seasons.id ORDER BY game_date, game_time ) AS logical_game_number, game_number, game_date, game_time, home_team.team_id as home_team
    , away_team.team_id as away_team, home_team_score, away_team_score, '' as game_location
    , seasons.id as season_id,
    home_team_seed, away_team_seed,
        (SELECT string_agg(game_number::text, ',')
    FROM mhac.tournamentgames t
    WHERE winner_to = tournamentgames.game_number
    AND season_id = tournamentgames.season_id) AS winners_from,
    (SELECT string_agg(game_number::text, ',')
    FROM mhac.tournamentgames t
    WHERE loser_to = tournamentgames.game_number
        AND season_id = tournamentgames.season_id) AS losers_from
    , tournamentgames.game_description
    , CASE WHEN seasons.tournament_start_date > current_date + 3 THEN false
        ELSE true
    END display,
    winner_to, loser_to
    FROM mhac.tournamentgames
    INNER JOIN mhac.seasons
        ON tournamentgames.season_id = seasons.id
    INNER JOIN mhac.levels
        ON levels.id = seasons.level_id
    LEFT OUTER JOIN mhac.standings as home_team
        ON tournamentgames.home_team_seed::int = home_team.standings_rank
        AND tournamentgames.season_id = home_team.season_id
    LEFT OUTER JOIN mhac.standings as away_team
        ON tournamentgames.away_team_seed::int = away_team.standings_rank
        AND tournamentgames.season_id = away_team.season_id


    ORDER BY game_number


SELECT * FROM mhac.tournamentgames
SELECT * FROM mhac.standings
WHERE season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a'
    and standings_rank = 5




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


UPDATE mhac.standings
SET standings_rank = rn
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY standings.season_id ORDER BY win_percentage desc) as rn, standings.season_id, standings.team_id FROM mhac.standings
INNER JOIN mhac.season_teams_with_names
    ON standings.team_id = season_teams_with_names.id WHERE archive is null AND season_teams_with_names.season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a') as r
WHERE standings.season_id = r.season_id
AND standings.team_id = r.team_id;




INSERT INTO mhac.tournamentgames(game_number,  game_date, game_time, home_team_seed, away_team_seed, game_description, season_id, winner_to, loser_to)
VALUES
(1, '2022-02-10', '11:00:00', 4, 5, Null, '4312875b-e949-4f6c-9d33-a3086873bc1a', 3, 5  )

SELECT * FROM mhac.tournamentgames WHERE season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a' AND game_number = 7;

DELETE FROM mhac.tournamentgames
WHERE season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a'
    AND game_number in (5,6)


 UPDATE mhac.tournamentgames
SET game_date = '2022-02-12'::date, game_time = '14:30:00'::time, home_team_seed = NULL, away_team_seed = NULL, game_description = '', winner_to = NULL, loser_to = NULL
WHERE game_number = 7
    AND season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a'::uuid


SELECT COUNT(*)
FROM mhac.season_teams_with_names
INNER JOIN mhac.standings
    ON season_teams_with_names.id = standings.team_id
WHERE season_teams_with_names.season_id = '4312875b-e949-4f6c-9d33-a3086873bc1a'
    AND standings_rank <> 99