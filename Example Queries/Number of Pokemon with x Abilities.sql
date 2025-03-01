-- number of pokemon with 2 abilities
WITH PokeAbilityCnt AS (
SELECT
	PA."PokedexRowId",
	MAX(PA."AbilitySlotNbr") AS AbilityCnt
FROM public."PokemonAbilities" AS PA
GROUP BY PA."PokedexRowId"
HAVING MAX(PA."AbilitySlotNbr") = 2)

SELECT COUNT("PokedexRowId") FROM PokeAbilityCnt
