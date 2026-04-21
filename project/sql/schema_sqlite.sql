-- SQLite Schema for CineBase
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS hasMusicComposer;
DROP TABLE IF EXISTS musicComposer;
DROP TABLE IF EXISTS producedBy;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS directedBy;
DROP TABLE IF EXISTS director;
DROP TABLE IF EXISTS producedIn;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS hasProducer;
DROP TABLE IF EXISTS producer;
DROP TABLE IF EXISTS actedIn;
DROP TABLE IF EXISTS mediaCast;
DROP TABLE IF EXISTS hasWriter;
DROP TABLE IF EXISTS writer;
DROP TABLE IF EXISTS listedIn;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS IMDB;
DROP TABLE IF EXISTS media;

CREATE TABLE media (
    mediaID INTEGER PRIMARY KEY,
    tagline TEXT,
    popularity REAL,
    runtime INTEGER,
    overview TEXT,
    releaseDate TEXT,
    revenue REAL,
    mediaStatus TEXT,
    title TEXT,
    budget REAL,
    language TEXT
);

CREATE TABLE IMDB (
    IMDBID TEXT,
    mediaID INTEGER,
    IMDBVotes INTEGER,
    IMDBRating REAL,
    PRIMARY KEY (IMDBID, mediaID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE
);

CREATE TABLE genre (
    genreID INTEGER PRIMARY KEY AUTOINCREMENT,
    genreName TEXT
);

CREATE TABLE listedIn (
    mediaID INTEGER,
    genreID INTEGER,
    PRIMARY KEY (mediaID, genreID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (genreID) REFERENCES genre(genreID) ON DELETE CASCADE
);

CREATE TABLE writer (
    writerID INTEGER PRIMARY KEY AUTOINCREMENT,
    writerName TEXT
);

CREATE TABLE hasWriter (
    mediaID INTEGER,
    writerID INTEGER,
    PRIMARY KEY (mediaID, writerID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (writerID) REFERENCES writer(writerID) ON DELETE CASCADE
);

CREATE TABLE mediaCast (
    castID INTEGER PRIMARY KEY AUTOINCREMENT,
    castName TEXT
);

CREATE TABLE actedIn (
    mediaID INTEGER,
    castID INTEGER,
    PRIMARY KEY (mediaID, castID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (castID) REFERENCES mediaCast(castID) ON DELETE CASCADE
);

CREATE TABLE producer (
    producerID INTEGER PRIMARY KEY AUTOINCREMENT,
    producerName TEXT
);

CREATE TABLE hasProducer (
    mediaID INTEGER,
    producerID INTEGER,
    PRIMARY KEY (mediaID, producerID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (producerID) REFERENCES producer(producerID) ON DELETE CASCADE
);

CREATE TABLE country (
    countryID INTEGER PRIMARY KEY AUTOINCREMENT,
    productionCountry TEXT
);

CREATE TABLE producedIn (
    mediaID INTEGER,
    countryID INTEGER,
    PRIMARY KEY (mediaID, countryID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (countryID) REFERENCES country(countryID) ON DELETE CASCADE
);

CREATE TABLE director (
    directorID INTEGER PRIMARY KEY AUTOINCREMENT,
    directorName TEXT
);

CREATE TABLE directedBy (
    mediaID INTEGER,
    directorID INTEGER,
    PRIMARY KEY (mediaID, directorID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (directorID) REFERENCES director(directorID) ON DELETE CASCADE
);

CREATE TABLE company (
    companyID INTEGER PRIMARY KEY AUTOINCREMENT,
    productionCompany TEXT
);

CREATE TABLE producedBy (
    mediaID INTEGER,
    companyID INTEGER,
    PRIMARY KEY (mediaID, companyID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (companyID) REFERENCES company(companyID) ON DELETE CASCADE
);

CREATE TABLE musicComposer (
    musicComposerID INTEGER PRIMARY KEY AUTOINCREMENT,
    musicComposerName TEXT
);

CREATE TABLE hasMusicComposer (
    mediaID INTEGER,
    musicComposerID INTEGER,
    PRIMARY KEY (mediaID, musicComposerID),
    FOREIGN KEY (mediaID) REFERENCES media(mediaID) ON DELETE CASCADE,
    FOREIGN KEY (musicComposerID) REFERENCES musicComposer(musicComposerID) ON DELETE CASCADE
);
