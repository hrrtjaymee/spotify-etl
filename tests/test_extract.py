import pandas as pd
from unittest.mock import MagicMock
import pytest
from src.extract import extract_artist_albums, extract_artist_ids,\
    extract_artist_details, extract_playlist, extract_tracks


#################################
# extract playlist
def test_extract_playlist_return():
    sp = MagicMock()
    sp.playlist.return_value = {"items": [{"track": {"artists": [{"id": "id1",}]}}]}
    playlist = extract_playlist('0aMS6lryKsPNl70k4DLQdJ', sp)

    assert playlist is not None

#################################
#extract artist_ids
def test_extract_artist_ids_return_artist_ids():
    fake_items = {'items': [
            {"item": {"artists": [{"id": "artist1"}]}},
            {"item": {"artists": [{"id": "artist2"}]}},
        ],
        'next': None
    }
    
    results = extract_artist_ids(fake_items)
    artist_ids = [i for i in results]

    assert artist_ids is not None   
    assert isinstance(artist_ids[0], str)

def test_extract_artist_ids_return_none():
    fake_items = {'items': [], 'next': None
    }
    
    results = extract_artist_ids(fake_items)
    artist_ids = [i for i in results]

    assert len(artist_ids) == 0 

#################################
#extract artist_details
def test_extract_artist_details_return_many_artists():
    sample_ids = ['id1', 'id2', 'id3']
    sample_artist = [
    {'name': 'Georgie', 'followers': {'total': 12342}, 'popularity': 10, 'external_urls': {'spotify': 'https://open.spotify.com/artist/id1'}},
    {'name': 'Sheldon', 'followers': {'total': 1342},  'popularity': 4,  'external_urls': {'spotify': 'https://open.spotify.com/artist/id2'}},
    {'name': 'Missy',   'followers': {'total': 1342},  'popularity': 4,  'external_urls': {'spotify': 'https://open.spotify.com/artist/id3'}},
    ]
    sp = MagicMock()
    sp.artist.side_effect = sample_artist
    artists_details = extract_artist_details(sample_ids, sp)
    assert isinstance(artists_details, pd.DataFrame)
    assert len(artists_details) > 1

def test_extract_artist_details_return_one_artists():
    sample_ids = ['id1']
    sample_artist = {
    'name': 'Georgie',
    'followers': {'total': 12342},
    'popularity': 10,
    'external_urls': {'spotify': 'www.artist-url.com'}
    }

    sp = MagicMock()
    sp.artist.return_value = sample_artist
    artists_details = extract_artist_details(sample_ids, sp)
    assert isinstance(artists_details, pd.DataFrame)
    assert len(artists_details) == 1

#################################
#extract artist_albums
def test_extract_artist_albums_return_many_albums_from_one_artist(): ##with one artist
    sample_ids = ['id1']
    sample_albums = {'items': 
        [
            {'id': 'album1', 'name': 'Album Title1', 'total_tracks': 10, 'release_date': '1981-12', 'external_urls': {'spotify': 'https:spotify/Album1'}},
            {'id': 'album2', 'name': 'Album Title2', 'total_tracks': 3, 'release_date': '2004-10', 'external_urls': {'spotify': 'https:spotify/Album2'}},
            {'id': 'album3', 'name': 'Album Title3', 'total_tracks': 26, 'release_date': '2024-1', 'external_urls': {'spotify': 'https:spotify/Album2'}}
        ],
        'next': None
    }

    sp = MagicMock()
    sp.artist_albums.return_value = sample_albums

    albums = extract_artist_albums(sample_ids, sp)
    assert isinstance(albums, pd.DataFrame)
    assert len(albums) > 1
    assert set(albums.columns) == set([
        "album_id", "album_name", "artist_id",
        "number_tracks", "release_date", "album_url"
    ])

def test_extract_artist_albums_return_many_albums(): ##with many artists
    sample_ids = ['id1', 'id2']
    sample_albums = [
    {'items': [
        {'id': 'album1', 'name': 'Album Title1', 'total_tracks': 10, 'release_date': '2000-01', 'external_urls': {'spotify': 'https://spotify/album1'}},
    ], 'next': None},
    {'items': [
        {'id': 'album2', 'name': 'Album Title2', 'total_tracks': 8, 'release_date': '2010-05', 'external_urls': {'spotify': 'https://spotify/album2'}},
    ], 'next': None},
]

    sp = MagicMock()
    sp.artist_albums.side_effect = sample_albums

    albums = extract_artist_albums(sample_ids, sp)
    assert len(albums['artist_id'].unique()) == 2

