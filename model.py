import pandas as pd
from ast import literal_eval
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print('Generating results from model.py...')

#Importing the relevant datasets locally stored
metadata = pd.read_csv("movies_metadata.csv")
credits_ = pd.read_csv("credits.csv")
keywords = pd.read_csv("keywords.csv")

metadata = metadata.iloc[0:10000,:]
credits_ = credits_.iloc[0:10000,:]
keywords = keywords.iloc[0:10000,:]

# Convert IDs to int. Required for merging
keywords['id'] = keywords['id'].astype('int')
credits_['id'] = credits_['id'].astype('int')
metadata['id'] = metadata['id'].astype('int')

# Merge keywords and credits into your main metadata dataframe
metadata = metadata.merge(credits_, on='id')
metadata = metadata.merge(keywords, on='id')

features = ['cast', 'crew', 'keywords', 'genres']
for feature in features:
    metadata[feature] = metadata[feature].apply(literal_eval)

def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan

def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        #Check if more than 3 elements exist. If yes, return only first three. If no, return entire list.
        if len(names) > 3:
            names = names[:3]
        return names

    #Return empty list in case of missing/malformed data
    return []

metadata['director'] = metadata['crew'].apply(get_director)

features = ['cast', 'keywords', 'genres']
for feature in features:
    metadata[feature] = metadata[feature].apply(get_list)

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

# Apply clean_data function to your features.
features = ['cast', 'keywords', 'director', 'genres']

for feature in features:
    metadata[feature] = metadata[feature].apply(clean_data)

def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

metadata['soup'] = metadata.apply(create_soup, axis=1)

def make_recommendation(query, metadata=metadata):
    new_row = metadata.iloc[-1, :].copy()
    new_row['soup'] = query  # Set the soup to the user's query

    # Convert the single Series to a DataFrame
    new_row_df = pd.DataFrame([new_row])
    
    # Concatenate the new row to the metadata
    metadata_updated = pd.concat([metadata, new_row_df], ignore_index=True)

    # Build count matrix and compute similarity
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(metadata_updated['soup'])

    cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

    sim_scores = list(enumerate(cosine_sim2[-1, :]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    ranked_titles = []
    for i in range(1, 11):
        indx = sim_scores[i][0]
        ranked_titles.append([
            metadata_updated['title'].iloc[indx],
            metadata_updated['imdb_id'].iloc[indx],
            metadata_updated['runtime'].iloc[indx],
            metadata_updated['release_date'].iloc[indx],
            metadata_updated['vote_average'].iloc[indx]
        ])

    return ranked_titles
