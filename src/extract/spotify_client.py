import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

load_dotenv()

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('CLIENT_ID'), 
    client_secret=os.getenv('CLIENT_SECRET'))
sp = spotipy.Spotify(auth_manager=auth_manager)


def get_artists_deets(artists_lists): #without top tracks
    artists_df = {
        'id': [], 
        'artist_name': [], 
        'followers': [], 
        'popularity': [], 
        'url': [], 
        'last_updated': []
    }

    for item in artists_lists:
            
            artist_id = item['id']

            current = datetime.now()
            search_result = sp.artist(artist_id=artist_id)

            artists_df['id'].append(artist_id)
            artists_df['artist_name'].append(item['name'])
            artists_df['followers'].append(search_result['followers']['total'])
            artists_df['popularity'].append(search_result['popularity'])
            artists_df['url'].append(search_result['external_urls']['spotify'])
            artists_df['last_updated'].append(current)
    
    return artists_df

def initialize_artists(): #main function that will call other sub functions
    playlist_id = '0fACn1Axw1sBcozazZFbsJ'

    result_playlist = sp.playlist_items(playlist_id=playlist_id)
    
    if result_playlist is None:
        print('No playlist found')
        return
    
    tracks_items = result_playlist['items']
    artists = [] #used as input for get_artists_deets()

    while result_playlist['next']:
        for item in tracks_items:
            artists.extend(item['track']['artists'])

        result_playlist = sp.next(result_playlist)

    print(json.dumps(artists[0], indent = 4))

    #calling get_artists_deets
    artist_df = pd.DataFrame(data=get_artists_deets(artists))

    return artist_df



initialize_artists()








# results_2 = sp.search(q='remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis', type='artist', limit=2)
# artists = results_2['artists']['items']
# while results_2['artists']['next']:
#     results_2 = sp.next(results_2['artists'])
#     artists.extend(results_2['artists']['items'])

# for artist in artists:
#     print(artist['name'])

# genre_results = sp.categories()
# print(genre_results)


