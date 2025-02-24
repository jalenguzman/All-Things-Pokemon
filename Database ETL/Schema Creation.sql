-- an encyclopedia of all pokemon and their forms
CREATE TABLE "Pokedex"(
    "PokedexRowId" SMALLINT NOT NULL,
    "PokedexNbr" CHAR(4) NOT NULL, --national dex
    "PokemonName" VARCHAR(20) NOT NULL,
    "Subname" VARCHAR(25) NULL,
    "SpeciesName" VARCHAR(30) NOT NULL,
    "PokemonType1Id" SMALLINT NOT NULL,
    "PokemonType2Id" SMALLINT NOT NULL,
    "Height" DECIMAL(8, 2) NOT NULL,
    "Weight" DECIMAL(8, 2) NOT NULL,
    "FlavorText" VARCHAR(255) NOT NULL,
    "Gen" SMALLINT NOT NULL,
    "IsMega" BOOLEAN NOT NULL,
    "IsRegionVariant" BOOLEAN NOT NULL,
    "IsAdditionalVariant" BOOLEAN NOT NULL,
    "IsSubLegendary" BOOLEAN NOT NULL,
    "IsMythical" BOOLEAN NOT NULL,
    "IsLegendary" BOOLEAN NOT NULL,
    "ArtworkURL" VARCHAR(255) NULL
);
ALTER TABLE "Pokedex" ADD PRIMARY KEY("PokedexRowId");

-- an encylopedia of all pokemon moves and basic info about them
CREATE TABLE "Moves"(
    "MoveRowId" SMALLINT NOT NULL,
    "MoveName" VARCHAR(30) NOT NULL,
    "MoveTypeId" SMALLINT NOT NULL,
    "MoveCategoryId" SMALLINT NOT NULL,
    "MovePower" SMALLINT NULL,
    "MoveAccuracy" VARCHAR(5) NULL,
    "MovePowerPoints" SMALLINT NULL,
    "MoveDesc" VARCHAR(255) NOT NULL,
    "EffectProbability" SMALLINT NULL
);
ALTER TABLE "Moves" ADD PRIMARY KEY("MoveRowId");

-- an encyclopedia of all abilities and basic info about them
CREATE TABLE "Abilities"(
    "AbilityRowId" SMALLINT NOT NULL,
    "AbilityName" VARCHAR(30) NOT NULL,
    "AbilityDesc" VARCHAR(255) NOT NULL,
    "IntroGen" SMALLINT NOT NULL
);
ALTER TABLE "Abilities" ADD PRIMARY KEY("AbilityRowId");

-- a fact table for describing moves as either physical / special / status / other
CREATE TABLE "MoveCategory"(
    "MoveCategoryId" SMALLINT NOT NULL,
    "MoveCategoryDesc" VARCHAR(10) NOT NULL
);
ALTER TABLE "MoveCategory" ADD PRIMARY KEY("MoveCategoryId");

-- a fact table describing every Pokemon type
CREATE TABLE "Type"(
    "TypeId" SMALLINT NOT NULL,
    "TypeName" VARCHAR(10) NULL
);
ALTER TABLE "Type" ADD PRIMARY KEY("TypeId");

-- a fact table describing every egg group assigned to the Pokemon in the pokedex
CREATE TABLE "EggGroup"(
    "EggGroupId" SMALLINT NOT NULL,
    "EggGroupDesc" VARCHAR(15) NOT NULL
);
ALTER TABLE "EggGroup" ADD PRIMARY KEY("EggGroupId");

-- 
CREATE TABLE "TypeEffectiveness"(
    "TypeEffectivenessId" INTEGER NOT NULL,
    "AttackingTypeId" SMALLINT NOT NULL,
    "DefendingTypeId" SMALLINT NOT NULL,
    "Effectiveness" DECIMAL(8, 2) NOT NULL
);
ALTER TABLE "TypeEffectiveness" ADD PRIMARY KEY("TypeEffectivenessId");

