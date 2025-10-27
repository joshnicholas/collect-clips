
# #%%
import pandas as pd 
import feedparser

import pathlib
import os 
import re
import requests
from bs4 import BeautifulSoup as bs
import datetime 
# #%%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

# #%%

def parse_rss(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        items.append({
            "published": entry.get("published", ""),
            "title": entry.get("title", ""),
            "description": entry.get("description", ""),
            "link": entry.get("link", "")
        })
    return pd.DataFrame.from_records(items)

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)


def make_old(out_path, stem, column_names):
    if not os.path.isfile(out_path):
        empty_df = pd.DataFrame(columns=column_names)
        dumper(out_path, stem, empty_df)


feeds = [
    ("ABC", 'https://www.youtube.com/feeds/videos.xml?channel_id=UCVgO39Bk5sMo66-6o6Spn6Q'),
    ("7News", 'https://www.youtube.com/feeds/videos.xml?channel_id=UC5T7D-Dh1eDGtsAFCuwv_Sw'),
    ('9News', 'https://www.youtube.com/feeds/videos.xml?channel_id=UCIYLOcEUX6TbBo7HQVF2PKA'),
    ("Sky News Australia", 'https://www.youtube.com/feeds/videos.xml?channel_id=UCO0akufu9MOzyz3nvGIXAAw'),
    ("10 News", 'https://www.youtube.com/feeds/videos.xml?channel_id=UC64A-bbH15b5kN5A32CErOA')
]


for thingo in feeds:

    inter = parse_rss(thingo[1])

    cols = inter.columns.tolist()

    already_done = os.listdir('data')

    make_old('data',thingo[0], cols)

    old = pd.read_csv(f'data/{thingo[0]}.csv')

    tog = pd.concat([old, inter])

    for col in ['title', 'description']:
        tog[col] = tog[col].str.strip().str.replace("\n", ' ')

    tog['Pub'] = thingo[0]

    tog.sort_values(by=['published'], ascending=True, inplace=True)
    tog.drop_duplicates(subset=['link'], keep='last', inplace=True)

    dumper('data',thingo[0], tog)


iterrer = pathlib.Path('data')
fillos = list(iterrer.rglob("*.csv"))

listo = []
for fillo in fillos:
    inter = pd.read_csv(fillo)
    listo.append(inter)

combined = pd.concat(listo)
combined.sort_values(by=['published'], ascending=False, inplace=True)
combined.drop_duplicates(subset=['link'], keep='last', inplace=True)

dumper('data', 'combined', combined)


### Scrape full story

pattern = re.compile(r"/(\d{4})/([a-z]{3})/(\d{2})/", re.IGNORECASE)

# for count in range(1, 88):
for count in range(1, 2):
    # print("Count: ", count)

    pathos = f"https://www.theguardian.com/australia-news/series/full-story?page={count}"
    r = requests.get(pathos)



    soup = bs(r.text, 'html.parser')


    # ahs = soup.find_all('a', attrs={"data-link-name":"media"})

    ahs = soup.find_all('div', class_='dcr-11l4sjk')

    records = []

    for thingo in ahs:
        # print(thingo.text)
        # print(thingo.a['href'])

        datto = datetime.datetime.strptime("-".join(re.search(r"/(\d{4})/([a-z]{3})/(\d{1,2})/",thingo.a['href']).groups()), "%Y-%b-%d").strftime("%Y-%m-%d")
        try:
            standfirst = thingo.find("div", class_='dcr-oi4shr').text
        # print(standfirst.text)
            # print(standfirst)
        except:
            standfirst = ""

        record = {"Title": thingo.text,
                "Url": "https://www.theguardian.com" +thingo.a['href'],
                "Standfirst": standfirst, 
                "Date": datto }

        records.append(record)

    new = pd.DataFrame.from_records(records)
    old = pd.read_csv('fs/combined.csv')
    
    tog = pd.concat([old, new])
    tog.sort_values(by=['Date'], ascending=False, inplace=True)
    tog.drop_duplicates(subset=['Url'], inplace=True)

    dumper('fs', 'combined', tog)
    # dumper('fs', f"page_{count}", new)

    # rand_delay(5)

# pp(new)