"""
Create a json dictionary of player ids:names from the cricinfo html
"""

import re
import json
import requests


def get_html(style, discipline):
    # top 200 test run scorers with average > 35
    if style == 'test':
        html = requests.get('http://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;filter=advanced;orderby=runs;qualmin1=35;qualval1=batting_average;size=200;template=results;type=batting').text
    # top 100 odi run scorers with average > 30
    if style == 'odi':
        html = requests.get('http://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;filter=advanced;orderby=runs;qualmin1=30;qualval1=batting_average;size=100;template=results;type=batting').text
    with open(f'data/{discipline}/{style}/html.txt', 'w') as file:
        file.write(html)


def create_player_dict(style, discipline):
    """create dict linking names and cricinfo ids from html and store as json"""
    get_html(style, discipline)
    path = f'data/{discipline}/{style}/html.txt'
    destination = f'data/{discipline}/{style}/ids_names.json'

    with open(path) as file:
        contents = file.read()
        match_regex = re.compile(r'/content/player/(\d*).html" class="data-link">(.*)</a>')
        ids_names = dict(match_regex.findall(contents))

    with open(destination, 'w') as file:
        json.dump(ids_names, file)

    return ids_names