-- used to connect pokedex entries to their possible abilities
CREATE TABLE "PokemonAbilities"(
    "PokedexRowId" SMALLINT NOT NULL,
    "AbilityRowId" SMALLINT NOT NULL,
    "IsHidden" BOOLEAN NOT NULL,
    "AbilitySlotNbr" SMALLINT NOT NULL --1,2, or 3
);
ALTER TABLE "PokemonAbilities" ADD PRIMARY KEY("PokedexRowId", "AbilityRowId");

-- 1 to 1 table with Pokedex for breeding info for each pokemon
CREATE TABLE "Breeding"(
    "PokedexRowId" SMALLINT NOT NULL,
    "MalePerc" SMALLINT NOT NULL,
    "FemalePerc" SMALLINT NOT NULL,
    "EggCycles" SMALLINT NOT NULL,
    "EggGroup1Id" SMALLINT NOT NULL,
    "EggGroup2Id" SMALLINT NOT NULL
);
ALTER TABLE "Breeding" ADD PRIMARY KEY("PokedexRowId");

-- 1 to 1 table with Pokedex for training info for each pokemon
CREATE TABLE "Training"(
    "PokedexRowId" SMALLINT NOT NULL,
    "CatchRatePerc" SMALLINT NOT NULL,
    "BaseFriendship" SMALLINT NOT NULL,
    "BaseExp" SMALLINT NOT NULL,
    "GrowthRate" VARCHAR(15) NOT NULL,
    "HPYield" SMALLINT NOT NULL,
    "AtkYield" SMALLINT NOT NULL,
    "DefYield" SMALLINT NOT NULL,
    "SpAtkYield" SMALLINT NOT NULL,
    "SpDefYield" SMALLINT NOT NULL,
    "SpdYield" SMALLINT NOT NULL
);
ALTER TABLE "Training" ADD PRIMARY KEY("PokedexRowId");

-- holds information about what pokemon things evolve from and what the requirement was to get them to evolve
CREATE TABLE "Evolution"(
    "EvolutionId" SMALLINT NOT NULL,
    "EvolvesFromRowId" SMALLINT NOT NULL,
    "EvolvesToRowId" SMALLINT NOT NULL,
    "EvolutionRequirement" VARCHAR(255) NULL
);
ALTER TABLE "Evolution" ADD PRIMARY KEY("EvolutionId");

-- used to connect pokedex entries to their viable moves
CREATE TABLE "PokemonMoves"(
    "PokedexNbr" SMALLINT NOT NULL,
    "MoveRowId" SMALLINT NOT NULL
);
ALTER TABLE "PokemonMoves" ADD PRIMARY KEY("PokedexNbr", "MoveRowId");

-- 1 to 1 table with Pokedex for base stat line info for each pokemon
CREATE TABLE "BaseStats"(
    "PokedexRowId" SMALLINT NOT NULL,
    "HP" INTEGER NOT NULL,
    "Atk" INTEGER NOT NULL,
    "Def" INTEGER NOT NULL,
    "SpAtk" INTEGER NOT NULL,
    "SpDef" INTEGER NOT NULL,
    "Speed" INTEGER NOT NULL,
    "Total" INTEGER NOT NULL
);
ALTER TABLE "BaseStats" ADD PRIMARY KEY("PokedexRowId");

-- creating foreign key connections
ALTER TABLE "PokemonAbilities" ADD CONSTRAINT "pokemonabilities_abilityrowid_foreign" FOREIGN KEY("AbilityRowId") REFERENCES "Abilities"("AbilityRowId"); -- PokemonAbilities.AbilityRowId N-->1 Abilities.AbilityRowId
ALTER TABLE "PokemonAbilities" ADD CONSTRAINT "pokemonabilities_pokedexrowid_foreign" FOREIGN KEY("PokedexRowId") REFERENCES "Pokedex"("PokedexRowId"); -- PokemonAbilities.PokedexRowId N-->1 Pokedex.PokedexRowId

