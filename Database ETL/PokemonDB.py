#load libraries
import pandas as pd
import requests #requests.get()
from bs4 import BeautifulSoup #soup.find() #BeautifulSoup()
import re #re.findall() #re.search()
import itertools #itertools.product()

#DEF SCRAPE FUNCTIONS
def get_request_response(url):
  response = requests.get(url)
  if response.status_code != 200: #only status code that we accept
    raise Exception(f"Failed to load page {url}")
  return response

def scrape_pokedex_data(url):
  response = get_request_response(url)
  
  soup = BeautifulSoup(response.content, 'html.parser') #parse using BeautifulSoup
  table = soup.find('table', {'id': 'pokedex'}) #select table necessary
  
  #extract
  pokemon_data = []
  headers = [header.text for header in table.find('thead').find_all('th')]
  rows = table.find('tbody').find_all('tr')

  #for every row of the table on pokedex page
  for row in rows:
    cells = row.find_all('td')
    pokemon = {}
    for i in range(len(headers)):
            if headers[i] == 'Name':
                name_cell = cells[i]
                name = name_cell.find('a').text.strip()
                subname = name_cell.find('small').text.strip() if name_cell.find('small') else None
                pokemon['Name'] = name
                pokemon['Subname'] = subname
            else:
                pokemon[headers[i]] = cells[i].text.strip()
    pokemon_data.append(pokemon) #append to list

  df = pd.DataFrame(pokemon_data) #return as df
  return df

def scrape_move_data(url):
  response = get_request_response(url)

  soup = BeautifulSoup(response.content, 'html.parser') #parse using BeautifulSoup
  table = soup.find('table', {'id': 'moves'}) #select table necessary

  #extract
  move_data = []
  headers = [header.text for header in table.find('thead').find_all('th')]
  rows = table.find('tbody').find_all('tr')

  #for every pokedex row
  for row in rows:
        cells = row.find_all('td')
        moves = {}
        for i in range(len(headers)):
            cell = cells[i]
            img = cell.find('img')
            if img: #images need to be saved differently than plain text
                    #move categories: (physical/special/status) are saved as images in this table
                moves[headers[i]] = img['src']
            else:
                moves[headers[i]] = cell.text.strip()
        move_data.append(moves)

  df = pd.DataFrame(move_data)
  return df

def scrape_ability_data(url):
  response = get_request_response(url)

  soup = BeautifulSoup(response.content, 'html.parser') #parse using BeautifulSoup
  table = soup.find('table', {'id': 'abilities'}) #select table necessary

  #extract
  #same as pokedex below
  ability_data = []
  headers = [header.text for header in table.find('thead').find_all('th')]
  rows = table.find('tbody').find_all('tr')

  for row in rows:
    cells = row.find_all('td')
    abilities= {
        headers[i]: cells[i].text.strip() for i in range(len(headers))
    }
    ability_data.append(abilities)

  df = pd.DataFrame(ability_data)
  return df

def get_special_pokemon(choice):
  match choice:
        case 'Sublegendary':
            poke_list = ['Articuno', 'Zapdos', 'Moltres',
                     'Raikou', 'Entei', 'Suicine',
                     'Regirock', 'Regice', 'Registeel', 'Regieleki', 'Regidrago',
                     'Latias', 'Latios',
                     'Uxie', 'Mesprit', 'Azelf'
                     'Heatran', 'Regigigas', 'Cresselia',
                     'Colbalion', 'Terrakion', 'Virizion', 'Silvally',
                     'Tornadus', 'Thundurus', 'Landorus', 'Enamorus',
                     'Tapu Koko', 'Tapu Lele', 'Tapu Bulu', 'Tapu Fini',
                     'Kubfu', 'Urshifu', 'Glastrier', 'Spectrier',
                     'Wo-Chien', 'Chien-Pao', 'Ting-Lu', 'Chi-Yu',
                     'Okidogi', 'Munkidori', 'Fezandipiti', 'Ogerpon']

        case 'Legendary':
           poke_list = ['Mewtwo', 'Lugia', 'Ho-Oh', #Gen 1 and 2 Legendaries
                     'Kyogre', 'Groudon', 'Rayquaza', #Gen 3
                     'Dialga', 'Palkia', 'Giratina',  #Gen 4
                     'Reshiram', 'Zekrom', 'Kyurem',  #Gen 5
                     'Xerneas', 'Yveltal', 'Zygarde', #Gen 6
                     'Cosmog', 'Cosmeom', 'Solgaleo', 'Lunala', 'Necrozma', #Gen 7
                     'Zacian', 'Zamazenta', 'Eternatus', 'Calyrex', #Gen 8
                     'Koraidon', 'Miraidon', 'Terapagos'] #Gen 9

        case 'Mythical':
            poke_list = ['Mew', 'Celebi', 'Jirachi', 'Deoxys',
                    'Phione', 'Manaphy', 'Darkrai', 'Shaymin',
                    'Arceus', 'Victini', 'Keldeo', 'Meloetta',
                    'Genesect', 'Diancie', 'Hoopa', 'Volcanion',
                    'Magearna', 'Marshadow', 'Zeraora', 'Meltan',
                    'Melmetal', 'Zarude', 'Pecharunt']

        # if match is not confirmed, use last case
        case _:
            return "Invalid Choice"
  return poke_list

