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

#call comprehensive scrape functions
pokedex = scrape_pokedex_data('https://pokemondb.net/pokedex/all')
moves = scrape_move_data('https://pokemondb.net/move/all')
abilities = scrape_ability_data('https://pokemondb.net/ability')
