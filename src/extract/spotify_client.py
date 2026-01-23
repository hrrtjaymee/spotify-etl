import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from datetime import datetime
import psycopg2
from src.transform.utils import normalize_date

load_dotenv()

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('CLIENT_ID'), 
    client_secret=os.getenv('CLIENT_SECRET'))
sp = spotipy.Spotify(auth_manager=auth_manager)

def load_albums(artists_ids, cursor):
    artist_albums = {
         'album_id': [],
         'album_name': [],
         'artist_id': [],
         'number_tracks': [],
         'release_date': [],
         'album_url': []
    }
     
    print('Filling album table')
    #BUILDING ARTIST_ALBUM_DF CONTENT

    album_ids = []
    albums_ = set()
    for spotify_id in artists_ids:
        try: 
            album_search = sp.artist_albums(artist_id=spotify_id, include_groups='album')
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error for searching albums for artist {spotify_id}') from e

        album_items = album_search['items']
        while True:
            for item in album_items:

                if item['id'] in albums_:
                    continue

                album_ids.append(item['id'])
                albums_.add(item['id'])

                artist_albums['artist_id'].append(spotify_id)
                artist_albums['album_id'].append(item['id'])
                artist_albums['album_name'].append(item['name'])
                artist_albums['number_tracks'].append(item['total_tracks'])
                artist_albums['release_date'].append(normalize_date(item['release_date']))
                artist_albums['album_url'].append(item['external_urls']['spotify'])
            
            if album_search['next']:
                album_search = sp.next(album_search)
            else: 
                break
        
    print('Finished creating albums table')
     
     #loading albums to database
    values = zip(
        artist_albums['artist_id'],
        artist_albums['album_id'],
        artist_albums['album_name'],
        artist_albums['number_tracks'],
        artist_albums['release_date'],
        artist_albums['album_url']
    )

    load_query = '''
        INSERT INTO ALBUM
        (artist_id, album_id, album_name, number_tracks, release_date, album_url) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (album_id) DO NOTHING
        ''' #when an album already exists, do not update the album
    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load album from {spotify_id}') from e
    return album_ids

def load_tracks(albums_ids, cursor):
    tracks = {
        'track_id': [],
        'album_id': [],
        'track_name': [],
        'disc_num': [],
        'track_num': [],
        'duration_s': [],
        'track_url': []
    }

    print('Filling tracks table')

    for album in albums_ids:
        try:
            album_search = sp.album_tracks(album_id=album)
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error when searching for album {album}') from e
        
        while True:
            for track in album_search['items']:
                tracks['track_id'].append(track['id'])
                tracks['album_id'].append(album)
                tracks['track_name'].append(track['name'])
                tracks['disc_num'].append(track['disc_number'])
                tracks['track_num'].append(track['track_number'])
                tracks['duration_s'].append(track['duration_ms']/1000) #turn milliseconds into seconds
                tracks['track_url'].append(track['external_urls']['spotify'])

            if album_search['next']:
                album_search = sp.next(album_search)
            else:
                break

    print('Finished creating tracks table')

    #loading traacks to database
    values = zip(
        tracks['track_id'],
        tracks['album_id'],
        tracks['track_name'],
        tracks['disc_num'],
        tracks['track_num'],
        tracks['duration_s'],
        tracks['track_url'],
    )

    load_query = '''
        INSERT INTO TRACK
        (track_id, album_id, track_name, disc_num, track_num, duration_s, track_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT DO NOTHING
        '''
    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load tracks from album') from e
        
    return 

def load_top_tracks(artists_ids, cursor):
    top_tracks_query = '''
                        INSERT INTO TOP_TRACKS (artist_id, last_updated) 
                        VALUES (%s, %s) RETURNING top_tracks_id
                        '''
    
    track_item_query = '''
                        INSERT INTO TOP_TRACK_ITEM (top_tracks_id, track_id) VALUES (%s, %s)
                        '''
    
    insert_query = '''
                            INSERT INTO TRACK (track_id, track_name, disc_num, track_num, duration_s, track_url) 
                            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (track_id) DO NOTHING
                            '''

    print('Filling top tracks table')

    for artist in artists_ids:
        current = datetime.now()
        try:
            top_tracks_search = sp.artist_top_tracks(artist_id=artist)['tracks']
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error when searching for top tracks for artist {artist}') from e
        
        try:
            cursor.execute(top_tracks_query, (artist, current))
            row = cursor.fetchone()
            if row is None:
                raise ValueError('TOP_TRACKS record not found')
            
            current_id = row[0]

            for track in top_tracks_search:
                values = (
                    track['id'], 
                    track['name'], 
                    track['disc_number'], 
                    track['track_number'], 
                    track['duration_ms']/1000, 
                    track['external_urls']['spotify'])
                cursor.execute(insert_query, values)

                cursor.execute(
                    track_item_query, (current_id, track['id'])
                )
                
        except psycopg2.Error as e:
            raise RuntimeError(f'Failed to load top tracks for artist {artist}') from e

    return 

