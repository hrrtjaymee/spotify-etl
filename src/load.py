from psycopg2.extensions import cursor as Cursor
import pandas as pd
import psycopg2
from src.utils.logger import get_logger

logger = get_logger(__name__)
def load_artists(artist_df: pd.DataFrame, cursor: Cursor):
    values = zip(
        artist_df['artist_id'],
        artist_df['artist_name'],
        artist_df['followers'],
        artist_df['popularity'],
        artist_df['artist_url'],
        artist_df['last_updated']
    )

    load_query = '''
        INSERT INTO spotify_etl.artist
        (artist_id, artist_name, followers, popularity, artist_url, last_updated) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (artist_id) DO UPDATE
        SET 
            followers = EXCLUDED.followers,
            popularity = EXCLUDED.popularity,
            artist_url = EXCLUDED.artist_url,
            last_updated = EXCLUDED.last_updated
        ''' #updates row contents when there are duplicates
    
    logger.info('Loading artists')

    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load artist {artist_df['artist_id']} {e}')
    
    logger.info('Finished loading artists')
    return

def load_albums(albums: pd.DataFrame, cursor: Cursor):
    values = zip(
        albums['artist_id'],
        albums['album_id'],
        albums['album_name'],
        albums['number_tracks'],
        albums['release_date'],
        albums['album_url']
    )

    load_query = '''
        INSERT INTO spotify_etl.album
        (artist_id, album_id, album_name, number_tracks, release_date, album_url) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON CONFLICT (album_id) DO NOTHING
        ''' #when an album already exists, do not update the album
    
    logger.info('Loading albums')

    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load album from {albums['artist_id']}') from e

    logger.info('Finished loading albums')
    return

def load_tracks(tracks: pd.DataFrame, cursor: Cursor):
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
        INSERT INTO spotify_etl.track
        (track_id, album_id, track_name, disc_num, track_num, duration_s, track_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT DO NOTHING
        '''

    logger.info('Loading tracks')

    try: 
        cursor.executemany(load_query, values)
    except psycopg2.Error as e:
        raise RuntimeError(f'Failed to load tracks from album') from e

    logger.info('Finished loading tracks')
    return 
# def load_top_tracks(artists_ids: list, cursor: Cursor):
#     top_tracks_query = '''
#                         INSERT INTO TOP_TRACKS (artist_id, last_updated) 
#                         VALUES (%s, %s) RETURNING top_tracks_id
#                         '''
    
#     track_item_query = '''
#                         INSERT INTO TOP_TRACK_ITEM (top_tracks_id, track_id) VALUES (%s, %s)
#                         '''
    
#     insert_query = '''
#                             INSERT INTO TRACK (track_id, track_name, disc_num, track_num, duration_s, track_url) 
#                             VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (track_id) DO NOTHING
#                             '''
    
#     try:
#             cursor.execute(top_tracks_query, (artist, current))
#             row = cursor.fetchone()
#             if row is None:
#                 raise ValueError('TOP_TRACKS record not found')
            
#             current_id = row[0]

#             for track in top_tracks_search:
#                 values = (
#                     track['id'], 
#                     track['name'], 
#                     track['disc_number'], 
#                     track['track_number'], 
#                     track['duration_ms']/1000, 
#                     track['external_urls']['spotify'])
#                 cursor.execute(insert_query, values)

#                 cursor.execute(
#                     track_item_query, (current_id, track['id'])
#                 )
                
#     except psycopg2.Error as e:
#         raise RuntimeError(f'Failed to load top tracks for artist {artist}') from e