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

def load_albums(artists_ids):
     artist_albums = {
         'album_id': [],
         'album_name': [],
         'artist_id': [],
         'number_tracks': [],
         'release_date': [],
         'url': []
    }
     
     print('Filling album table')
     #BUILDING ARTIST_ALBUM_DF CONTENT
     for spotify_id in artists_ids:
        album_search = sp.artist_albums(artist_id=spotify_id, include_groups='album')
        album_ids = []
        albums_ = set()
        

        album_items = album_search['items']
        while album_search['next']:
            for item in album_items:

                if item['id'] in albums_:
                    continue

                album_ids.append(item['id'])
                albums_.add(item['id'])

                artist_albums['artist_id'].append(spotify_id)
                artist_albums['album_id'].append(item['id'])
                artist_albums['album_name'].append(item['name'])
                artist_albums['number_tracks'].append(item['total_tracks'])
                artist_albums['release_date'].append(item['release_date'])
                artist_albums['url'].append(item['external_urls']['spotify'])
            album_search = sp.next(album_search)
        
     print('Finished creating albums table')
    #TODO: load album_df to databases
     return album_ids

def load_tracks(albums_ids):
    tracks = {
        'track_id': [],
        'album_id': [],
        'disc_number': [],
        'duration_ms': [],
        'url': []
    }

    print('Filling tracks table')

    for album in albums_ids:
        album_search = sp.album_tracks(album_id=album)

        while album_search['next']:
            for track in album_search['items']:
                tracks['track_id'].append(track['id'])
                tracks['album_id'].append(album)
                tracks['track_name'].append(track['name'])
                tracks['duration_ms'].append(track['duration_ms'])
                tracks['url'].append(track['external_urls']['spotify'])

            album_search = sp.next(album_search)

    print('Finished creating tracks table')
    #TODO: load tracks_df to database
    return 

def load_top_tracks(artists_ids):
    top_tracks = {
        'artist_id': [],
        'tracks_ids': [],
        'last_updated': []
    }

    print('Filling top tracks table')

    for artist in artists_ids:
        current = datetime.now()
        top_tracks_search = sp.artist_top_tracks(artist_id=artist)['tracks']
        top_tracks['artist_id'].append(artist)

        temp_top = []
        for tracks in top_tracks_search:
            temp_top.append(tracks['id'])

        top_tracks['tracks_ids'].append(temp_top)
        top_tracks['last_updated'].append(current)

    print('Fnished filling top tracks table')
    #TODO: load top_tracks to database
    return 

#MAKING THE ARTIST DF
def load_artists(artists_ids): 

    artists_df = {
        'artist_id': [], 
        'artist_name': [], 
        'followers': [], 
        'popularity': [], 
        'url': [], 
        'last_updated': [],
    }

    
    print('Filling artist table')
    for spotify_id in artists_ids:

        current = datetime.now()
        #BUILDING ARTIST_DF CONTENT
        artist_search = sp.artist(artist_id=spotify_id)

        artists_df['artist_id'].append(spotify_id)
        artists_df['artist_name'].append(artist_search['name'])
        artists_df['followers'].append(artist_search['followers']['total'])
        artists_df['popularity'].append(artist_search['popularity'])
        artists_df['url'].append(artist_search['external_urls']['spotify'])
        artists_df['last_updated'].append(current)

    print('Finished creating artist df')

    #TODO: load artist_df to database
    return artists_ids

def initialize_artists(): #main function that will call other sub functions
    BATCH_SIZE = 10
    playlist_id = '0fACn1Axw1sBcozazZFbsJ'

    result_playlist = sp.playlist_items(playlist_id=playlist_id)
    
    if result_playlist is None:
        print('No playlist found')
        return
    
    tracks_items = result_playlist['items']
    artists_ids = [] #used as input for get_artists_deets()
    artists_ = set()

    BATCH_NUMBER = 1

    while result_playlist['next']:
        for item in tracks_items:
            for artist in item['track']['artists']:
                 if artist['id'] in artists_:
                      continue
                 artists_ids.append(artist['id'])
                 artists_.add(artist['id'])

                 if len(artists_ids) >= BATCH_SIZE:
                      print('Processing batch number: ', BATCH_NUMBER)
                      load_artists(artists_ids)
                      albums = load_albums(artists_ids)
                      load_top_tracks(artists_ids)
                      load_tracks(albums_ids=albums)
                      print(f'Batch number {BATCH_NUMBER} finished')
                      artists_ids.clear()
                      BATCH_NUMBER += 1
                 

        result_playlist = sp.next(result_playlist)

    return

initialize_artists()