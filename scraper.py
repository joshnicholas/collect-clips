
# #%%
import pandas as pd 
import feedparser

import pathlib
import os 

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