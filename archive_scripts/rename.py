import pandas as pd

from sudulunu.helpers import pp, dumper

old = pd.read_csv('fs/combined.csv')
# ['Title', 'Url', 'Standfirst', 'Date']

# published,title,description,link,Pub

old.rename(columns={'Date': "published", 'Title': 'title', 'Standfirst': 'description', 'Url': "link"}, inplace=True)

dumper('fs', 'combined', old)

pp(old)