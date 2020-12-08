UPDATE mhac.seasons 
SET slug = lower(s1.year::text || '_' || REPLACE(levels.level_name::text, ' ', '_') || '_' || sports.sport_name::text)
FROM mhac.seasons s1
INNER JOIN mhac.levels
    ON s1.level_id = levels.id
INNER JOIN mhac.sports
    ON s1.sport_id = sports.id