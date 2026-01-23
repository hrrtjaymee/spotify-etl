CREATE TABLE IF NOT EXISTS ARTIST (
    artist_id VARCHAR(30) PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    followers INTEGER,
    popularity INTEGER,
    artist_url VARCHAR(255),
    last_updated TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ALBUM (
    album_id VARCHAR(30) PRIMARY KEY,
    album_name VARCHAR(255) NOT NULL,
    artist_id VARCHAR(30) REFERENCES ARTIST(artist_id) ON DELETE CASCADE,
    number_tracks SMALLINT,
    release_date DATE,
    album_url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS TRACK (
    track_id VARCHAR(30) PRIMARY KEY,
    album_id VARCHAR(30) REFERENCES ALBUM(album_id) ON DELETE CASCADE,
    track_name VARCHAR(255) NOT NULL,
    disc_num SMALLINT,
    track_num SMALLINT,
    duration_s INTEGER,
    track_url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS TOP_TRACKS (
    top_tracks_id BIGSERIAL PRIMARY KEY,
    artist_id VARCHAR(30) REFERENCES ARTIST(artist_id) ON DELETE CASCADE,
    last_updated TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS TOP_TRACK_ITEM (
    top_tracks_id BIGINT REFERENCES TOP_TRACKS(top_tracks_id) ON DELETE CASCADE, --should be BIGINT because this references BIGSERIAL, which autoincrements
    track_id VARCHAR(30) REFERENCES TRACK(track_id) ON DELETE CASCADE,
    PRIMARY KEY (top_tracks_id, track_id)
)
