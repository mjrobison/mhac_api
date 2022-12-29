SELECT * FROM mhac.basketball_stats AS bs inner join mhac.season_teams as st on bs.team_id = st.id AND st.team_id = 'a611499e-c596-4d52-8730-d4dc130235d7';


SELECT st.season_id, player_id, number AS player_number, bs.team_id, p.first_name, p.last_name, t.team_name
                , SUM(field_goals_attempted) AS field_goals_attempted
                , SUM(field_goals_made) AS field_goals_made
                , SUM(three_pointers_attempted) AS three_pointers_attempted
                , SUM(three_pointers_made) AS three_pointers_made
                , SUM(free_throws_attempted) AS free_throws_attempted
                , SUM(free_throws_made) AS free_throws_made
                , SUM(total_points) AS total_points
                , SUM(assists) AS assists
                , SUM(offensive_rebounds) AS offensive_rebounds
                , SUM(defensive_rebounds) AS defensive_rebounds
                , SUM(total_rebounds) AS total_rebounds
                , SUM(steals) AS steals
                , SUM(blocks) AS blocks
                , SUM(turnovers) AS turnovers
                , COUNT(game_id) AS games_played
            FROM mhac.basketball_stats AS bs
            INNER JOIN mhac.season_teams AS st
                ON bs.team_id = st.id
            INNER JOIN mhac.teams AS t
                ON st.team_id = t.id
            INNER JOIN mhac.person AS p
                ON bs.player_id = p.id
            WHERE st.team_id = 'a611499e-c596-4d52-8730-d4dc130235d7'
                AND st.season_id IN ('ff4014db-cb89-4e45-b4ea-8521b301c176', 'c300cc68-e990-4158-a7c5-9a15c9f27f70', 'd099d7a6-05ff-4028-88a4-e609ddbb8d26', '3323edf0-d806-4e32-9fd2-cb698a27b3a9')
GROUP BY st.season_id, player_id, bs.team_id, p.first_name, p.last_name, t.team_name, number
;