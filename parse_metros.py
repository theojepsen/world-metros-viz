import json
import re
import os
from bs4 import BeautifulSoup
import urllib
from dbpedia_loader import DbpediaResourceLoader

def tidyStr(s):
    s = s.replace('\n', ' ')
    s = re.sub('\s+', ' ', s)
    s = re.sub('\[[^\]]+\]', '', s)
    if s == 'n/a': return None
    return s

metros = []

wikipedia_page = 'List_of_metro_systems'
if not os.path.isfile(wikipedia_page + '.html'):
    urllib.urlretrieve ("https://en.wikipedia.org/wiki/List_of_metro_systems", wikipedia_page + '.html')

with open(wikipedia_page + '.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

table = soup.findAll('table')[0]

for tr in table.findAll('tr'): # for each row in the table
    cols = tr.findAll('td')
    metro = {}

    if len(cols) == 8:
        col_ofst = 2
        city_a = cols[0].findAll('a')[0]
        # The resource name for the city's wikipedia article:
        metro['city_resource'] = urllib.unquote(city_a['href']).decode('utf8').split('/wiki/')[-1]
        metro['city'] = city_a.text
        metro['country'] = cols[1].findAll('a')[0].text
    elif len(cols) == 6: # nested col for each metro in the city
        col_ofst = 0
        # Use the same city info as the previous metro:
        metro['city_resource'] = metros[-1]['city_resource']
        metro['city'] = metros[-1]['city']
        metro['country'] = metros[-1]['country']
    elif len(cols) == 0: # empty row
        continue
    else:
        raise Exception("Unexpected number of columns in table row")

    metro['name'] = tidyStr(cols[col_ofst].text)
    metro['year_opened'] = int(tidyStr(cols[col_ofst+1].text))

    metro['year_last_expansion'] = tidyStr(cols[col_ofst+2].text)
    try: metro['year_last_expansion'] = int(metro['year_last_expansion'])
    except: pass

    metro['stations'] = tidyStr(cols[col_ofst+3].text)
    try: metro['stations'] = int(metro['stations'])
    except: pass

    metro['length'] = tidyStr(cols[col_ofst+4].text)
    try: metro['length'] = float(metro['length'].split()[0])
    except: pass

    metro['ridership'] = tidyStr(cols[col_ofst+5].text)
    try: metro['ridership'] = float(metro['ridership'].split()[0])
    except: pass

    metros.append(metro)


print "Total metros:", len(metros)

# DBPedia was missing these populations:
missing_city_pop = {
                'Helsinki': 1470552,
                'Gurgaon': 876824,
                'Tehran': 14700000,
                'Rome': 4357041,
                'Rotterdam': 1181284,
                'Kazan': 1216965,
                'Moscow': 11503501,
                'Nizhny Novgorod': 1250619,
                'Novosibirsk': 1567087,
                'Saint Petersburg': 5323300,
                'Samara': 1171598,
                'Yekaterinburg': 1488791,
                'Adana': 1753337,
                'Dnipro': 1460000,
                'Kiev': 3375000,
                }

dbrl = DbpediaResourceLoader()
with dbrl:
    for metro in metros:
        pop = dbrl.getPop(metro['city_resource'])
        metro['city_population'] = pop
        if not pop and metro['city'] in missing_city_pop:
            metro['city_population'] = missing_city_pop[metro['city']]

with open('metros.json', 'w') as f:
    json.dump(metros, f)
