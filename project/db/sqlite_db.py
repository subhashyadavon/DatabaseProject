import sqlite3
from db.base_db import BaseDatabase
from pathlib import Path

class SQLiteDatabase(BaseDatabase):
    def __init__(self, connection=None):
        super().__init__(connection)
        if self.connection:
            self.connection.execute("PRAGMA foreign_keys = ON;")

    def _execute_query(self, query, params=None):
        if self.mock_mode:
            return []
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            return []

    def searchTitle(self, title_query: str):
        query = """
            SELECT popularity, releaseDate, title, overview, tagline
            FROM media
            WHERE LOWER(title) LIKE ?
            ORDER BY popularity DESC
            LIMIT 10;
        """
        results = self._execute_query(query, (f'%{title_query.lower()}%',))
        if self.mock_mode: return []
        return [{"popularity": row[0], "releaseDate": str(row[1]), "title": row[2], "overview": row[3], "tagline": row[4]} for row in results]

    def languageTitle(self, title_query: str):
        query = """
            SELECT m.language, m.title
            FROM media m
            WHERE LOWER(m.title) LIKE ?
            LIMIT 10;
        """
        results = self._execute_query(query, (f'%{title_query.lower()}%',))
        return [{"language": row[0], "title": row[1]} for row in results]

    def topActors(self):
        query = """
            SELECT castName, SUM(revenue) AS SumRevenue 
            FROM mediaCast
            JOIN actedIn ON mediaCast.castID = actedIn.castID 
            JOIN media ON actedIn.mediaID = media.mediaID 
            GROUP BY castName 
            ORDER BY SumRevenue DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "revenue": float(row[1]) if row[1] else 0} for row in results]

    def topDirectors(self):
        query = """
            SELECT directorName, AVG(IMDB.IMDBRating) AS AverageRating 
            FROM director 
            JOIN directedBy ON director.directorID = directedBy.directorID 
            JOIN media ON directedBy.mediaID = media.mediaID 
            JOIN IMDB ON media.mediaID = IMDB.mediaID 
            GROUP BY director.directorName 
            ORDER BY AverageRating DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "rating": float(row[1]) if row[1] else 0} for row in results]

    def topComposers(self):
        query = """
            SELECT mc.musicComposerName, AVG(m.revenue) AS AverageRevenue
            FROM musicComposer mc
            JOIN hasMusicComposer hmc ON mc.musicComposerID = hmc.musicComposerID
            JOIN media m ON hmc.mediaID = m.mediaID
            GROUP BY mc.musicComposerID, mc.musicComposerName
            ORDER BY AverageRevenue DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "revenue": float(row[1]) if row[1] else 0} for row in results]
    
    def topWriters(self):
        query = """
            SELECT writerName, SUM(revenue - budget) AS overallGain
            FROM writer
            JOIN hasWriter ON writer.writerID = hasWriter.writerID
            JOIN media ON hasWriter.mediaID = media.mediaID
            GROUP BY writer.writerID, writerName
            ORDER BY overallGain DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "gain": float(row[1]) if row[1] else 0} for row in results]

    def topMovies(self):
        query = """
            SELECT popularity, title, revenue
            FROM media 
            ORDER BY popularity DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"popularity": row[0], "title": row[1], "revenue": float(row[2]) if row[2] else 0} for row in results]

    def countGenre(self):
        query = """
            SELECT g.genreName, COUNT(*) AS genreCount
            FROM media m
            JOIN listedIn li ON m.mediaID = li.mediaID
            JOIN genre g ON li.genreID = g.genreID
            GROUP BY g.genreName
            ORDER BY genreCount DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"genre": row[0], "count": row[1]} for row in results]

    def topGenreDecade(self):
        query = """
            WITH GenreCounts AS (
                SELECT g.genreName,
                    (CAST(strftime('%Y', m.releaseDate) AS INTEGER) / 10 * 10) AS decade,
                    COUNT(*) AS genreCount
                FROM media m
                JOIN listedIn li ON m.mediaID = li.mediaID
                JOIN genre g ON li.genreID = g.genreID
                GROUP BY g.genreName, decade
            ),
            MaxGenreCountsPerDecade AS (
                SELECT decade, MAX(genreCount) AS maxGenreCount
                FROM GenreCounts
                GROUP BY decade
            )
            SELECT gc.decade, gc.genreName, gc.genreCount
            FROM GenreCounts gc
            JOIN MaxGenreCountsPerDecade mgc ON gc.decade = mgc.decade AND gc.genreCount = mgc.maxGenreCount
            ORDER BY gc.decade;
        """
        results = self._execute_query(query)
        return [{"decade": row[0], "genre": row[1], "count": row[2]} for row in results]

    def topRuntime(self):
        query = """
            SELECT title, runtime
            FROM media
            ORDER BY runtime DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"title": row[0], "runtime": row[1]} for row in results]

    def topCountry(self, country_query: str):
        query = """
            SELECT m.title, c.productionCountry, m.revenue
            FROM media m
            JOIN producedIn p ON m.mediaID = p.mediaID
            JOIN country c ON p.countryID = c.countryID
            WHERE c.productionCountry LIKE ?
            ORDER BY m.revenue DESC
            LIMIT 10;
        """
        results = self._execute_query(query, (country_query,))
        return [{"title": row[0], "country": row[1], "revenue": float(row[2]) if row[2] else 0} for row in results]

    def topCompany(self):
        query = """
            SELECT c.productionCompany, COUNT(m.mediaID) AS movieCount
            FROM media m
            JOIN producedBy pb ON m.mediaID = pb.mediaID
            JOIN company c ON pb.companyID = c.companyID
            GROUP BY c.productionCompany
            ORDER BY movieCount DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"company": row[0], "count": row[1]} for row in results if row[0] != ""]

    def topActorDirector(self):
        query = """
            SELECT mediaCast.castName, director.directorName, COUNT(*) AS CollaborationCount 
            FROM mediaCast
            JOIN actedIn ON mediaCast.castID = actedIn.castID 
            JOIN media ON actedIn.mediaID = media.mediaID 
            JOIN directedBy ON media.mediaID = directedBy.mediaID 
            JOIN director ON directedBy.directorID = director.directorID 
            GROUP BY mediaCast.castName, director.directorName 
            HAVING COUNT(*) > 1 
            ORDER BY CollaborationCount DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"actor": row[0], "director": row[1], "count": row[2]} for row in results]
    
    def topCastSize(self):
        query = """
            SELECT m.title, COUNT(mc.castID) AS castSize
            FROM media m
            JOIN actedIn ai ON m.mediaID = ai.mediaID
            JOIN mediaCast mc ON ai.castID = mc.castID
            GROUP BY m.mediaID, m.title
            ORDER BY castSize DESC
            LIMIT 10;
        """
        results = self._execute_query(query)
        return [{"title": row[0], "count": row[1]} for row in results]
    
    def directorMovies(self, director_query):
        query = """
            SELECT releaseDate, title
            FROM media
            JOIN directedBy ON media.mediaID = directedBy.mediaID
            JOIN director ON directedBy.directorID = director.directorID
            WHERE LOWER(directorName) LIKE ?
            ORDER BY releaseDate DESC;
        """
        results = self._execute_query(query, (f'%{director_query.lower()}%',))
        return [{"releaseDate": str(row[0]), "title": row[1]} for row in results]
    
    def actorMovies(self, actor_query):
        query = """
            SELECT media.releaseDate, media.title
            FROM media
            JOIN actedIn ON media.mediaID = actedIn.mediaID
            JOIN mediaCast ON actedIn.castID = mediaCast.castID
            WHERE LOWER(castName) LIKE ?
            ORDER BY media.releaseDate DESC;
        """
        results = self._execute_query(query, (f'%{actor_query.lower()}%',))
        return [{"releaseDate": str(row[0]), "title": row[1]} for row in results]

    def delete(self):
        try:
            self.cursor.execute("PRAGMA foreign_keys = OFF;")
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = self.cursor.fetchall()
            for table in all_tables:
                table_name = str(table[0])
                if table_name != 'sqlite_sequence':
                    self.cursor.execute(f'DELETE FROM {table_name};')
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            self.connection.commit()
            return "SQLite Database deletion successful!"
        except Exception as e:
            self.connection.rollback()
            return f"Deletion Error {e}"

    def repopulate(self):
        return "Please run setup_local_db.py to repopulate SQLite."
        
    def recreate(self):
        try:
            schema_path = Path(__file__).parent.parent / 'sql' / 'schema_sqlite.sql'
            with open(schema_path, 'r') as f:
                self.cursor.executescript(f.read())
            self.connection.commit()
            return "SQLite Database recreation successful!"
        except Exception as e:
            return f"Creation Error {e}"