def get_pokemon_gen(PokedexNbr):
  converted = int(PokedexNbr)

  if(converted <= 151):
    return 1
  elif(converted <= 251):
    return 2
  elif(converted <= 386):
    return 3
  elif(converted <= 493):
    return 4
  elif(converted <= 649):
    return 5
  elif(converted <= 721):
    return 6
  elif(converted <= 809):
    return 7
  elif(converted <= 905):
    return 8
  elif(converted >= 906):
    return 9
  else:
    return "Invalid Pokedex Number"

def get_move_category(cat):
  match cat:
    case 'https://img.pokemondb.net/images/icons/move-special.png':
      return 'Special'
    case 'https://img.pokemondb.net/images/icons/move-status.png':
      return 'Status'
    case 'https://img.pokemondb.net/images/icons/move-physical.png':
      return 'Physical'
    case _:
      return 'None'

def scrape_individual_page_data(url):
  response = get_request_response(url)

  soup = BeautifulSoup(response.content, 'html.parser') #parse using BeautifulSoup
  tables_dict = {}

  #artwork url
  img_tag = soup.find('img', {'alt': re.compile(r'.artwork')}) #find first img named artwork
  img_url = img_tag['src'] if img_tag else None #if it has a source
  tables_dict['Artwork'] = img_url #return back into tables_dict

  #general tables
  headers_of_interest = ["Pokédex data", "Training", "Breeding", "Pokédex entries"] #tables we want return data for
  headers = soup.find_all(['h2', 'h3'])

  for header in headers:
        header_text = header.text.strip()
        if header_text in headers_of_interest:
            #Find the next table after the header
            table = header.find_next('table')
            if table:
                rows = table.find_all('tr')
                table_data = []
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    cell_data = [cell.text.strip() for cell in cells]
                    table_data.append(cell_data)
                # Ensure all rows have the same number of columns
                max_columns = max(len(row) for row in table_data)
                table_data = [row + [''] * (max_columns - len(row)) for row in table_data]
                df = pd.DataFrame(table_data)
                tables_dict[header_text] = df

  #evolution table
  evo_tables = soup.find_all('div', {'class': 'infocard-list-evo'})
  for idx, evo_table in enumerate(evo_tables):
      evo_data = []
      evo_cards = evo_table.find_all('div', {'class': 'infocard'}) #pokemon in evolution
      evo_arrows = evo_table.find_all('span', {'class': 'infocard infocard-arrow'}) #level/how they evolve
      for i, card in enumerate(evo_cards):
          card_data = card.text.strip().split('\n')
          if i < len(evo_arrows):
              arrow_text = evo_arrows[i].text.strip()
              card_data.append(arrow_text)
          evo_data.append(card_data)
      df = pd.DataFrame(evo_data)
      tables_dict[f'Evolution_Table_{idx + 1}'] = df

  #Extract move tables
  move_tables = soup.find_all('table', {'class': 'data-table'})
  for idx, table in enumerate(move_tables):
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = table.find_all('tr')
    table_data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        cell_data = []
        for cell in cells:
            img = cell.find('img')
            if img:
                cell_data.append(img['src'])
            else:
                cell_data.append(cell.text.strip())
        table_data.append(cell_data)
    df = pd.DataFrame(table_data, columns=headers if headers else None)
    tables_dict[f'Move_Table_{idx + 1}'] = df

  return tables_dict

