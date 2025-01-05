#load libraries
import pandas as pd

#call comprehensive scrape functions
pokedex = scrape_pokedex_data('https://pokemondb.net/pokedex/all')
moves = scrape_move_data('https://pokemondb.net/move/all')
abilities = scrape_ability_data('https://pokemondb.net/ability')
