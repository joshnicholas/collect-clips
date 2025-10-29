import requests
from bs4 import BeautifulSoup as bs
import datetime 
import re 

import pandas as pd 
from sudulunu.helpers import pp, dumper, rand_delay

import pathlib
import os 

#  #%%

# pathos = pathlib.Path(__file__).parent
os.chdir('/Users/josh_nicholas/Personal/collect-clips/')

print(os.getcwd())

pattern = re.compile(r"/(\d{4})/([a-z]{3})/(\d{2})/", re.IGNORECASE)

excuse = ['https://www.theguardian.com/australia-news/2021/apr/13/its-become-all-consuming-how-andrew-denton-went-from-tv-presenter-to-assisted-dying-advocate']

for count in range(70, 88):
# for count in range(1, 88):
# for count in range(1, 2):
    print("Count: ", count)

    pathos = f"https://www.theguardian.com/australia-news/series/full-story?page={count}"
    r = requests.get(pathos)



    soup = bs(r.text, 'html.parser')


    # ahs = soup.find_all('a', attrs={"data-link-name":"media"})

    ahs = soup.find_all('div', class_='dcr-11l4sjk')

    records = []

    for thingo in ahs:
        # print(thingo.text)
        # print(thingo.a['href'])

        try:

            datto = datetime.datetime.strptime("-".join(re.search(r"/(\d{4})/([a-z]{3})/(\d{1,2})/",thingo.a['href']).groups()), "%Y-%b-%d").strftime("%Y-%m-%d")
            # try:
            #     standfirst = thingo.find("div", class_='dcr-oi4shr').text
            # # print(standfirst.text)
            #     print(standfirst)
            # except:
            #     standfirst = ""

            r2 = requests.get(f"https://www.theguardian.com{thingo.a['href']}")

            new_soup = bs(r2.text, 'html.parser')

            standfirst = new_soup.find('div', attrs={"style":"--grid-area:standfirst"}).text.replace("\n", " ").strip()

            title = thingo.a['aria-label'].replace("– Full Story podcast", " ").replace("\n", " ").strip()

            # print(title,f"https://www.theguardian.com{thingo.a['href']}" )

            contributors = new_soup.find("address", attrs={"aria-label": "Contributor info"}).text.replace("\n", " ").strip()



            # print(title)

            # print(find.text)
            # print(contributors.text)

            record = {"title": title,
                    "link": "https://www.theguardian.com" +thingo.a['href'],
                    "description": standfirst, 
                    "published": datto,
                    "contributors": contributors }

            records.append(record)

            rand_delay(1)

        except Exception as e:
            if f"https://www.theguardian.com{thingo.a['href']}" in excuse:
                continue
            else:
                print(title,f"https://www.theguardian.com{thingo.a['href']}" )
                print(e)
                break

    new = pd.DataFrame.from_records(records)

    dumper('fs', f"page_{count}", new)

    rand_delay(3)

# pp(new)



# # %%

def combine(path, sort_col, drop_col):

    iterrer = pathlib.Path(path)
    fillos = list(iterrer.rglob("*.csv"))

    listo = []
    for fillo in fillos:
        inter = pd.read_csv(fillo)
        listo.append(inter)

    combined = pd.concat(listo)
    combined.sort_values(by=[sort_col], ascending=False, inplace=True)
    combined.drop_duplicates(subset=[drop_col], keep='last', inplace=True)

    dumper(path, 'combined', combined)

combine('fs', 'published', 'link')