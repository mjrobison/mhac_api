ALTER TABLE mhac.person                                                                                   
    ADD CONSTRAINT ux_persons UNIQUE (first_name, last_name, birth_date, person_type);
