-- number of pokemon with access to [MoveName]
SELECT
  -- counting the number of forms and number of species separately
	COUNT(P."PokedexRowId") AS VariationCnt,
	COUNT(DISTINCT P."PokedexNbr") AS SpeciesCnt
FROM public."Pokedex" AS P
	LEFT JOIN public."PokemonMoves" AS PM ON CAST(P."PokedexNbr" AS INTEGER) = PM."PokedexNbr"
	LEFT JOIN public."Moves" AS M ON PM."MoveRowId" = M."MoveRowId"
WHERE M."MoveName" = 'Close Combat' --replace with whatever move wanted