# Function to split abilities into three columns
def split_abilities(abilities):
    # Pattern to match abilities
    pattern = r"(\d\.\s*([^0-9]+?))(?=(?:\d\.\s*[^0-9])|$)"
    matches = re.findall(pattern, abilities)
    abilities_split = [match[1].strip() for match in matches]

    # Split the second ability if it contains concatenated abilities
    if len(abilities_split) > 1:
        ability2 = abilities_split[1]
        match = re.search(r'([a-z])([A-Z])', ability2)
        if match:
            split_idx = match.start(1) + 1
            abilities_split[1] = ability2[:split_idx].strip()
            abilities_split.append(ability2[split_idx:].strip())

    # Ensure the list has exactly 3 elements
    return pd.Series(abilities_split + [None] * (3 - len(abilities_split)))

def transpose_df(df):
    df = df.transpose()
    df.columns = df.iloc[0] #set column names to values in row 1
    df = df[1:] #remove row 1
    return df

def clean_pokedex_entry_data(df):
    df = transpose_df(df)

    df['Height'] = df['Height'].str.split(r'([a-z])').str[0].replace('—', '0').astype(float)
    df['Weight'] = df['Weight'].str.split(r'([a-z])').str[0].replace('—', '0').astype(float)
    #df[['Type1', 'Type2']] = df['Type'].str.split(' ')
    df[['Ability1', 'Ability2', 'HiddenAbility']] = df['Abilities'].apply(split_abilities)
    df['PokedexNbr'] = df['National №']

    df = df[['PokedexNbr', 'Type', 'Species', 'Height', 'Weight',
             'Ability1', 'Ability2', 'HiddenAbility']]
    return df

def clean_training_data(df):
    df = transpose_df(df)
    df['CatchRatePerc'] = df['Catch rate'].str.split('(').str[0].replace('—', '0').astype(float)
    df['BaseFriendship'] = df['Base Friendship'].str.split('(').str[0].replace('—', '0').astype(float)
    df['BaseExp'] = df['Base Exp.'].replace('—', '0').astype(float)

    df.rename(columns=
    {'EV yield': 'EVYield',
     'Growth Rate': 'GrowthRate'}, inplace=True)

    df = df[['EVYield', 'CatchRatePerc', 'BaseFriendship', 'BaseExp', 'GrowthRate']]
    return df

def clean_breeding_data(df):
    df = transpose_df(df)

    if df['Gender'].str.contains('Genderless|—').any():
      df['MalePerc'] = 0
      df['FemalePerc'] = 0
    else:
      df[['MalePerc', 'FemalePerc']] = df['Gender'].str.split(',', expand=True)
      df['MalePerc'] = df['MalePerc'].str.split('%').str[0].astype(float)
      df['FemalePerc'] = df['FemalePerc'].str.split('%').str[0].astype(float)

    df['EggCycles'] = df['Egg cycles'].str.split('(').str[0].replace('—', '0').astype(float)
    df[['EggGroup1', 'EggGroup2']] = df['Egg Groups'].str.split(',', expand = True).reindex([0, 1], axis=1)
    df['EggGroup2'] = df['EggGroup2'].str.strip() #trim whitespace

    df = df[['MalePerc', 'FemalePerc', 'EggCycles', 'EggGroup1', 'EggGroup2']]
    return df

def clean_pokdex_flavor_text_data(dict):
    if 'Pokédex entries' in dict: #check if entry exists, may not for scarlet/violet dlc exclusives
      df = dict['Pokédex entries']

      rows = len(df.index) - 1 #get max row in df (latest flavortext)
      data = {'FlavorText': [df[1][rows]]} #select out max row as flavortext

      return(pd.DataFrame(data))
    else:
      return None

def clean_evolution_data(dict):
  res = {key: val for key, val in dict.items() if key.startswith('Evolution_Table_')}
  if res == {}: #if there is no evolution for the pokemon
    return None

  data = []
  for key in res:
    temp = res[key]
    data.append(temp)

  df = pd.concat(data)
  df = pd.DataFrame(df)

  df.columns = ['Pokemon', 'Evolution']
  df['Evolution'] = df['Evolution'].shift(1)
  df = df.groupby('Pokemon').first()

  return df

