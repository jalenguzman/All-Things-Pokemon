#load libraries
import pandas as pd
import requests #requests.get()
from bs4 import BeautifulSoup #soup.find() #BeautifulSoup()

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
  elif(converted >= 1010):
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
    df['CatchRate'] = df['Catch rate'].str.split('(').str[0].replace('—', '0').astype(float)
    df['BaseFriendship'] = df['Base Friendship'].str.split('(').str[0].replace('—', '0').astype(float)
    df['BaseExp'] = df['Base Exp.'].replace('—', '0').astype(float)

    df.rename(columns=
    {'EV yield': 'EVYield',
     'Growth Rate': 'GrowthRate'}, inplace=True)

    df = df[['EVYield', 'CatchRate', 'BaseFriendship', 'BaseExp', 'GrowthRate']]
    return df

#call comprehensive scrape functions
pokedex = scrape_pokedex_data('https://pokemondb.net/pokedex/all')
moves = scrape_move_data('https://pokemondb.net/move/all')
abilities = scrape_ability_data('https://pokemondb.net/ability')


