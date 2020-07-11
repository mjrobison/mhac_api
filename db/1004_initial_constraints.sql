
ALTER TABLE ONLY mhac.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: basketball_stats basketball_stats_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.basketball_stats
    ADD CONSTRAINT basketball_stats_pkey PRIMARY KEY (pk);


--
-- Name: game_results game_results_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.game_results
    ADD CONSTRAINT game_results_pkey PRIMARY KEY (pk);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (game_id);


--
-- Name: levels levels_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (id);


--
-- Name: person person_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);


--
-- Name: person_type person_type_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.person_type
    ADD CONSTRAINT person_type_pkey PRIMARY KEY (id);


--
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- Name: season_teams season_teams_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.season_teams
    ADD CONSTRAINT season_teams_pkey PRIMARY KEY (id);


--
-- Name: seasons seasons_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (id);


--
-- Name: sports sports_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.sports
    ADD CONSTRAINT sports_pkey PRIMARY KEY (id);


--
-- Name: standings standings_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.standings
    ADD CONSTRAINT standings_pkey PRIMARY KEY (pk);


--
-- Name: team_rosters team_rosters_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.team_rosters
    ADD CONSTRAINT team_rosters_pkey PRIMARY KEY (roster_id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- Name: basketball_stats ux_stats; Type: CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.basketball_stats
    ADD CONSTRAINT ux_stats UNIQUE (game_id, player_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

-- ALTER TABLE ONLY public.users
--     ADD CONSTRAINT users_email_key UNIQUE (email);


-- --
-- -- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
-- --

-- ALTER TABLE ONLY public.users
--     ADD CONSTRAINT users_pkey PRIMARY KEY (id);


-- --
-- -- Name: users users_uuid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
-- --

-- ALTER TABLE ONLY public.users
--     ADD CONSTRAINT users_uuid_key UNIQUE (uuid);


--
-- Name: basketball_stats basketball_stats_game_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.basketball_stats
    ADD CONSTRAINT basketball_stats_game_id_fkey FOREIGN KEY (game_id) REFERENCES mhac.games(game_id);


--
-- Name: basketball_stats basketball_stats_player_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.basketball_stats
    ADD CONSTRAINT basketball_stats_player_id_fkey FOREIGN KEY (player_id) REFERENCES mhac.person(id);


--
-- Name: basketball_stats basketball_stats_team_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.basketball_stats
    ADD CONSTRAINT basketball_stats_team_id_fkey FOREIGN KEY (team_id) REFERENCES mhac.season_teams(id);


--
-- Name: game_results game_results_game_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.game_results
    ADD CONSTRAINT game_results_game_id_fkey FOREIGN KEY (game_id) REFERENCES mhac.games(game_id);


--
-- Name: games games_away_team_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.games
    ADD CONSTRAINT games_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES mhac.season_teams(id);


--
-- Name: games games_home_team_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.games
    ADD CONSTRAINT games_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES mhac.season_teams(id);


--
-- Name: person person_person_type_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.person
    ADD CONSTRAINT person_person_type_fkey FOREIGN KEY (person_type) REFERENCES mhac.person_type(id);


--
-- Name: schedule schedule_game_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.schedule
    ADD CONSTRAINT schedule_game_id_fkey FOREIGN KEY (game_id) REFERENCES mhac.games(game_id);


--
-- Name: schedule schedule_season_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.schedule
    ADD CONSTRAINT schedule_season_id_fkey FOREIGN KEY (season_id) REFERENCES mhac.seasons(id);


--
-- Name: season_teams season_teams_season_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.season_teams
    ADD CONSTRAINT season_teams_season_id_fkey FOREIGN KEY (season_id) REFERENCES mhac.seasons(id);


--
-- Name: season_teams season_teams_team_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.season_teams
    ADD CONSTRAINT season_teams_team_id_fkey FOREIGN KEY (team_id) REFERENCES mhac.teams(id);


--
-- Name: seasons seasons_level_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.seasons
    ADD CONSTRAINT seasons_level_id_fkey FOREIGN KEY (level_id) REFERENCES mhac.levels(id);


--
-- Name: seasons seasons_sport_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.seasons
    ADD CONSTRAINT seasons_sport_id_fkey FOREIGN KEY (sport_id) REFERENCES mhac.sports(id);


--
-- Name: standings standings_season_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.standings
    ADD CONSTRAINT standings_season_id_fkey FOREIGN KEY (season_id) REFERENCES mhac.seasons(id);


--
-- Name: team_rosters team_rosters_player_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.team_rosters
    ADD CONSTRAINT team_rosters_player_id_fkey FOREIGN KEY (player_id) REFERENCES mhac.person(id);


--
-- Name: team_rosters team_rosters_season_team_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.team_rosters
    ADD CONSTRAINT team_rosters_season_team_id_fkey FOREIGN KEY (season_team_id) REFERENCES mhac.season_teams(id);


--
-- Name: teams teams_address_id_fkey; Type: FK CONSTRAINT; Schema: mhac; Owner: postgres
--

ALTER TABLE ONLY mhac.teams
    ADD CONSTRAINT teams_address_id_fkey FOREIGN KEY (address_id) REFERENCES mhac.addresses(id);


--
-- PostgreSQL database dump complete
--

