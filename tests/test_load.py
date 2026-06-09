import pandas as pd
from unittest.mock import MagicMock
import pytest
import psycopg2
from src.load import load_artists, load_albums, load_tracks


def make_artists_df():
    return pd.DataFrame({
        'artist_id': ['id1', 'id2'],
        'artist_name': ['Georgie', 'Sheldon'],
        'followers': [12342, 1342],
        'popularity': [10, 4],
        'artist_url': ['https://open.spotify.com/artist/id1', 'https://open.spotify.com/artist/id2'],
        'last_updated': ['2024-01-01', '2024-01-01']
    })

def make_albums_df():
    return pd.DataFrame({
        'artist_id': ['id1', 'id2'],
        'album_id': ['album1', 'album2'],
        'album_name': ['Album Title1', 'Album Title2'],
        'number_tracks': [10, 8],
        'release_date': ['2000-01-01', '2010-05-01'],
        'album_url': ['https://open.spotify.com/album/album1', 'https://open.spotify.com/album/album2']
    })

def make_tracks_df():
    return pd.DataFrame({
        'track_id': ['track1', 'track2', 'track3'],
        'album_id': ['album1', 'album1', 'album1'],
        'track_name': ['Track Name1', 'Track Name2', 'Track Name3'],
        'disc_num': [1, 1, 1],
        'track_num': [1, 2, 3],
        'duration_s': [170.2, 180.4, 180.0],
        'track_url': ['https://open.spotify.com/track/track1', 'https://open.spotify.com/track/track2', 'https://open.spotify.com/track/track3']
    })


#################################
# load_artists
def test_load_artists_calls_executemany():
    cursor = MagicMock()
    load_artists(make_artists_df(), cursor)
    cursor.executemany.assert_called_once()

def test_load_artists_raises_on_db_error():
    cursor = MagicMock()
    cursor.executemany.side_effect = psycopg2.Error('DB error')

    with pytest.raises(RuntimeError, match='Failed to load artist'):
        load_artists(make_artists_df(), cursor)


#################################
# load_albums
def test_load_albums_calls_executemany():
    cursor = MagicMock()
    load_albums(make_albums_df(), cursor)
    cursor.executemany.assert_called_once()

def test_load_albums_raises_on_db_error():
    cursor = MagicMock()
    cursor.executemany.side_effect = psycopg2.Error('DB error')

    with pytest.raises(RuntimeError, match='Failed to load album'):
        load_albums(make_albums_df(), cursor)

def test_load_albums_called_with_correct_query():
    cursor = MagicMock()
    load_albums(make_albums_df(), cursor)

    query_used = cursor.executemany.call_args[0][0]
    assert 'ON CONFLICT' in query_used
    assert 'DO NOTHING' in query_used


#################################
# load_tracks
def test_load_tracks_calls_executemany():
    cursor = MagicMock()
    load_tracks(make_tracks_df(), cursor)
    cursor.executemany.assert_called_once()

def test_load_tracks_raises_on_db_error():
    cursor = MagicMock()
    cursor.executemany.side_effect = psycopg2.Error('DB error')

    with pytest.raises(RuntimeError, match='Failed to load tracks'):
        load_tracks(make_tracks_df(), cursor)

def test_load_tracks_called_with_correct_query():
    cursor = MagicMock()
    load_tracks(make_tracks_df(), cursor)

    query_used = cursor.executemany.call_args[0][0]
    assert 'ON CONFLICT' in query_used
    assert 'DO NOTHING' in query_used