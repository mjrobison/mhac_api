ALTER TABLE mhac.teams
ADD COLUMN active BOOLEAN;

BEGIN TRANSACTION;
UPDATE mhac.teams
SET active = true;
