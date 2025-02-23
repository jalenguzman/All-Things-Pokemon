#load libraries
import pandas as pd
import requests #requests.get()
from bs4 import BeautifulSoup #soup.find() #BeautifulSoup()
import re #re.findall() #re.search()
import itertools #itertools.product()
from functools import reduce #reduce()

def get_request_response(url):
  """
  Gets information on the requested URL.
  @param url: the url (str) of the webpage we want information for
  @returns: Response.response.object from url.
  """

  response = requests.get(url, timeout = 10) #gives 10s to give response
  if response.status_code != 200: #only status code that we accept
    raise Exception(f"Failed to load page {url}")
  return response

def transpose_df(df):
  """
  Transposes a dataframe object and does some preprocessing.
  @param df: a dataframe that needs to be transposed and column names to be set for it
  @returns: transposed version of dataframe given.
  """

  df = df.transpose()
  df.columns = df.iloc[0] #set column names to values in row 1
  df = df[1:] #remove row 1
  return df

##### Scraping Data From WebPages Functions #####

def scrape_pokedex_data(url):
  """
  Used to get basic information from the table on PokemonDB.net/pokedex.
  @param url: 'https://pokemondb.net/pokedex'
  @returns: A dataframe of all pokemon, their variant forms, and basic information about them
  """

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
  """
  Used to get basic information from the table on PokemonDB.net/move/all
  @param url: 'https://pokemondb.net/move/all'
  @returns: A dataframe of all pokemon moves and basic information about them
  """

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
  """
  Used to get basic information from the table on PokemonDB.net/ability
  @param url: 'https://pokemondb.net/ability'
  @returns: A dataframe of all pokemon abilities and basic information about them
  """

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

