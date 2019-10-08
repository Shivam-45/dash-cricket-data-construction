"""
Create a list of player ids from the webpage source code
"""

import re
import json
import requests

def get_html():
    #top 100 test run scorers with average > 35
    if style == 'test':
        html = requests.get('http://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=runs;qualmin1=35;qualval1=batting_average;size=200;template=results;type=batting').text
    #top 100 odi run scorers with average > 30
    if style == 'odi':
        html = requests.get('http://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;filter=advanced;orderby=runs;qualmin1=30;qualval1=batting_average;size=100;template=results;type=batting').text
    with open(f'data/{discipline}/{style}/html.txt', 'w') as file:
        file.write(html)
        
def create_ids():
    """create list of ids from cricinfo html and store as json"""
    path = f'data/{discipline}/{style}/html.txt'
    destination = f'data/{discipline}/{style}/ids.json'

    with open(path) as file:
        contents = file.read()
        match_regex = re.compile(r'/content/player/(\d*)')
        ids = list(match_regex.findall(contents))

    with open(destination, 'w') as file:
        json.dump(ids, file)

    return ids

def create_ids_names():
    """create dict linking names and cricinfo ids from html and store as json"""
    path = f'data/{discipline}/{style}/html.txt'
    destination = f'data/{discipline}/{style}/ids_names.json'
    destinationb = f'data/{discipline}/{style}/ids_nations.json'

    with open(path) as file:
        contents = file.read()
        match_regex = re.compile(r'/content/player/(\d*).html" class="data-link">(.*)</a>')
        ids_names = dict(match_regex.findall(contents))
        match_regex = re.compile(r'/content/player/(\d*).html" class="data-link">.*</a>.*\((.*)\)</td>')
        ids_nations = dict(match_regex.findall(contents))

    with open(destination, 'w') as file:
        json.dump(ids_names, file)
    
    with open(destinationb, 'w') as file:
        json.dump(ids_nations, file)

    return ids_names

style = 'test'
discipline = 'batting'
get_html()
create_ids_names()
