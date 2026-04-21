import sqlite3
import csv
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'cinebase.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'sql' / 'schema_sqlite.sql'
CSV_PATH = Path(__file__).parent.parent / 'data' / 'data.csv'

def setup():
    print(f"Initializing local SQLite database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Run Schema
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())
    print("Schema created successfully.")
    
    # 2. Load Data
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found!")
        return

    print("Loading data from CSV (Limiting to first 1000 records)...")
    with open(CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader) # skip header
        
        count = 0
        for row in reader:
            if count >= 1000: break
            
            try:
                # Based on the mapping in csv_to_sql.py
                (mediaID, title, vote_average, vote_count, mediaStatus, release_date, revenue, runtime, budget, 
                 imdb_id, original_language, original_title, overview, popularity, tagline, genres, 
                 production_companies, production_countries, spoken_languages, cast, director, 
                 director_of_photography, writers, producers, music_composer, imdb_rating, imdb_votes) = row
            except ValueError:
                continue

            # Insert into media
            cursor.execute("""
                INSERT INTO media (mediaID, title, popularity, runtime, overview, releaseDate, revenue, mediaStatus, budget, language, tagline) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mediaID, title, popularity, runtime, overview, release_date, revenue, mediaStatus, budget, original_language, tagline))
            
            # Insert into IMDB
            cursor.execute("INSERT INTO IMDB (IMDBID, mediaID, IMDBVotes, IMDBRating) VALUES (?, ?, ?, ?)", 
                           (imdb_id, mediaID, vote_count, vote_average))
            
            # Map Many-to-Many relationships
            # Genre
            for g in set(genres.split(', ')):
                if not g: continue
                cursor.execute("INSERT OR IGNORE INTO genre (genreName) VALUES (?)", (g,))
                cursor.execute("INSERT OR IGNORE INTO listedIn (mediaID, genreID) SELECT ?, genreID FROM genre WHERE genreName = ?", (mediaID, g))
            
            # Cast
            for c in set(cast.split(', ')):
                if not c: continue
                cursor.execute("INSERT OR IGNORE INTO mediaCast (castName) VALUES (?)", (c,))
                cursor.execute("INSERT OR IGNORE INTO actedIn (mediaID, castID) SELECT ?, castID FROM mediaCast WHERE castName = ?", (mediaID, c))
            
            # Director
            for d in set(director.split(', ')):
                if not d: continue
                cursor.execute("INSERT OR IGNORE INTO director (directorName) VALUES (?)", (d,))
                cursor.execute("INSERT OR IGNORE INTO directedBy (mediaID, directorID) SELECT ?, directorID FROM director WHERE directorName = ?", (mediaID, d))
                
            # Company
            for comp in set(production_companies.split(', ')):
                if not comp: continue
                cursor.execute("INSERT OR IGNORE INTO company (productionCompany) VALUES (?)", (comp,))
                cursor.execute("INSERT OR IGNORE INTO producedBy (mediaID, companyID) SELECT ?, companyID FROM company WHERE productionCompany = ?", (mediaID, comp))

            # Country
            for country in set(production_countries.split(', ')):
                if not country: continue
                cursor.execute("INSERT OR IGNORE INTO country (productionCountry) VALUES (?)", (country,))
                cursor.execute("INSERT OR IGNORE INTO producedIn (mediaID, countryID) SELECT ?, countryID FROM country WHERE productionCountry = ?", (mediaID, country))

            # Writer
            for w in set(writers.split(', ')):
                if not w: continue
                cursor.execute("INSERT OR IGNORE INTO writer (writerName) VALUES (?)", (w,))
                cursor.execute("INSERT OR IGNORE INTO hasWriter (mediaID, writerID) SELECT ?, writerID FROM writer WHERE writerName = ?", (mediaID, w))

            # Composer
            for mc in set(music_composer.split(', ')):
                if not mc: continue
                cursor.execute("INSERT OR IGNORE INTO musicComposer (musicComposerName) VALUES (?)", (mc,))
                cursor.execute("INSERT OR IGNORE INTO hasMusicComposer (mediaID, musicComposerID) SELECT ?, musicComposerID FROM musicComposer WHERE musicComposerName = ?", (mediaID, mc))

            count += 1
            if count % 100 == 0:
                print(f"Loaded {count} records...")

    conn.commit()
    conn.close()
    print("Database setup complete! Local SQLite server is ready.")

if __name__ == "__main__":
    setup()