def scrape_evolution_data(url):
  """
  Scrapes evolution data from the given URL.
  @param url: 'https://pokemondb.net/evolution/'
  @returns: A dictionary where keys are evolution page URLs and elements are dfs of different evo chains
  """
  
  response = get_request_response(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  nav = soup.find('nav', class_='panel panel-nav')  #Find navigator panel full of subpages
  links = nav.find_all('a', href=True)  #get all links in navigator panel
  
  #empty dictionary to store eventual return data
  evolution_dict = {}  
  
  #pretending I'm not looking at a triple for loop
  for link in links:
      ending = link.get('href')
      if ending == '/evolution/none': #if url is for evolution page for pokemon without evos
          continue  #Skip
  
      full_url = f'https://pokemondb.net{ending}'  #Combine URL
  
      #scrape
      response = get_request_response(full_url)  
      soup = BeautifulSoup(response.content, 'html.parser')
      table = soup.find('table', {'id': 'evolution'})  
  
      if not table:
          continue  # Skip if no table is found
  
      evolution_data = []
      
      #columns and rows data
      headers = [header.text.strip() for header in table.find('thead').find_all('th')]
      rows = table.find('tbody').find_all('tr')
      
      #iterate through rows and set them into columns (depending on header)
      for row in rows:
          cells = row.find_all('td')
          chains = {}

          for i in range(len(headers)):
              if headers[i] == 'Evolving from': #specific actions for data in 'Evolving from' column
                  name_cell = cells[i]
                  name = name_cell.find('a').text.strip()
                  subname = name_cell.find('small').text.strip() if name_cell.find('small') else None
                  chains['Evolving From Name'] = name
                  chains['Evolving From Subname'] = subname
              elif headers[i] == 'Evolving to':  
                  name_cell = cells[i]
                  name = name_cell.find('a').text.strip()
                  subname = name_cell.find('small').text.strip() if name_cell.find('small') else None
                  chains['Evolving To Name'] = name
                  chains['Evolving To Subname'] = subname
              else:
                  chains[headers[i]] = cells[i].text.strip()
          
          evolution_data.append(chains)  #Append row data

      df = pd.DataFrame(evolution_data)  #convert collected info into df
      evolution_dict[ending] = df  #Set into dict
  
  return evolution_dict

def scrape_individual_page_data(url):
  """
  Central Control for Scraping information from an individual pokemon's pokedex page
  @param url: f'https://pokemondb.net/pokedex/{number or name}'
  @returns: Dictionary with 4 items: Forms, Flavor Text, Evolution Chains, and Moves
  """

  response = get_request_response(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  tables_dict = {}

  tables_dict['Forms'] = scrape_forms_data(soup) #Scrape forms data
  tables_dict['Flavor Text'] = scrape_flavor_text(soup) #Scrape flavor text from pokemon entries
  tables_dict['Moves'] = scrape_moves_data(soup) #Scrape moves data

  return tables_dict

def scrape_forms_data(soup):
  """
  Scrapes data from Pokemon's individual page (Pokedex, Training, and Breeding Tables) for all its possible variants
  @param soup: The HTML parsed BeautifulSoup content from the pokemon's individual page url
  @returns: dictionary where each key represents a pokemon's variant and contains pokedex, training, and breeding data
  """  

  form_tab_container = soup.find('div', {'class': 'tabset-basics'})
  form_tabs = form_tab_container.select('a.sv-tabs-tab') if form_tab_container else []
  form_data = {}

  for tab in form_tabs:
      form_name = tab.text.strip()
      form_id = tab['href'].replace('#', '')  # e.g., 'tab-basic-475'
      form_div = soup.find('div', {'id': form_id})

      if not form_div:
          continue  # Skip if the form's div is not found

      # Scrape data for this form
      form_tables = {}
      headers_of_interest = ["Pokédex data", "Training", "Breeding"]
      headers = form_div.find_all(['h2', 'h3'])

      for header in headers:
          header_text = header.text.strip()
          if header_text in headers_of_interest:
              table = header.find_next('table')
              if table:
                  rows = table.find_all('tr')
                  table_data = []
                  for row in rows:
                      cells = row.find_all(['td', 'th'])
                      cell_data = [cell.text.strip() for cell in cells]
                      
                      #Handle abilities piece specifically so we can separate them out later
                      if header_text == "Pokédex data" and "Abilities" in cell_data:
                          #Extract abilities and join them with a delimiter
                          abilities = []
                          ability_cells = row.find_all('td')
                          for ability_cell in ability_cells:
                              ability_links = ability_cell.find_all('a')
                              for link in ability_links:
                                  abilities.append(link.text.strip())
                          #add delimiter
                          cell_data = ["Abilities", "|".join(abilities)]
                      
                      table_data.append(cell_data)
                  # Ensure all rows have the same number of columns
                  max_columns = max(len(row) for row in table_data)
                  table_data = [row + [''] * (max_columns - len(row)) for row in table_data]
                  df = pd.DataFrame(table_data)
                  form_tables[header_text] = df
      
      # Extract artwork URL
      
      img_tag = form_div.find('img', {'alt': re.compile(r'.artwork')})
      img_url = img_tag['src'] if img_tag else None
      form_tables['Artwork'] = img_url

      # Store the form's data
      form_data[form_name] = form_tables
      
  return form_data

def scrape_flavor_text(soup):
  """
  Scrapes data from Pokemon's Pokedex Entries (akaed here as Flavor Text)
  @param soup: The HTML parsed BeautifulSoup content from the pokemon's individual page url
  @returns: dictionary where each key represents a pokemon's variant and contains the flavored text
  """

  header = soup.find('h2', string = 'Pokédex entries')
  
  flavor_text = {}
  if header:
    table = header.find_next('table')
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
    flavor_text['Flavor Text'] = df
  
  else:
    data = {'Game': ['None'],
            'Flavor Text': ['Pokemon has no pokedex entry']}
    df = pd.DataFrame(data)
    flavor_text['Flavor Text'] = df
  
  return flavor_text

def scrape_moves_data(soup):
  """
  Scrapes data about Pokemon's available moves
  @param soup: The HTML parsed BeautifulSoup content from the pokemon's individual page url
  @returns: dictionary where each key represents a specific game and what moves the pokemon can learn in that game
  """

  move_tab_container = soup.find('div', {'class': 'tabset-moves-game sv-tabs-wrapper'})
  move_tabs = move_tab_container.select('a.sv-tabs-tab') if move_tab_container else []
  move_data = {}

  for tab in move_tabs:
      tab_name = tab.text.strip()
      tab_id = tab['href'].replace('#', '')  # e.g., 'tab-moves-21'
      tab_div = soup.find('div', {'id': tab_id})

      if not tab_div:
          continue  # Skip if the tab's div is not found

      # Scrape move tables for this tab
      move_tables = []
      tables = tab_div.find_all('table', {'class': 'data-table'})

      for table in tables:
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
          move_tables.append(df)

      # Store the move data for this tab
      move_data[tab_name] = move_tables

  return move_data

#### Cleaning Scraped Dictionaries and Converting to easier to handle DataFrame Functions #####

def clean_individual_page_data(tables_data):
  """
  Control Center for calling functions that can clean the data coming from a pokemon's individual pokedex page
  @param tables_data: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dictionary where the first key is a mega table with most scraped data and the second key is the Pokemon's move data. Both keys are dfs
  """

  artwork_url = clean_artwork_data(tables_data) #artwork
  entry_data = clean_pokedex_entry_data(tables_data) #pokedex
  training_data = clean_training_data(tables_data) #training
  breeding_data = clean_breeding_data(tables_data) #breeding
  flavor_text_data = clean_pokedex_flavor_text_data(tables_data) #flavor text
    
  #evolution_data = clean_evolution_data(tables_data) #evolution
  move_data = clean_move_data(tables_data) #moves

  #combine as needed for sql table storage
  dfs = [entry_data, training_data, breeding_data, artwork_url]
  merged = reduce(lambda left, right: pd.merge(left, right, on = 'Name', how = 'left'), dfs)
    
  flavor_text_data = pd.concat([flavor_text_data] * len(merged), ignore_index=True) #add enough rows in order to add onto merged
  merged = pd.concat([merged.reset_index(drop=True), flavor_text_data.reset_index(drop=True)], axis=1) #add flavor text to merged

  return merged, move_data

def clean_artwork_data(dict):
  """
  Converts Dictionary with Artwork data into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with ArtworkURL as the main column (# of rows equal to number of variants specific Pokemon has)
  """

  column_names = ['Name', 'ArtworkURL'] #set names of columns for returning df
  main_dict = {} #create empty df to hold items in intermediate phase
  
  for key in dict['Forms']: #for each pokemon variant
    if bool(dict['Forms'][key]) == False:
      continue
    
    main_dict[key] = dict['Forms'][key]['Artwork'] #extract needed info
  
  df = pd.DataFrame(main_dict.items(), columns = column_names) #rowbind all elements extracted
  return df

def clean_pokedex_entry_data(dict):
  """
  Converts Dictionary with Pokedex Entry data into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with basic pokemon data (# of rows equal to number of variants specific Pokemon has)
  """

  #predefine columns wanted in the ending df
  column_names = ['Name', 'PokedexNbr', 'Type', 'Species', 'Height', 'Weight', 'Ability1', 'Ability2', 'Ability3']
  main_df = pd.DataFrame(columns = column_names) #create empty df to append to
  
  #for every form at a single pokedex number
  for key in dict['Forms']:
    
    # if there is no form information in the key
    if bool(dict['Forms'][key]) == False: 
      continue #skip to next for loop iteration
    
    if 'ability' in key:
      continue #skip to next loop if tab is for an ability iteration
    
    df = dict['Forms'][key]['Pokédex data']
    df = transpose_df(df)
    
    df['Name'] = key
    df['Height'] = df['Height'].str.split(r'([a-z])').str[0].replace('—', '0').astype(float) #splits off all char info, replace -s with 0s and convert to float
    df['Weight'] = df['Weight'].str.split(r'([a-z])').str[0].replace('—', '0').astype(float)
    df[['Ability1', 'Ability2', 'Ability3']] = df['Abilities'].apply(split_abilities)
    df['PokedexNbr'] = df['National №']
    
    df = df[column_names]
    main_df = pd.concat([main_df.astype(df.dtypes), df.astype(main_df.dtypes)]) #astype used to prevent future warning error
  
  return main_df

def split_abilities(abilities):
  """
  Splits string of abilities by | delimiter into 3 max three column series
  @param abilities: string of abilities with | delimiter for parsing
  @returns: Series where each element represents a distinct Pokemon ability
  """

  abilities_split = abilities.split('|') #split ability string by delimiter
  abilities_split = [ability.strip() for ability in abilities_split] #trim whitespace
    
  return pd.Series(abilities_split + [None] * (3 - len(abilities_split)))

def clean_training_data(dict):
  """
  Converts Dictionary with Pokemon's Training data into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with training data (# of rows equal to number of variants specific Pokemon has)
  """

  #predefine columns wanted in the ending df
  column_names = ['Name', 'CatchRatePerc', 'BaseFriendship', 'BaseExp', 'GrowthRate', 'EVYield']
  main_df = pd.DataFrame(columns = column_names) #create empty df to append to
  
  for key in dict['Forms']:
    
    if bool(dict['Forms'][key]) ==False:
      continue
    
    if 'ability' in key:
      continue #skip to next loop if tab is for an ability interaction (ex: Pokemon with Water Absorb will have additional forms but on their type weaknesses matrix)
    
    df = dict['Forms'][key]['Training']
    df = transpose_df(df)
    
    df['Name'] = key
    df['CatchRatePerc'] = df['Catch rate'].str.split('(').str[0].replace('—', '0').astype(float) #splits off all char info, replace -s with 0s and convert to float
    df['BaseFriendship'] = df['Base Friendship'].str.split('(').str[0].replace('—', '0').astype(float)
    df['BaseExp'] = df['Base Exp.'].replace('—', '0').astype(float)

    df.rename(columns=
    {'EV yield': 'EVYield',
     'Growth Rate': 'GrowthRate'}, inplace=True)

    df = df[column_names]
    main_df = pd.concat([main_df.astype(df.dtypes), df.astype(main_df.dtypes)])
    
  return main_df

def clean_breeding_data(dict):
  """
  Converts Dictionary with Pokemon's Breeding data into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with breeding data (# of rows equal to number of variants specific Pokemon has)
  """
  
  column_names = ['Name', 'MalePerc', 'FemalePerc', 'EggCycles', 'EggGroup1', 'EggGroup2']
  main_df = pd.DataFrame(columns = column_names)
  
  for key in dict['Forms']:
    
    if bool(dict['Forms'][key]) == False:
      continue
    
    if 'ability' in key:
      continue #skip to next loop if tab is for an ability iteration

    
    df = dict['Forms'][key]['Breeding']
    df = transpose_df(df)
  
    df['Name'] = key
    if df['Gender'].str.contains('Genderless|—').any(): #need different logic for genderless pokemon
      df['MalePerc'] = 0 #can just automatically set male and female perc to 0
      df['FemalePerc'] = 0
    else: #otherwise use data from dictionary
      df[['MalePerc', 'FemalePerc']] = df['Gender'].str.split(',', expand=True)
      df['MalePerc'] = df['MalePerc'].str.split('%').str[0].astype(float)
      df['FemalePerc'] = df['FemalePerc'].str.split('%').str[0].astype(float)

    df['EggCycles'] = df['Egg cycles'].str.split('(').str[0].replace('—', '0').astype(float)
    df[['EggGroup1', 'EggGroup2']] = df['Egg Groups'].str.split(',', expand=True).reindex(columns=[0, 1])
    df['EggGroup1'] = df['EggGroup1'].str.strip()
    df['EggGroup2'] = df['EggGroup2'].fillna('').str.strip() #when there is no second egg group (NA) fill with blank value

    df = df[column_names]
    main_df = pd.concat([main_df.astype(df.dtypes), df.astype(main_df.dtypes)])
    
  return main_df

def clean_pokedex_flavor_text_data(dict):
  """
  Converts Dictionary with Pokedex Flavor Text data into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with pokemon's flavor text (# of rows equal to number of variants specific Pokemon has)
  """
  
  df = pd.DataFrame(dict['Flavor Text']['Flavor Text'])
  
  df.columns = ['Game', 'FlavorText']
  df = df.tail(1) #select last row
  df = df[['FlavorText']] #only select one column
  
  return df

def clean_move_data(dict):
  """
  Converts Dictionary with Pokemon's Available Moves into Dataframe
  @param dict: the result of scrape_individual_page_data / the - hopefully - successfully HTML data scraped into dictionaries and dfs
  @returns: dataframe with all pokemon's available moves across recent games
  """

  column_names = ['MoveName']
  main_df = pd.DataFrame(data = ['Move'], columns = column_names)
  
  for key in dict['Moves']:
    for item in range(len(dict['Moves'][key])):
      df = pd.DataFrame(dict['Moves'][key][item])
      df.rename(columns = {'Move': 'MoveName'}, inplace = True)
      df = df[column_names]
      
      main_df = pd.concat([main_df, df])
  
  main_df = main_df.drop_duplicates() #only return distinct move names
  
  return main_df

##### Augmenting Dataframes with new ETL created columns or creating said columns Functions #####

def get_special_pokemon(choice):
  """
  Returns A list of pokemon under a special categorization
  @param choice: 'Sublegendary', 'Legendary', 'Mythical' - semi fan generated categories for specific pokemon
  @returns: returns list of Pokemon names for any of the different special pokemon categories
  """

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
  """
  Returns the generation the pokemon was introduced to depending on it's PokedexNbr
  @param PokedexNbr: string value of the Pokemon's position in the national dex
  @returns: number representing the pokemon's introduction generation
  """

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
  """
  Returns a String (The Move Category) depending on jpg string entered
  @param cat: a string that should reference one of the below .jpg image files
  @returns: a simple move category string
  """

  match cat:
    case 'https://img.pokemondb.net/images/icons/move-special.png':
      return 'Special'
    case 'https://img.pokemondb.net/images/icons/move-status.png':
      return 'Status'
    case 'https://img.pokemondb.net/images/icons/move-physical.png':
      return 'Physical'
    case _:
      return 'None'

def augment_pokedex_data(pokedex):
  """
  Augments Basic Pokedex Information
  @param pokedex: dataframe of General Pokedex info (Name, Typing, and Base Stats)
  @returns: pokedex dataframe with additional formatting and columns attached
  """

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
  """
  Augments General Move Data Table
  @param moves: dataframe of general move info (Move Name, Move Type, etc.)
  @returns: moves dataframe with additional formatting and columns attached
  """

  moves['Category'] = moves['Cat.'].apply(get_move_category)
  moves['MoveRowId'] = moves.index + 1 #create primary key
  
  #mainly renaming stuff
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
  moves = moves.replace('—', None) #replace just -s with nulls
  
  return moves

def augment_ability_data(abilities):
  """
  Augments General Ability Data Table
  @param abilities: dataframe of general ability info (Ability Name, Desc, etc.)
  @returns: abilities dataframe with additional formatting and columns attached
  """

  abilities['AbilityRowId'] = abilities.index + 1 #create primary key
  abilities.rename(columns =
     {'Name': 'AbilityName', #rename columns to match wanted SQL columns
      'Description': 'AbilityDesc',
      'Gen.': 'IntroGen'}, inplace = True)
      
  abilities = abilities[['AbilityRowId', 'AbilityName', 'AbilityDesc', 'IntroGen']]
  
  return abilities

##### Create near finalized tables for to SQL Functions #####

def create_move_category_table(moves):
  """
  Creates Table for dbo.MoveCategory
  @param moves: dataframe with all pokemon moves
  @returns: table with only a unique list of move categories
  """

  move_category = pd.DataFrame()
  move_category['MoveCategoryDesc'] = moves['Category'].unique()
  move_category = move_category.sort_values(by = 'MoveCategoryDesc')
  move_category['MoveCategoryId'] = range(len(move_category))
  
  return move_category

def create_base_stats_table(pokedex):
  """
  Creates Table for dbo.BaseStats
  @param moves: dataframe with all pokemon variants and their base stats
  @returns: table with the base stats of each pokemon variant
  """
  base_stats = pokedex[['PokedexRowId', 'HP', 'Atk', 'Def', 'SpAtk', 'SpDef', 'Speed', 'Total']]
  
  return base_stats

def get_type_ids():
  """
  Creates Dictionary of Different Pokemon Types
  @param null
  @returns: dictionary that associates every pokemon type with a number
  """

  type_ids = {
    None: 0,
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
  
  return type_ids
  
def create_type_table():
  """
  Creates Table for dbo.Type
  @param null
  @returns: Dataframe with each type and a type id
  """
  
  type_ids = get_type_ids()
  types = pd.DataFrame(list(type_ids.items()), columns=['TypeName', 'TypeId'])
  
  return types

def create_type_effectiveness_table():
  """Creates Table for dbo.TypeEffectiveness
  @param null
  @returns: table describing the relationship between attacking and defending types
  """
  
  type_ids = get_type_ids()
  
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
  
  return type_effectiveness

def create_breeding_table(df):
  """
  Creates Table for dbo.Breeding
  @param dataframe that contains Pokemon and their breeding data
  @returns: table with all the breeding info for each pokemon variant
  """
  
  breeding = df[['PokedexRowId', 'MalePerc', 'FemalePerc', 'EggCycles', 'EggGroup1', 'EggGroup2']]
  return breeding

def create_egg_group_table(breeding):
  """
  Creates Table for dbo.EggGroup
  @param dataframe of all Pokemon's breeding information
  @returns: table listing out the possible egg groups Pokemon can have
  """
  
  #get distinct egg groups
  egg_groups = pd.unique(breeding[['EggGroup1', 'EggGroup2']].values.ravel('K'))
  
  egg_groups = pd.DataFrame(data = egg_groups, columns = ['EggGroupDesc'])
  egg_groups = egg_groups.sort_values(by = 'EggGroupDesc', na_position = 'first')
  egg_groups['EggGroupId'] = range(len(egg_groups))
  
  return egg_groups

def create_training_table(df):
  """
  Creates Table for dbo.Training
  @param dataframe that contains all Pokemon's training information
  @returns: table listing out the possible egg groups Pokemon can have
  """
  
  #the goal is to convert EVYield into separate columns
  #create dictionary to match stat names to column names
  stat_mapping = {
    'HP': 'HPYield',
    'Attack': 'AtkYield',
    'Defense': 'DefYield',
    'Sp. Atk': 'SpAtkYield',
    'Sp. Def': 'SpDefYield',
    'Speed': 'SpdYield'
  }
  
  for col in stat_mapping.values():
    df[col] = 0 #set all the values to 0s initially
  
  #defining a function in a function for fun
  def extract_stat_values(row):
    matches = re.findall(r'(\d+) (HP|Attack|Defense|Sp\. Atk|Sp\. Def|Speed)', row)
    return {stat_mapping[stat]: int(value) for value, stat in matches}

  for index, row in df.iterrows(): #for every row
    stat_values = extract_stat_values(row['EVYield']) #extract data from stat with applied function
    for col, value in stat_values.items():
        df.at[index, col] = value
  
  #select wanted columns
  training = df[['PokedexRowId', 'CatchRatePerc', 'BaseFriendship', 'BaseExp', 'GrowthRate', 
                  'HPYield', 'AtkYield', 'DefYield', 'SpAtkYield', 'SpDefYield', 'SpdYield']]
                  
  return training

def create_pokedex_table(df):
  """
  Creates Table for dbo.Pokedex
  @param dataframe that contains all Pokemon's basic pokedex information
  @returns: table that will be central to sql database
  """
  
  type_ids = get_type_ids()
  df = df.replace({'Type1': type_ids, 'Type2': type_ids})
  
  df.rename(columns =
    {'Type1': 'PokemonType1Id',
     'Type2': 'PokemonType2Id'}, inplace = True)
  
  #really just sorting out columns to only those wanted
  pokedex = df[['PokedexRowId', 'PokedexNbr', 'PokemonName', 'Subname', 'PokemonType1Id', 'PokemonType2Id', 'Height', 'Weight', 'FlavorText', 'Gen', 
                'IsMega', 'IsRegionVariant', 'IsAdditionalVariant', 'IsSubLegendary', 'IsMythical', 'IsLegendary', 'ArtworkURL']]
                
  return pokedex

#call comprehensive scrape functions
pokedex = scrape_pokedex_data('https://pokemondb.net/pokedex/all')
moves = scrape_move_data('https://pokemondb.net/move/all')
abilities = scrape_ability_data('https://pokemondb.net/ability')

pokedex = augment_pokedex_data(pokedex)
moves = augment_move_data(moves)
abilities = augment_ability_data(abilities)

move_category = create_move_category_table(moves)
base_stats = create_base_stats_table(pokedex)

types = create_type_table()
type_effectiveness = create_type_effectiveness_table()

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
individual_entries['PokedexRowId'] = range(1, len(test) + 1) #add primary key
combined = pd.merge(pokedex, individual_entries, on = ['PokedexNbr', 'PokedexRowId']) #combine with other pokedex information

breeding = create_breeding_table(combined)
egg_groups = create_egg_group_table(breeding)
training = create_training_table(combined)
dex = create_pokedex_table(combined)

#TO DO:
#attach foreign keys
#breeding egggroupnames to egg group groupids
#pokedex typenames to type typeid
#moves category to move category movecategoryid

#create PokemonAbilities and PokemonMoves intermediary tables

#export to sql
