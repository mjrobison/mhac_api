CREATE VIEW mhac.season_teams_with_names AS
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
    l.level_name
   FROM (((mhac.season_teams st
     JOIN mhac.teams t ON ((st.team_id = t.id)))
     JOIN mhac.seasons s ON ((st.season_id = s.id)))
     JOIN mhac.levels l ON ((s.level_id = l.id)));


ALTER TABLE mhac.season_teams_with_names OWNER TO postgres;