def test_extract_artist_albums_return_nonduplicate_album_ids():
    sample_ids = ['id1']
    sample_albums = {'items': 
        [
            {'id': 'album1', 'name': 'Album Title1', 'total_tracks': 10, 'release_date': '1981-12', 'external_urls': {'spotify': 'https:spotify/Album1'}},
            {'id': 'album2', 'name': 'Album Title2', 'total_tracks': 3, 'release_date': '2004-10', 'external_urls': {'spotify': 'https:spotify/Album2'}},
            {'id': 'album2', 'name': 'Album Title3', 'total_tracks': 26, 'release_date': '2024-1', 'external_urls': {'spotify': 'https:spotify/Album2'}}
        ],
        'next': None
    }

    sp = MagicMock()
    sp.artist_albums.return_value = sample_albums

    albums = extract_artist_albums(sample_ids, sp)
    assert len(albums[albums['album_id'] == 'album2']) == 1

def test_extract_artist_albums_return_normalized_dates():
    sample_ids = ['id1']
    sample_albums = {'items': 
        [
            {'id': 'album1', 'name': 'Album Title1', 'total_tracks': 10, 'release_date': '1981-12', 'external_urls': {'spotify': 'https:spotify/Album1'}},
            {'id': 'album2', 'name': 'Album Title2', 'total_tracks': 3, 'release_date': '2004', 'external_urls': {'spotify': 'https:spotify/Album2'}},
        ],
        'next': None
    }

    sp = MagicMock()
    sp.artist_albums.return_value = sample_albums

    result = extract_artist_albums(sample_ids, sp)
    assert result.iloc[0]['release_date'] == "1981-12-01"
    assert result.iloc[1]['release_date'] == '2004-01-01'
 
#################################
##extract tracks 
def test_extract_tracks_return_dataframe():
    album_ids = pd.Series(['album1', 'album2'])
    tracks = {'items': 
        [
            {'id': 'track1', 'name': 'Track Name1', 'disc_number': 1, 'track_number': 1, 'duration_ms': 170200, 'external_urls': {'spotify': 'https:spotify/track1'}},
            {'id': 'track2', 'name': 'Track Name2', 'disc_number': 1, 'track_number':2, 'duration_ms': 180400, 'external_urls': {'spotify': 'https:spotify/track2'}},
            {'id': 'track3', 'name': 'Track Name3', 'disc_number': 1, 'track_number': 3, 'duration_ms': 180003, 'external_urls': {'spotify': 'https:spotify/track3'}}
        ],
        'next': None
    }
    
    sp = MagicMock()
    sp.album_tracks.return_value = tracks
    tracks = extract_tracks(album_ids, sp)
    assert isinstance(tracks, pd.DataFrame)
    assert set(tracks.columns) == set(['track_id', 'album_id', 'track_name', 'disc_num', 'track_num', 'duration_s', 'track_url'])

def test_extract_tracks_return_many_tracks_from_one_album():
    album_ids = pd.Series(['album1'])
    sample_tracks = {'items': 
        [
            {'id': 'track1', 'name': 'Track Name1', 'disc_number': 1, 'track_number': 1, 'duration_ms': 170200, 'external_urls': {'spotify': 'https:spotify/track1'}},
            {'id': 'track2', 'name': 'Track Name2', 'disc_number': 1, 'track_number':2, 'duration_ms': 180400, 'external_urls': {'spotify': 'https:spotify/track2'}},
            {'id': 'track3', 'name': 'Track Name3', 'disc_number': 1, 'track_number': 3, 'duration_ms': 180003, 'external_urls': {'spotify': 'https:spotify/track3'}}
        ],
        'next': None
    }
    
    sp = MagicMock()
    sp.album_tracks.return_value = sample_tracks
    tracks = extract_tracks(album_ids, sp)
    assert len(tracks) > 1
    assert len(tracks['album_id'].unique()) == 1

def test_extract_tracks_return_many_tracks_from_many_albums():
    album_ids = pd.Series(['album1', 'album2', 'album3'])
    sample_tracks = {'items': 
        [
            {'id': 'track1', 'name': 'Track Name1', 'disc_number': 1, 'track_number': 1, 'duration_ms': 170200, 'external_urls': {'spotify': 'https:spotify/track1'}},
            {'id': 'track2', 'name': 'Track Name2', 'disc_number': 1, 'track_number':2, 'duration_ms': 180400, 'external_urls': {'spotify': 'https:spotify/track2'}},
            {'id': 'track3', 'name': 'Track Name3', 'disc_number': 1, 'track_number': 3, 'duration_ms': 180003, 'external_urls': {'spotify': 'https:spotify/track3'}}
        ],
        'next': None
    }
    
    sp = MagicMock()
    sp.album_tracks.return_value = sample_tracks
    tracks = extract_tracks(album_ids, sp)
    assert len(tracks) > 1
    assert len(tracks['album_id'].unique()) == 3