ALTER TABLE "PokemonMoves" ADD CONSTRAINT "pokemonmoves_moverowid_foreign" FOREIGN KEY("MoveRowId") REFERENCES "Moves"("MoveRowId"); -- PokemonMoves.MoveRowId N-->1 Moves.MoveRowId

ALTER TABLE "Moves" ADD CONSTRAINT "moves_movetypeid_foreign" FOREIGN KEY("MoveTypeId") REFERENCES "Type"("TypeId"); -- Moves.MoveTypeId N-->1 Type.TypeId
ALTER TABLE "Moves" ADD CONSTRAINT "moves_movecategoryid_foreign" FOREIGN KEY("MoveCategoryId") REFERENCES "MoveCategory"("MoveCategoryId"); --Moves.MoveCategoryId N-->1 MoveCategory.MoveCategoryId

ALTER TABLE "Evolution" ADD CONSTRAINT "evolution_evolvesfromrowid_foreign" FOREIGN KEY("EvolvesFromRowId") REFERENCES "Pokedex"("PokedexRowId"); -- Evolution.EvolvesFromRowId N-->1 Pokedex.PokedexRowId
ALTER TABLE "Evolution" ADD CONSTRAINT "evolution_pokedexrowid_foreign" FOREIGN KEY("EvolvesToRowId") REFERENCES "Pokedex"("PokedexRowId"); -- Evolution.PokedexRowId N-->1 Pokedex.PokedexRowId

ALTER TABLE "Training" ADD CONSTRAINT "training_pokedexrowid_foreign" FOREIGN KEY("PokedexRowId") REFERENCES "Pokedex"("PokedexRowId"); -- Training.PokedexRowId 1<-->1 Pokedex.PokedexRowId
ALTER TABLE "BaseStats" ADD CONSTRAINT "basestats_pokedexrowid_foreign" FOREIGN KEY("PokedexRowId") REFERENCES "Pokedex"("PokedexRowId"); --Pokedex.PokedexRowId 1<-->1 BaseStats.PokedexRowId

ALTER TABLE "Breeding" ADD CONSTRAINT "breeding_pokedexrowid_foreign" FOREIGN KEY("PokedexRowId") REFERENCES "Pokedex"("PokedexRowId"); --Pokedex.PokedexRowId 1<-->1 Breeding.PokedexRowId
ALTER TABLE "Breeding" ADD CONSTRAINT "breeding_egggroup1id_foreign" FOREIGN KEY("EggGroup1Id") REFERENCES "EggGroup"("EggGroupId"); -- Breeding.EggGroup1Id N-->1 EggGroup.EggGroupId
ALTER TABLE "Breeding" ADD CONSTRAINT "breeding_egggroup2id_foreign" FOREIGN KEY("EggGroup2Id") REFERENCES "EggGroup"("EggGroupId"); --Breeding.EggGroup2Id N-->1 EggGroup.EggGroupId

ALTER TABLE "Pokedex" ADD CONSTRAINT "pokedex_pokemontype1id_foreign" FOREIGN KEY("PokemonType1Id") REFERENCES "Type"("TypeId"); -- Pokedex.PokemonType1Id N-->1 Type.TypeId
ALTER TABLE "Pokedex" ADD CONSTRAINT "pokedex_pokemontype2id_foreign" FOREIGN KEY("PokemonType2Id") REFERENCES "Type"("TypeId"); -- Pokedex.PokemonType2Id N-->1 Type.TypeId

ALTER TABLE "TypeEffectiveness" ADD CONSTRAINT "typeeffectiveness_attackingtypeid_foreign" FOREIGN KEY("AttackingTypeId") REFERENCES "Type"("TypeId"); --TypeEffectiveness.AttackingTypeId N-->1 Type.TypeId
ALTER TABLE "TypeEffectiveness" ADD CONSTRAINT "typeeffectiveness_defendingtypeid_foreign" FOREIGN KEY("DefendingTypeId") REFERENCES "Type"("TypeId"); --TypeEffectiveness.DefendingTypeId N-->1 Type.TypeId
