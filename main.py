from src.load.db import get_connection
from src.extract.spotify_client import initialize_artists


def main():
    conn = get_connection()

    initialize_artists(conn)

    conn.close()

main()