UPDATE mhac.seasons
SET archive = true;


INSERT INTO mhac.seasons(id, name, year, level_id, sport_id, start_date, roster_submission_deadline, tournament_start_date, slug)
VALUES
(uuid_generate_v4(), '2020-2021 Fall', 2020, 1, 1, '2020-11-01', '2020-11-01', '2021-02-15', '2020_18u_boys_basketball'),
(uuid_generate_v4(), '2020-2021 Fall', 2020, 2, 1, '2020-11-01', '2020-11-01', '2021-02-15', '2020_18u_girls_basketball'),
(uuid_generate_v4(), '2020-2021 Fall', 2020, 3, 1, '2020-11-01', '2020-11-01', '2021-02-15', '2020_16u_boys_basketball'),
(uuid_generate_v4(), '2020-2021 Fall', 2020, 5, 1, '2020-11-01', '2020-11-01', '2021-02-15', '2020_14u_boys_basketball');


    INSERT INTO mhac.season_teams
    VALUES
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 1), (SELECT id FROM mhac.teams where slug = 'hendersonville_royals')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 5), (SELECT id FROM mhac.teams where slug = 'hendersonville_royals')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 1), (SELECT id FROM mhac.teams where slug = 'life_christian')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 5), (SELECT id FROM mhac.teams where slug = 'life_christian')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 1), (SELECT id FROM mhac.teams where slug = 'tennessee_heat')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 5), (SELECT id FROM mhac.teams where slug = 'tennessee_heat')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 1), (SELECT id FROM mhac.teams where slug = 'western_kentucky')),
    (uuid_generate_v4(), (SELECT id FROM mhac.seasons where year = '2020' and level_id = 5), (SELECT id FROM mhac.teams where slug = 'western_kentucky'));
