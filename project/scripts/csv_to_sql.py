import csv
from pathlib import Path
import sys
import shutil

def infer_and_format_value(value):
    try:
        int(value)
        return value
    except ValueError:
        try:
            if value == 'Infinity':
                raise ValueError
            float(value)
            return value
        except ValueError:
            string = value.replace("'", "''")
            return string

def generate_insert_statements(csv_data, limit=1000):
    statements = list()
    for rowNum,row in enumerate(csv_data):
        if rowNum >= limit: break

        row = [infer_and_format_value(value) for value in row]
        mediaID, title, vote_average, vote_count, mediaStatus, release_date, revenue, runtime, budget, imdb_id, original_language, original_title, overview, popularity, tagline, genres, production_companies, production_countries, spoken_languages, cast, director, director_of_photography, writers, producers, music_composer, imdb_rating, imdb_votes = row

        overview = overview.replace(';',':')
        
        statement = f"INSERT INTO media (mediaID, title, popularity, runtime, overview, releaseDate, revenue, mediaStatus, budget, language) VALUES ({mediaID}, '{title}', {popularity}, {runtime}, '{overview}', '{release_date}', {revenue}, '{mediaStatus}', {budget}, '{original_language}');"
        if statement not in statements: statements.append(statement)
        statement = f"INSERT INTO IMDB (IMDBID, mediaID, IMDBVotes, IMDBRating) VALUES ('{imdb_id}', {mediaID}, {vote_count}, {vote_average});"
        if statement not in statements: statements.append(statement)

        genre_list = genres.split(', ')
        for genre_name in genre_list:
            statement = f"INSERT INTO genre (genreName) VALUES('{genre_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO listedIn (mediaID, genreID) SELECT {mediaID}, genreID FROM genre WHERE genreName = '{genre_name}';"
            if statement not in statements: statements.append(statement)

        company_list = set(production_companies.lower().split(', '))
        for company_name in company_list:
            statement = f"INSERT INTO company (productionCompany) VALUES ('{company_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO producedBy (mediaID, companyID) SELECT {mediaID}, companyID FROM company WHERE productionCompany = '{company_name}';"
            if statement not in statements: statements.append(statement)

        country_list = production_countries.split(', ')
        for country_name in country_list:
            statement = f"INSERT INTO country (productionCountry) VALUES ('{country_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO producedIn (mediaID, countryID) SELECT {mediaID}, countryID FROM country WHERE productionCountry = '{country_name}';"
            if statement not in statements: statements.append(statement)

        writer_list = writers.split(', ')
        for writer_name in writer_list:
            statement = f"INSERT INTO writer (writerName) VALUES('{writer_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO hasWriter (mediaID, writerID) SELECT {mediaID}, writerID FROM writer WHERE writerName = '{writer_name}';"
            if statement not in statements: statements.append(statement)

        producer_list = producers.split(', ')
        for producer_name in producer_list:
            statement = f"INSERT INTO producer (producerName) VALUES('{producer_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO hasProducer (mediaID, producerID) SELECT {mediaID}, producerID FROM producer WHERE producerName = '{producer_name}';"
            if statement not in statements: statements.append(statement)

        composer_list = music_composer.split(', ')
        for composer_name in composer_list:
            statement = f"INSERT INTO musicComposer (musicComposerName) VALUES('{composer_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO hasMusicComposer (mediaID, musicComposerID) SELECT {mediaID}, musicComposerID FROM musicComposer WHERE musicComposerName = '{composer_name}';"
            if statement not in statements: statements.append(statement)

        director_list = director.split(', ')
        for director_name in director_list:
            statement = f"INSERT INTO director (directorName) VALUES('{director_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO directedBy (mediaID, directorID) SELECT {mediaID}, directorID FROM director WHERE directorName = '{director_name}';"
            if statement not in statements: statements.append(statement)

        cast_list = cast.split(', ')
        for cast_name in cast_list:
            statement = f"INSERT INTO mediaCast (castName) VALUES('{cast_name}');"
            if statement not in statements: statements.append(statement)
            statement = f"INSERT INTO actedIn (mediaID, castID) SELECT {mediaID}, castID FROM mediaCast WHERE castName = '{cast_name}';"
            if statement not in statements: statements.append(statement)

    return statements

shutil.copy(Path(__file__).parent.parent / 'sql' / 'backup.sql', Path(__file__).parent.parent / 'sql' / 'media.sql')

#sys.stdout = open(Path(__file__).parent / 'output1.txt', 'w')
sys.stdout = open(Path(__file__).parent.parent / 'sql' / 'insert.sql', 'w')

with open(Path(__file__).parent.parent / 'data' / 'data.csv', mode='r') as file:
    reader = csv.reader(file)
    header = next(reader)

    statements = generate_insert_statements(reader)
    for statement in statements:
        print(statement)