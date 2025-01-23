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

#call comprehensive scrape functions
pokedex = scrape_pokedex_data('https://pokemondb.net/pokedex/all')
moves = scrape_move_data('https://pokemondb.net/move/all')
abilities = scrape_ability_data('https://pokemondb.net/ability')


