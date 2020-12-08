ALTER TABLE mhac.game_results
    ADD CONSTRAINT ux_game_period UNIQUE (game_id, period);