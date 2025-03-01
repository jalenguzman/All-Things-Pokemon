-- gen 3 vs gen 9 average bst
WITH Gen3 AS (
SELECT
	BS."Total" AS BSTotal
FROM public."Pokedex" AS P
	LEFT JOIN public."BaseStats" AS BS ON P."PokedexRowId" = BS."PokedexRowId"
WHERE P."Gen" = 3
	--megas and regional variants were not released until later
	AND P."IsMega" = False AND P."IsRegionVariant" = False),

Gen9 AS (
SELECT
	BS."Total" AS BSTotal
FROM public."Pokedex" AS P
	LEFT JOIN public."BaseStats" AS BS ON P."PokedexRowId" = BS."PokedexRowId"
WHERE P."Gen" = 9
	-- include regional variants whose original form may not have been released in Gen9
	OR (P."IsRegionVariant" = True AND LOWER(P."Subname") LIKE 'paldean%'))

SELECT CONCAT('Gen 3 Avg BST: ', ROUND(AVG(BSTotal), 2)) FROM Gen3
UNION
SELECT CONCAT('Gen 9 Avg BST: ', ROUND(AVG(BSTotal), 2)) FROM Gen9
