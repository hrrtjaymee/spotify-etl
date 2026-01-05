CREATE TABLE ARTIST (
    artist_id VARCHAR(30) UNIQUE PRIMARY KEY,
    artist_name VARCHAR(255),
    followers INTEGER,
    popularity INTEGER,
    artist_url VARCHAR(255),
    last_updated TIMESTAMP
);

CREATE TABLE ALBUM (
    album_id VARCHAR(30) UNIQUE PRIMARY KEY,
    album_name VARCHAR(255),
    artist_id VARCHAR(30) REFERENCES ARTIST(artist_id),
    number_tracks SMALLINT,
    release_date DATE,
    album_url VARCHAR(255)
);

CREATE TABLE TRACK (
    track_id VARCHAR(30) UNIQUE PRIMARY KEY,
    album_id VARCHAR(30) REFERENCES ALBUM(album_id),
    disc_number SMALLINT,
    duration_ms DECIMAL(2),
    track_url VARCHAR(255)
);

CREATE TABLE TOP_TRACKS (
    top_tracks_id VARCHAR(30) UNIQUE PRIMARY KEY,
    artist_id VARCHAR(30) REFERENCES ARTIST(artist_id),
    last_updated TIMESTAMP
);

CREATE TOP_TRACK_ITEMS (
    top_tracks_id VARCHAR(30) REFERENCES TOP_TRACKS(top_tracks_id),
    track_id VARCHAR(30) REFERENCES TRACK(track_id),
    PRIMARY KEY (top_tracks_id, track_id)
)
