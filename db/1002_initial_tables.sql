CREATE TABLE mhac.addresses (
    id uuid NOT NULL,
    name character varying(150),
    address_line_1 character varying(150),
    address_line_2 character varying(150),
    city character varying(150),
    state character varying(2),
    postal_code character varying(10)
);


ALTER TABLE mhac.addresses OWNER TO postgres;

CREATE TABLE mhac.basketball_stats (
    pk integer NOT NULL,
    game_id uuid,
    player_id uuid,
    field_goals_attempted integer,
    field_goals_made integer,
    three_pointers_attempted integer,
    three_pointers_made integer,
    free_throws_attempted integer,
    free_throws_made integer,
    total_points integer,
    assists integer,
    offensive_rebounds integer,
    defensive_rebounds integer,
    total_rebounds integer,
    steals integer,
    blocks integer,
    team_id uuid,
    turnovers integer,
    roster_id bigint
);


ALTER TABLE mhac.basketball_stats OWNER TO postgres;
CREATE SEQUENCE mhac.basketball_stats_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE mhac.basketball_stats_pk_seq OWNER TO postgres;
ALTER SEQUENCE mhac.basketball_stats_pk_seq OWNED BY mhac.basketball_stats.pk;


CREATE TABLE mhac.game_results (
    pk integer NOT NULL,
    game_id uuid,
    period character varying(5),
    home_score integer,
    away_score integer,
    game_order integer
);
ALTER TABLE mhac.game_results OWNER TO postgres;

CREATE SEQUENCE mhac.game_results_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mhac.game_results_pk_seq OWNER TO postgres;
ALTER SEQUENCE mhac.game_results_pk_seq OWNED BY mhac.game_results.pk;


CREATE TABLE mhac.games (
    game_id uuid NOT NULL,
    home_team_id uuid,
    away_team_id uuid,
    final_home_score integer,
    final_away_score integer
);
ALTER TABLE mhac.games OWNER TO postgres;


CREATE TABLE mhac.levels (
    id integer NOT NULL,
    level_name character varying(50)
);
ALTER TABLE mhac.levels OWNER TO postgres;

CREATE SEQUENCE mhac.levels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE mhac.levels_id_seq OWNER TO postgres;
ALTER SEQUENCE mhac.levels_id_seq OWNED BY mhac.levels.id;

CREATE TABLE mhac.person (
    id uuid NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    birth_date date,
    height character varying(10),
    person_type integer,
    team_id uuid,
    number integer,
    "position" character varying
);
ALTER TABLE mhac.person OWNER TO postgres;


CREATE TABLE mhac.person_type (
    id integer NOT NULL,
    type character varying(100)
);
ALTER TABLE mhac.person_type OWNER TO postgres;
CREATE SEQUENCE mhac.person_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE mhac.person_type_id_seq OWNER TO postgres;
ALTER SEQUENCE mhac.person_type_id_seq OWNED BY mhac.person_type.id;


CREATE TABLE mhac.schedule (
    id integer NOT NULL,
    game_id uuid,
    game_date timestamp without time zone,
    game_time timestamp without time zone,
    season_id uuid,
    neutral_site boolean
);
ALTER TABLE mhac.schedule OWNER TO postgres;
CREATE SEQUENCE mhac.schedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE mhac.schedule_id_seq OWNER TO postgres;
ALTER SEQUENCE mhac.schedule_id_seq OWNED BY mhac.schedule.id;


CREATE TABLE mhac.season_teams (
    id uuid NOT NULL,
    season_id uuid NOT NULL,
    team_id uuid NOT NULL
);

ALTER TABLE mhac.season_teams OWNER TO postgres;

CREATE TABLE mhac.seasons (
    id uuid NOT NULL,
    name character varying(100),
    year character varying(4),
    level_id integer NOT NULL,
    sport_id integer NOT NULL,
    start_date timestamp without time zone,
    roster_submission_deadline timestamp without time zone,
    roster_addition_deadline timestamp without time zone,
    tournament_start_date timestamp without time zone,
    archive boolean
);
ALTER TABLE mhac.seasons OWNER TO postgres;


CREATE TABLE mhac.teams (
    id uuid NOT NULL,
    team_name character varying(100),
    team_mascot character varying(150),
    address_id uuid,
    main_color character varying(6),
    secondary_color character varying(6),
    website character varying(150),
    logo_color character varying(150),
    logo_grey character varying(150),
    slug character varying(150)
);
ALTER TABLE mhac.teams OWNER TO postgres;



CREATE TABLE mhac.sports (
    id integer NOT NULL,
    sport_name character varying(100) NOT NULL
);

ALTER TABLE mhac.sports OWNER TO postgres;
CREATE SEQUENCE mhac.sports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE mhac.sports_id_seq OWNER TO postgres;
ALTER SEQUENCE mhac.sports_id_seq OWNED BY mhac.sports.id;

CREATE TABLE mhac.standings (
    pk integer NOT NULL,
    team_id uuid,
    season_id uuid,
    wins integer,
    losses integer,
    games_played integer,
    win_percentage numeric(5,4)
);


ALTER TABLE mhac.standings OWNER TO postgres;
CREATE SEQUENCE mhac.standings_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE mhac.standings_pk_seq OWNER TO postgres;
ALTER SEQUENCE mhac.standings_pk_seq OWNED BY mhac.standings.pk;


CREATE TABLE mhac.team_rosters (
    roster_id integer NOT NULL,
    season_team_id uuid,
    player_id uuid
);


ALTER TABLE mhac.team_rosters OWNER TO postgres;
CREATE SEQUENCE mhac.team_rosters_roster_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE mhac.team_rosters_roster_id_seq OWNER TO postgres;
ALTER SEQUENCE mhac.team_rosters_roster_id_seq OWNED BY mhac.team_rosters.roster_id;

CREATE TABLE mhac.tournamentgames (
    game_number integer,
    game_date date,
    game_time timestamp without time zone,
    home_team uuid,
    away_team uuid,
    home_team_score integer,
    away_team_score integer,
    location text,
    home_team_seed text,
    away_team_seed text,
    game_description text
);


ALTER TABLE mhac.tournamentgames OWNER TO postgres;

ALTER TABLE ONLY mhac.basketball_stats ALTER COLUMN pk SET DEFAULT nextval('mhac.basketball_stats_pk_seq'::regclass);
ALTER TABLE ONLY mhac.game_results ALTER COLUMN pk SET DEFAULT nextval('mhac.game_results_pk_seq'::regclass);
ALTER TABLE ONLY mhac.levels ALTER COLUMN id SET DEFAULT nextval('mhac.levels_id_seq'::regclass);
ALTER TABLE ONLY mhac.person_type ALTER COLUMN id SET DEFAULT nextval('mhac.person_type_id_seq'::regclass);
ALTER TABLE ONLY mhac.schedule ALTER COLUMN id SET DEFAULT nextval('mhac.schedule_id_seq'::regclass);
ALTER TABLE ONLY mhac.sports ALTER COLUMN id SET DEFAULT nextval('mhac.sports_id_seq'::regclass);
ALTER TABLE ONLY mhac.standings ALTER COLUMN pk SET DEFAULT nextval('mhac.standings_pk_seq'::regclass);
ALTER TABLE ONLY mhac.team_rosters ALTER COLUMN roster_id SET DEFAULT nextval('mhac.team_rosters_roster_id_seq'::regclass);