def clean_move_data(dict):
    res = {key: val for key, val in dict.items() if key.startswith('Move_Table_')}
    data = []

    for key in res:
      temp = res[key]
      temp = temp[1:]
      if 'Move' in temp.columns:
        data.append(temp['Move'])

    df = pd.concat(data)
    df = df.unique()
    df = pd.DataFrame(df, columns = ['Move'])
    return df

def clean_individual_page_data(tables_data):
    artwork_url = pd.DataFrame([tables_data['Artwork']], columns = ['ArtURL'])
    entry_data = clean_pokedex_entry_data(tables_data['Pokédex data']) #pokedex
    training_data = clean_training_data(tables_data['Training']) #training
    breeding_data = clean_breeding_data(tables_data['Breeding']) #breeding
    flavor_text_data = clean_pokdex_flavor_text_data(tables_data) #flavor text
    evolution_data = clean_evolution_data(tables_data) #evolution
    move_data = clean_move_data(tables_data) #moves

    #combine as needed for sql table storage
    df = pd.concat([entry_data, training_data, breeding_data], axis = 1)
    df = pd.concat([df.reset_index(drop=True), artwork_url, flavor_text_data], axis = 1)

    return df, evolution_data, move_data

def augment_pokedex_data(pokedex):
  pokedex[['Type1', 'Type2']] = pokedex['Type'].str.split(' ', expand=True, n=1) #split into two columns
  pokedex['Gen'] = pokedex['#'].apply(get_pokemon_gen) #pokemon generation
  pokedex['PokedexRowId'] = pokedex.index + 1
  
  #Add True or False Columns
  pokedex['IsMega'] = pokedex['Subname'].str.contains('Mega', case=False, na=False) #megas
  pokedex['IsRegionVariant'] = pokedex['Subname'].str.contains('Galarian|Alolan|Hisuian|Paldean', case=False, na=False) #regional variants
  pokedex['IsAdditionalVariant'] = pokedex['IsAdditionalVariant'] = (pokedex['Subname'].str.contains('None') == False) & \
                                   (pokedex['IsMega'] == False) & \
                                   (pokedex['IsRegionVariant'] == False) #additional variants
  
  #different types of special/legendary pokemon
  pokedex['IsSubLegendary'] = pokedex['Name'].apply(lambda x: True if any(i in x for i in get_special_pokemon('Sublegendary')) else False)
  pokedex['IsMythical'] = pokedex['Name'].apply(lambda x: True if any(i in x for i in get_special_pokemon('Mythical')) else False)
  pokedex['IsLegendary'] = pokedex['Name'].apply(lambda x: True if any(i in x for i in get_special_pokemon('Legendary')) else False)
  
  #renaming columns for pokedex
  pokedex.rename(columns=
    {'#': 'PokedexNbr', #more descriptive
     'Name': 'PokemonName',
     'Attack': 'Atk',
     'Defense': 'Def',
     'Sp. Atk': 'SpAtk', #having the extra space will cause me trouble at some point
     'Sp. Def': 'SpDef'}, inplace=True)

  pokedex = pokedex[['PokedexRowId', 'PokedexNbr', 'PokemonName', 'Subname', 'Type1', 'Type2',
                   'Total', 'HP', 'Atk', 'Def', 'SpAtk', 'SpDef', 'Speed',
                   'Gen', 'IsMega', 'IsRegionVariant', 'IsAdditionalVariant',
                   'IsSubLegendary', 'IsMythical', 'IsLegendary']] #reorder and select

  return pokedex

def augment_move_data(moves):
  moves['Category'] = moves['Cat.'].apply(get_move_category)
  moves['MoveRowId'] = moves.index + 1
  
  moves.rename(columns =
    {'Name': 'MoveName',
     'Type': 'MoveType',
     'Power': 'MovePower',
     'Acc.': 'MoveAccuracy',
     'PP': 'MovePowerPoints',
     'Effect': 'MoveDesc',
     'Prob. (%)': 'EffectProbability'}, inplace = True)

  moves = moves[['MoveRowId', 'MoveName', 'MoveType', 'Category', 'MovePower', 'MoveAccuracy',
               'MovePowerPoints', 'MoveDesc', 'EffectProbability']]
  
  return moves

