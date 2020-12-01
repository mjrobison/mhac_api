ALTER TABLE mhac.person                                                                                   
    ADD CONSTRAINT ux_persons UNIQUE (first_name, last_name, person_type);
