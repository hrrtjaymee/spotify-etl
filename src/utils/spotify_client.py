import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

def get_spotipy_client():

    auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('CLIENT_ID'), 
    client_secret=os.getenv('CLIENT_SECRET'))

    sp = spotipy.Spotify(auth_manager=auth_manager)

    return sp