def augment_ability_data(abilities):
  abilities['AbilityRowId'] = abilities.index + 1
  abilities.rename(columns =
     {'Name': 'AbilityName',
      'Description': 'AbilityDesc',
      'Gen.': 'IntroGen'}, inplace = True)
      
  abilities = abilities[['AbilityRowId', 'AbilityName', 'AbilityDesc', 'IntroGen']]
  
  return abilities

def create_move_category_table(moves):
  move_category = pd.DataFrame()
  move_category['MoveCategoryDesc'] = moves['Category'].unique()
  move_category = move_category.sort_values(by = 'MoveCategoryDesc')
  move_category['MoveCategoryId'] = range(len(move_category))
  
  return move_category

#create the base stats table
base_stats = pokedex[['PokedexRowId', 'HP', 'Atk', 'Def', 'SpAtk', 'SpDef', 'Speed', 'Total']]

#create fact table for different Pokemon Types
type_ids = {
    "Normal": 1,
    "Fire": 2,
    "Water": 3,
    "Electric": 4,
    "Grass": 5,
    "Ice": 6,
    "Fighting": 7,  
    "Poison": 8,
    "Ground": 9,  
    "Flying": 10, 
    "Psychic": 11, 
    "Bug": 12,
    "Rock": 13, 
    "Ghost": 14, 
    "Dragon": 15, 
    "Dark": 16,
    "Steel": 17, 
    "Fairy": 18
}

types = pd.DataFrame(list(type_ids.items()), columns=['TypeName', 'TypeId'])

#listing out any type effectiveness interactions that aren't 1-1 into a dictionary
effectiveness = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Rock": 2, "Dark": 2, "Steel": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Ghost": 0},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Poison": 2, "Rock": 2, "Steel": 2, "Grass": 0.5, "Bug": 0.5, "Flying": 0},
    "Flying": {"Grass": 2, "Fighting": 2, "Bug": 2, "Electric": 0.5, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Steel": 0.5, "Dark": 0},
    "Bug": {"Grass": 2, "Psychic": 2, "Dark": 2, "Fire": 0.5, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Flying": 2, "Bug": 2, "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5},
    "Ghost": {"Psychic": 2, "Ghost": 2, "Normal": 0},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Psychic": 2, "Ghost": 2, "Fighting": 0.5, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Ice": 2, "Rock": 2, "Fairy": 2, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Steel": 0.5},
    "Fairy": {"Fighting": 2, "Dragon": 2, "Dark": 2, "Fire": 0.5, "Poison": 0.5, "Steel": 0.5}
}

#Create the type effectivness
type_effectiveness = pd.DataFrame([ #convert results to df
    {
        "TypeEffectivenessId": idx + 1,
        "AttackingTypeId": type_ids[atk],
        "DefendingTypeId": type_ids[defn],
        "Effectiveness": effectiveness.get(atk, {}).get(defn, 1)
    }
    
    #iterate through all possible pairs of attacking - defending types
    for idx, (atk, defn) in enumerate(itertools.product(type_ids.keys(), repeat=2))
])

#dictionary of dictionaries storage
individual_pages = {}

#for every pokemon get their specific page info
for idx, row in pokedex.iterrows():
  pokedex_nbr = row['PokedexNbr']
  url = f'https://pokemondb.net/pokedex/{pokedex_nbr}'
  tables_data = scrape_individual_page_data(url)
  clean_tables = clean_individual_page_data(tables_data)

  individual_pages[pokedex_nbr] = {
        f'df_{i+1}': df for i, df in enumerate(clean_tables)
    }

individual_entries = []

for pokedex_nbr, dfs in individual_pages.items():
  df = dfs.get('df_1')
  individual_entries.append(df)

individual_entries = pd.concat(individual_entries)

#create breeding table
breeding = individual_entries[['MalePerc', 'FemalePerc', 'EggCycles', 'EggGroup1', 'EggGroup2']]

#get distinct egg groups
egg_groups = pd.unique(breeding[['EggGroup1', 'EggGroup2']].values.ravel('K'))

egg_groups = pd.DataFrame(data = egg_groups, columns = ['EggGroupDesc'])
egg_groups = egg_groups.sort_values(by = 'EggGroupDesc', na_position = 'first')
egg_groups['EggGroupId'] = range(len(egg_groups))



