# Spotify ETL

A Python ETL pipeline that extracts data from the Spotify API and loads it into a PostgreSQL database. Given a playlist, it pulls all artists, their albums, and tracks, then upserts them into structured tables.

## What it does

1. **Extract** — Fetches a playlist from Spotify, then walks the data to collect artists, albums, and tracks via the Spotify API
2. **Load** — Upserts the results into a PostgreSQL database, handling duplicates gracefully

## Project Structure

```
spotify-etl/
├── src/
│   ├── extract.py          # Spotify API extraction logic
│   ├── load.py             # PostgreSQL load logic
│   └── utils/
│       ├── db.py           # Database connection setup
│       ├── logger.py       # Logging config
│       ├── spotify_client.py  # Spotify client setup
│       └── utils.py        # Helpers (e.g. date normalization)
├── tests/
│   ├── test_extract.py
│   └── test_load.py
└── .env
```

## Setup

### Prerequisites

- Python 3.12+
- A Spotify developer account with a registered app ([create one here](https://developer.spotify.com/dashboard))
- A running PostgreSQL instance

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=your_redirect_uri

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

## Database Schema

The pipeline loads into three tables under the `spotify_etl` schema:

| Table | Key columns |
|-------|------------|
| `artist` | `artist_id`, `artist_name`, `followers`, `popularity`, `artist_url`, `last_updated` |
| `album` | `album_id`, `artist_id`, `album_name`, `number_tracks`, `release_date`, `album_url` |
| `track` | `track_id`, `album_id`, `track_name`, `disc_num`, `track_num`, `duration_s`, `track_url` |

Artists are upserted on conflict (followers and popularity are updated). Albums and tracks are inserted and skipped on conflict.

## Running tests

```bash
pytest tests/
```

Tests use `unittest.mock` to mock the Spotify client and database cursor — no real API calls or database connections are needed to run them.

## Notes

- Duplicate albums across artists are deduplicated at extraction time
- Release dates are normalized to `YYYY-MM-DD` format regardless of how Spotify returns them (some are `YYYY`, some `YYYY-MM`)
- Track durations are converted from milliseconds to seconds during extraction
