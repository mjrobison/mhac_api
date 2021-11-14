ALTER TABLE mhac.person
ADD COLUMN age INT;

UPDATE mhac.person
SET AGE = (date_part('year','09/01/2021'::date) - date_part('year', birth_date::date))::int

ALTER TABLE mhac.person
DROP COLUMN birth_date;
