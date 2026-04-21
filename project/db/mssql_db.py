try:
    import pymssql
except ImportError:
    pymssql = None

from db.base_db import BaseDatabase
from pathlib import Path

class MSSQLDatabase(BaseDatabase):
    def _execute_query(self, query, params=None):
        if self.mock_mode:
            return []
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"MSSQL Error: {e}")
            return []

    def searchTitle(self, title_query: str):
        query = """
            SELECT TOP 10 popularity, releaseDate, title, overview, tagline
            FROM media
            WHERE LOWER(title) LIKE %s
            ORDER BY popularity DESC;
        """
        results = self._execute_query(query, (f'%{title_query.lower()}%',))
        if self.mock_mode: return []
        return [{"popularity": row[0], "releaseDate": str(row[1]), "title": row[2], "overview": row[3], "tagline": row[4]} for row in results]

    def languageTitle(self, title_query: str):
        query = """
            SELECT TOP 10 m.language, m.title
            FROM media m
            WHERE LOWER(m.title) LIKE %s;
        """
        results = self._execute_query(query, (f'%{title_query.lower()}%',))
        return [{"language": row[0], "title": row[1]} for row in results]

    def topActors(self):
        query = """
            SELECT TOP 10 castName, SUM(revenue) AS SumRevenue 
            FROM mediaCast
            JOIN actedIn ON mediaCast.castID = actedIn.castID 
            JOIN media ON actedIn.mediaID = media.mediaID 
            GROUP BY castName 
            ORDER BY SumRevenue DESC;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "revenue": float(row[1]) if row[1] else 0} for row in results]

    def topDirectors(self):
        query = """
            SELECT TOP 10 directorName, AVG(IMDB.IMDBRating) AS AverageRating 
            FROM director 
            JOIN directedBy ON director.directorID = directedBy.directorID 
            JOIN media ON directedBy.mediaID = media.mediaID 
            JOIN IMDB ON media.mediaID = IMDB.mediaID 
            GROUP BY director.directorName 
            ORDER BY AverageRating DESC;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "rating": float(row[1]) if row[1] else 0} for row in results]

    def topComposers(self):
        query = """
            SELECT TOP 10 mc.musicComposerName, AVG(m.revenue) AS AverageRevenue
            FROM musicComposer mc
            JOIN hasMusicComposer hmc ON mc.musicComposerID = hmc.musicComposerID
            JOIN media m ON hmc.mediaID = m.mediaID
            GROUP BY mc.musicComposerID, mc.musicComposerName
            ORDER BY AverageRevenue DESC;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "revenue": float(row[1]) if row[1] else 0} for row in results]
    
    def topWriters(self):
        query = """
            SELECT TOP 10 writerName, SUM(revenue - budget) AS overallGain
            FROM writer
            JOIN hasWriter ON writer.writerID = hasWriter.writerID
            JOIN media ON hasWriter.mediaID = media.mediaID
            GROUP BY writer.writerID, writerName
            ORDER BY overallGain DESC;
        """
        results = self._execute_query(query)
        return [{"name": row[0], "gain": float(row[1]) if row[1] else 0} for row in results]

    def topMovies(self):
        query = """
            SELECT TOP 10 popularity, title, revenue
            FROM media 
            ORDER BY popularity DESC;
        """
        results = self._execute_query(query)
        return [{"popularity": row[0], "title": row[1], "revenue": float(row[2]) if row[2] else 0} for row in results]

    def countGenre(self):
        query = """
            SELECT TOP 10 g.genreName, COUNT(*) AS genreCount
            FROM media m
            JOIN listedIn li ON m.mediaID = li.mediaID
            JOIN genre g ON li.genreID = g.genreID
            GROUP BY g.genreName
            ORDER BY genreCount DESC;
        """
        results = self._execute_query(query)
        return [{"genre": row[0], "count": row[1]} for row in results]

    def topGenreDecade(self):
        query = """
            WITH GenreCounts AS (
                SELECT g.genreName,
                    ((DATEPART(YEAR, m.releaseDate) / 10) * 10) AS decade,
                    COUNT(*) AS genreCount
                FROM media m
                JOIN listedIn li ON m.mediaID = li.mediaID
                JOIN genre g ON li.genreID = g.genreID
                GROUP BY g.genreName, ((DATEPART(YEAR, m.releaseDate) / 10) * 10)
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
            SELECT TOP 10 title, runtime
            FROM media
            ORDER BY runtime DESC;
        """
        results = self._execute_query(query)
        return [{"title": row[0], "runtime": row[1]} for row in results]

    def topCountry(self, country_query: str):
        query = """
            SELECT TOP 10 m.title, c.productionCountry, m.revenue
            FROM media m
            JOIN producedIn p ON m.mediaID = p.mediaID
            JOIN country c ON p.countryID = c.countryID
            WHERE c.productionCountry LIKE %s
            ORDER BY m.revenue DESC;
        """
        results = self._execute_query(query, (country_query,))
        return [{"title": row[0], "country": row[1], "revenue": float(row[2]) if row[2] else 0} for row in results]

    def topCompany(self):
        query = """
            SELECT TOP 10 c.productionCompany, COUNT(m.mediaID) AS movieCount
            FROM media m
            JOIN producedBy pb ON m.mediaID = pb.mediaID
            JOIN company c ON pb.companyID = c.companyID
            GROUP BY c.productionCompany
            ORDER BY movieCount DESC;
        """
        results = self._execute_query(query)
        return [{"company": row[0], "count": row[1]} for row in results if row[0] != ""]

    def topActorDirector(self):
        query = """
            SELECT TOP 10 mediaCast.castName, director.directorName, COUNT(*) AS CollaborationCount 
            FROM mediaCast
            JOIN actedIn ON mediaCast.castID = actedIn.castID 
            JOIN media ON actedIn.mediaID = media.mediaID 
            JOIN directedBy ON media.mediaID = directedBy.mediaID 
            JOIN director ON directedBy.directorID = director.directorID 
            GROUP BY mediaCast.castName, director.directorName 
            HAVING COUNT(*) > 1 
            ORDER BY CollaborationCount DESC;
        """
        results = self._execute_query(query)
        return [{"actor": row[0], "director": row[1], "count": row[2]} for row in results]
    
    def topCastSize(self):
        query = """
            SELECT TOP 10 m.title, COUNT(mc.castID) AS castSize
            FROM media m
            JOIN actedIn ai ON m.mediaID = ai.mediaID
            JOIN mediaCast mc ON ai.castID = mc.castID
            GROUP BY m.mediaID, m.title
            ORDER BY castSize DESC;
        """
        results = self._execute_query(query)
        return [{"title": row[1], "count": row[0]} for row in results]
    
    def directorMovies(self, director_query):
        query = """
            SELECT releaseDate, title
            FROM media
            JOIN directedBy ON media.mediaID = directedBy.mediaID
            JOIN director ON directedBy.directorID = director.directorID
            WHERE LOWER(directorName) LIKE %s
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
            WHERE LOWER(castName) LIKE %s
            ORDER BY media.releaseDate DESC;
        """
        results = self._execute_query(query, (f'%{actor_query.lower()}%',))
        return [{"releaseDate": str(row[0]), "title": row[1]} for row in results]

    def delete(self):
        try:
            self.connection.autocommit(False)
            self.cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';")
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
            all_tables = self.cursor.fetchall()
            for table in all_tables:
                table_name = str(table[0])
                self.cursor.execute(f'DELETE FROM {table_name};')
            self.cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';")
            self.connection.commit()
            return "MSSQL Database deletion successful!"
        except Exception as e:
            self.connection.rollback()
            return f"Deletion Error {e}"

    def repopulate(self):
        # In the original code, this called an external run_sql_file on insert.sql
        return "Please use the repopulate script or SQL commands for MSSQL."
        
    def recreate(self):
        try:
            # Reuses the legacy recreate logic if needed
            return "Schema recreation requires direct SQL script execution for MSSQL."
        except Exception as e:
            return f"Database creation error {e}"
