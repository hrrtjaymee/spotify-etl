from src.utils.db import get_connection
from src.utils.spotify_client import get_spotipy_client
from src.extract import extract_playlist, extract_artist_ids, extract_artist_albums,\
    extract_artist_details, extract_top_tracks, extract_tracks
from src.load import load_artists, load_albums, load_tracks
from src.utils.logger import get_logger
import argparse
import json

logger = get_logger(__name__)

BATCH_SIZE = 10
conn = get_connection()
cursor = conn.cursor()
sp = get_spotipy_client()

def main(playlist_id):

    try:
        result_playlist = extract_playlist(playlist_id=playlist_id, sp=sp)

        if result_playlist is None:
            logger.info(f'No playlit found with id {playlist_id}, ending process')
            return
    except Exception as e:
        logger.critical(f'Error while retrieving playlist {e}') 

    logger.info('Processing Batches')
    try: 
        gen = extract_artist_ids(result_playlist['items'])
        process_in_batches(gen)
    except Exception as e:
        logger.critical(f'Error while processing batches {e}')    

    return 

def process_in_batches(artist_ids_gen):
    batch, batch_number = [], 1

    for artist_id in artist_ids_gen:
        batch.append(artist_id)

        if len(batch) >= BATCH_SIZE:
            _process_batch(batch, batch_number)
            batch.clear()
            batch_number += 1

    if batch:
        _process_batch(batch, batch_number, label="final")

def _process_batch(artists_ids: list, batch_number: int, label: str = None):
    tag = f"batch {batch_number}" if not label else f"{label} batch"
    try:
        logger.info(f'Processing {tag}')
        artists = extract_artist_details(artists_ids, sp)
        load_artists(artists, cursor)
        albums = extract_artist_albums(artists_ids, sp)
        load_albums(albums, cursor)
        tracks = extract_tracks(albums['id'], sp)
        load_tracks(tracks, cursor)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f'{tag.capitalize()} failed: {e}')
    logger.info(f'{tag.capitalize()} finished')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and load items from playlists')
    parser.add_argument('--playlist', required=True, help='Spotify playlist ID')
    args = parser.parse_args()

    logger.info(f'Extracting and loading items from playlist...')
    main(args.playlist)