import spotipy
from dotenv import load_dotenv
from datetime import datetime
from src.utils.utils import normalize_date
from spotipy.client import Spotify
from src.utils.logger import get_logger
import pandas as pd

load_dotenv()
logger = get_logger(__name__)
def extract_playlist(playlist_id: str, sp: Spotify):
    try: 
        result_playlist = sp.playlist(playlist_id=playlist_id)
    except spotipy.SpotifyException as e:
        raise RuntimeError(f'Spotify API error when searching for playlist {playlist_id}') from e
    
    return result_playlist

def extract_artist_ids(initial_page: dict):
    artists_seen = set()
    page = initial_page

    logger.info(f'Extracting artist IDs from playlist')

    while True:
        for item in page['items']:
            for artist in item['item']['artists']:
                if artist['id'] in artists_seen:
                    continue
                artists_seen.add(artist['id'])
                yield artist['id']
        
        if page['next']:
            page = page['next'] 
        else:
            break

def extract_artist_details(artists_id: list, sp: Spotify) -> pd.DataFrame:
    artists_df = {
        'artist_id': [], 
        'artist_name': [], 
        'followers': [], 
        'popularity': [], 
        'artist_url': [], 
        'last_updated': [],
    }

    logger.info(f'Extracting artists details')

    for spotify_id in artists_id:
        current = datetime.now()

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
    logger.info('Finished extracting artist details')
    return pd.DataFrame(artists_df)

def extract_artist_albums(artists_id: list, sp: Spotify) -> pd.DataFrame:
    artist_albums = {
         'album_id': [],
         'album_name': [],
         'artist_id': [],
         'number_tracks': [],
         'release_date': [],
         'album_url': []
    }

    albums_seen = set()
    
    logger.info('Extracting albums from artists')
    for spotify_id in artists_id:
        try: 
            album_search = sp.artist_albums(artist_id=spotify_id, include_groups='album')
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error for searching albums for artist {spotify_id}') from e
        
        album_items = album_search['items']
        while True:
            for item in album_items:

                if item['id'] in albums_seen:
                    continue

                albums_seen.add(item['id'])

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
    logger.info('Finished extracting albums from artists')
    return pd.DataFrame(artist_albums)

def extract_tracks(albums_id: pd.Series, sp: Spotify) -> pd.DataFrame:
    tracks_df = {
        'track_id': [],
        'album_id': [],
        'track_name': [],
        'disc_num': [],
        'track_num': [],
        'duration_s': [],
        'track_url': []
    }

    logger.info('Extracting tracks from albums')

    for album in albums_id:
        try:
            album_search = sp.album_tracks(album_id=album)
        except spotipy.SpotifyException as e:
            raise RuntimeError(f'Spotify API error when searching for album {album}') from e
        
        while True:
            for track in album_search['items']:
                tracks_df['track_id'].append(track['id'])
                tracks_df['album_id'].append(album)
                tracks_df['track_name'].append(track['name'])
                tracks_df['disc_num'].append(track['disc_number'])
                tracks_df['track_num'].append(track['track_number'])
                tracks_df['duration_s'].append(track['duration_ms']/1000) #turn milliseconds into seconds
                tracks_df['track_url'].append(track['external_urls']['spotify'])

            if album_search['next']:
                album_search = sp.next(album_search)
            else:
                break
    logger.info('Finished extracting tracks from albums')
    return pd.DataFrame(tracks_df)

def extract_top_tracks(artists_id: list, sp: Spotify) -> pd.DataFrame:
    return