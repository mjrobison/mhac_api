 CREATE OR REPLACE VIEW mhac.season_teams_with_names AS
 SELECT st.id,
    st.season_id,
    t.id AS team_id,
    t.team_name,
    t.team_mascot,
    t.address_id,
    t.main_color,
    t.secondary_color,
    t.website,
    t.logo_color,
    t.logo_grey,
    t.slug,
    l.level_name,
    s.archive
   FROM mhac.season_teams st
     JOIN mhac.teams t ON st.team_id = t.id
     JOIN mhac.seasons s ON st.season_id = s.id
     JOIN mhac.levels l ON s.level_id = l.id;

-- View: mhac.season_teams_with_names

-- DROP VIEW mhac.season_teams_with_names;

CREATE OR REPLACE VIEW mhac.season_teams_with_names AS
 SELECT st.id,
    st.season_id,
    t.id AS team_id,
    t.team_name,
    t.team_mascot,
    t.address_id,
    t.main_color,
    t.secondary_color,
    t.website,
    t.logo_color,
    t.logo_grey,
    t.slug,
    l.level_name,
    s.archive,
    t.conference
   FROM mhac.teams t
     LEFT OUTER JOIN mhac.season_teams st ON st.team_id = t.id
     LEFT OUTER JOIN mhac.seasons s ON st.season_id = s.id
     LEFT OUTER JOIN mhac.levels l ON s.level_id = l.id;

ALTER TABLE mhac.season_teams_with_names
    OWNER TO postgres;