#MAKING THE ARTIST DF
def load_artists(artists_ids, cursor): 

    artists_df = {
        'artist_id': [], 
        'artist_name': [], 
        'followers': [], 
        'popularity': [], 
        'artist_url': [], 
        'last_updated': [],
    }

    
    print('Filling artist table')
    for spotify_id in artists_ids:

        current = datetime.now()
        #BUILDING ARTIST_DF CONTENT

        try:
            artist_search = sp.artist(artist_id=spotify_id)
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error when searching for artist {spotify_id}') from e

        artists_df['artist_id'].append(spotify_id)
        artists_df['artist_name'].append(artist_search['name'])
        artists_df['followers'].append(artist_search['followers']['total'])
        artists_df['popularity'].append(artist_search['popularity'])
        artists_df['artist_url'].append(artist_search['external_urls']['spotify'])
        artists_df['last_updated'].append(current)

    print('Finished creating artist df')

    #loading artists to database
    values = zip(
        artists_df['artist_id'],
        artists_df['artist_name'],
        artists_df['followers'],
        artists_df['popularity'],
        artists_df['artist_url'],
        artists_df['last_updated']
    )

    load_query = '''
        INSERT INTO ARTIST 
        (artist_id, artist_name, followers, popularity, artist_url, last_updated) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (artist_id) DO UPDATE
        SET 
            followers = EXCLUDED.followers,
            popularity = EXCLUDED.popularity,
            artist_url = EXCLUDED.artist_url,
            last_updated = EXCLUDED.last_updated
        ''' #updates row contents when there are duplicates
    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load artist {spotify_id}') from e

    return artists_ids

def initialize_artists(conn): #main function that will call other sub functions
    BATCH_SIZE = 10
    playlist_id = '0AdbY5aqbGn33pkYeIPMll'

    cursor = conn.cursor()

    try:
        result_playlist = sp.playlist_items(playlist_id=playlist_id)
    except spotipy.SpotifyException as e:
        raise RuntimeError(f'Spotify API error when searching for playlist {playlist_id}') from e
    
    if result_playlist is None:
        print('No playlist found')
        return
    
    artists_ids = [] #used as input for get_artists_deets()
    artists_ = set()

    BATCH_NUMBER = 1
    
    while result_playlist['next']:
        tracks_items = result_playlist['items']
        for item in tracks_items:
            for artist in item['track']['artists']:
                if artist['id'] in artists_:
                      continue
                artists_ids.append(artist['id'])
                artists_.add(artist['id'])

                if len(artists_ids) >= BATCH_SIZE:
                    try:
                        print('Processing batch number: ', BATCH_NUMBER)
                        load_artists(artists_ids, cursor)
                        albums = load_albums(artists_ids, cursor)
                        load_tracks(albums_ids=albums, cursor=cursor)
                        load_top_tracks(artists_ids, cursor)
                        conn.commit()
                        print('Changes committed')
                    except Exception as e:
                        conn.rollback()
                        print(f'Batch {BATCH_NUMBER} failed: {e}')

                    print(f'Batch number {BATCH_NUMBER} finished')
                    artists_ids.clear()
                    BATCH_NUMBER += 1
    if artists_ids: #getting remaining < BATCH_SIZE atists
        try:
            print('Processing final batch')
            load_artists(artists_ids, cursor)
            albums = load_albums(artists_ids, cursor)
            load_tracks(albums_ids=albums, cursor=cursor)
            load_top_tracks(artists_ids, cursor)
            conn.commit()
            print('Changes committed')
        except Exception as e:
            conn.rollback()
            print('Final batch failed: ', e)

    return