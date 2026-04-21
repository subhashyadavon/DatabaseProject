from pathlib import Path
import pymssql

insert_path = 'insert.sql'
create_path = 'media.sql'

class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def searchTitle(self, title_query: str):
        query = """
            SELECT TOP 10 popularity, releaseDate, title
            FROM media
            WHERE LOWER(title) LIKE %s
            ORDER BY popularity DESC;
        """
        self.cursor.execute(query, (f'%{title_query.lower()}%',))
        results = self.cursor.fetchall()

        if not results: return f'No titles found matching {title_query}'
        
        output = "\nResults"
        for row in results:
            popularity, release_date, title = row
            output += f"\n{popularity}    {release_date} \t {title}"
        output += "\n"
        return output

    def languageTitle(self, title_query: str):
        query = """
            SELECT TOP 10 m.language, m.title
            FROM media m
            WHERE LOWER(m.title) LIKE %s;
        """
        self.cursor.execute(query, (f'%{title_query.lower()}%',))
        results = self.cursor.fetchall()

        if not results: return f'No titles found matching {title_query}'

        output = "\n Lang \t Title"
        for row in results:
            language, title= row
            output += f"\n {language}   \t {title}"
        output += "\n"
        return output

    def topActors(self):
        query = """
            SELECT TOP 10 castName,  SUM(revenue) AS SumRevenue 
            FROM mediaCast
            JOIN actedIn ON mediaCast.castID = actedIn.castID 
            JOIN media ON actedIn.mediaID = media.mediaID 
            GROUP BY castName 
            ORDER BY SumRevenue DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        output = "\nActor Name\t\tFilmography Revenue"
        for row in results:
            output += f"\n{row[0]:<20}\t${round(row[1]):,}"
        output += '\n'
        return output

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
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = "\nDirector Name\t\tIMDB Rating"
        for row in results:
            output += f"\n{row[0]:<20}\t{row[1]}"
        output += '\n'
        return output

    def topComposers(self):
        query = """
            SELECT TOP 10 mc.musicComposerName, AVG(m.revenue) AS AverageRevenue
            FROM musicComposer mc
            JOIN hasMusicComposer hmc ON mc.musicComposerID = hmc.musicComposerID
            JOIN media m ON hmc.mediaID = m.mediaID
            GROUP BY mc.musicComposerID, mc.musicComposerName
            ORDER BY AverageRevenue DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = "\nComposer Name\t\tAverage Revenue"
        for row in results:
            output += f"\n{row[0]:<20}\t${round(row[1]):,}"
        output += '\n'
        return output
    
    def topWriters(self):
        query = """
            SELECT TOP 10 writerName, SUM(revenue - budget) AS overallGain
            FROM writer
            JOIN hasWriter ON writer.writerID = hasWriter.writerID
            JOIN media ON hasWriter.mediaID = media.mediaID
            GROUP BY writer.writerID, writerName
            ORDER BY overallGain DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = f"\n{'Writer Name':<20}\tOverall Net Revenue"
        for row in results:
            output += f"\n{row[0]:<20}\t${round(row[1]):,}"
        output += '\n'
        return output

    def topMovies(self):
        query = """
            SELECT TOP 10 popularity, title
            FROM media 
            ORDER BY popularity DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        output = f"\nPopularity\tTitle"
        for row in results:
            output += f"\n{row[0]}\t\t{row[1]}"
        output += '\n'
        return output

    def countGenre(self):
            query = """
                SELECT TOP 10 g.genreName,COUNT(*) AS genreCount
                FROM media m
                JOIN listedIn li ON m.mediaID = li.mediaID
                JOIN genre g ON li.genreID = g.genreID
                GROUP BY g.genreName
                ORDER BY genreCount DESC;
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            output = f"\n{'Popularity':<10}\tTitle"
            for row in results:
                output += f"\n{row[0]:<10}\t\t{row[1]}"
            output += '\n'
            return output

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
            JOIN MaxGenreCountsPerDecade mgc ON gc.decade = mgc.decade AND gc.genreCount = 
            mgc.maxGenreCount
            ORDER BY gc.decade;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        output = f"\nDecade\t{'Genre':<10}\tNumber of Movies"
        for row in results:
            output += f"\n{row[0]}\t{row[1]:<10}\t{row[2]}"
        output += '\n'
        return output

    def topRuntime(self):
        query = """
            SELECT TOP 10 title, runtime
            FROM media
            ORDER BY runtime DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        output = f"\n{'Title':<30}\tRuntime"
        for row in results:
            output += f"\n{row[0]:<30}\t{row[1]} minutes"
        output += '\n'
        return output

    def topCountry(self, country_query: str):
        query = """
            SELECT TOP 10 m.title, c.productionCountry, m.revenue
            FROM media m
            JOIN producedIn p ON m.mediaID = p.mediaID
            JOIN country c ON p.countryID = c.countryID
            WHERE c.productionCountry LIKE %s
            ORDER BY m.revenue DESC;
        """
        self.cursor.execute(query, (country_query,))
        results = self.cursor.fetchall()
            
        if not results: return f'No movies found for {country_query}'

        output = f"Top Movies from {country_query}\n{'Title':<50}\tRevenue"
        for row in results: 
            output += f"\n{row[0]:<50}\t${round(row[2]):,}"
        output += '\n'
        return output

    def topCompany(self):
        query = """
            SELECT TOP 10 c.productionCompany, COUNT(m.mediaID) AS movieCount
            FROM media m
            JOIN producedBy pb ON m.mediaID = pb.mediaID
            JOIN company c ON pb.companyID = c.companyID
            GROUP BY c.productionCompany
            ORDER BY movieCount DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = f"\n{'Production Company':<20}\tNumber of Movies"
        for row in results: 
            if row[0] != "": output += f"\n {row[0]:<20}\t{row[1]}"
        output += '\n'
        return output

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
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = f"\n{'Actor':<20}\t{'Director':<20}\t{'Count'}"
        for row in results:
            output += f"\n{row[0]:<20}\t{row[1]:<20}\t{row[2]}"
        output += '\n'
        return output
    
    def topCastSize(self):
        query = """
            SELECT TOP 10 m.title, COUNT(mc.castID) AS castSize
            FROM media m
            JOIN actedIn ai ON m.mediaID = ai.mediaID
            JOIN mediaCast mc ON ai.castID = mc.castID
            GROUP BY m.mediaID, m.title
            ORDER BY castSize DESC;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = f"\nCount\tTitle"
        for row in results:
            output += f"\n{row[1]}\t{row[0]}"
        output += '\n'
        return output
    
    def directorMovies(self, director_query):
        try:
            query = """
                SELECT TOP 25 directorName
                FROM director
                WHERE LOWER(directorName) LIKE %s;
            """
            self.cursor.execute(query, (f'%{director_query.lower()}%',))
            results = self.cursor.fetchall()

            if not results: return f'No directors match {director_query}'

            # Print available directors
            print("\nAvailable Directors")
            print("Index\t Name")
            for row in enumerate(results):
                print(f"{row[0]}\t{row[1][0]}")
            
            query = """
                SELECT releaseDate, title
                FROM media
                JOIN directedBy ON media.mediaID = directedBy.mediaID
                JOIN director ON directedBy.directorID = director.directorID
                WHERE LOWER(directorName) LIKE %s
                ORDER BY releaseDate DESC;
            """

            index = int(input('\nWhich director`s movies do you want see? (Type a valid number)\n>'))
            index = max(0, min(index, len(results)))
            director = results[index][0]

            self.cursor.execute(query, (f'{director.lower()}',))
            results = self.cursor.fetchall()
            if results:
                output = f"\n{director}'s Filmography"
                output += "\nRelease Date\tTitle"
                for row in results:
                    output += f"\n{row[0]}    \t{row[1]}"
                output += '\n'
            else:
                output = 'No results found'

            return output
        except ValueError:
            return "You didn't enter a valid number"
    
    def actorMovies(self, actor_query):
        try:
            query = """
                SELECT TOP 25 castName
                FROM mediaCast
                WHERE LOWER(castName) LIKE %s;
            """
            self.cursor.execute(query, (f'%{actor_query.lower()}%',))
            results = self.cursor.fetchall()

            if not results: return f'No Actors match {actor_query}'

            # Print available directors
            print("\nAvailable Actors")
            print("Index\t Name")
            for row in enumerate(results):
                print(f"{row[0]}\t{row[1][0]}")
            
            query = """
                SELECT media.releaseDate, media.title
                FROM media
                JOIN actedIn ON media.mediaID = actedIn.mediaID
                JOIN mediaCast ON actedIn.castID = mediaCast.castID
                WHERE LOWER(castName) LIKE %s
                ORDER BY media.releaseDate DESC;
            """

            index = int(input('\nWhich actor`s movies do you want see? (Type a valid number)\n>'))
            index = max(0, min(index, len(results)))
            actor = results[index][0]

            self.cursor.execute(query, (f'{actor.lower()}',))
            results = self.cursor.fetchall()
            if results:
                output = f"\n{actor}'s Filmography"
                output += "\nRelease Date\tTitle"
                for row in results:
                    output += f"\n{row[0]}    \t{row[1]}"
                output += '\n'
            else:
                output = 'No results found'

            return output
        except ValueError:
            return "You didn't enter a valid number"

    def delete(self):
        print("Deleting database data...\nExpect 8 minutes to delete all the records...")
        try:
            self.connection.autocommit(False)
            self.cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';")
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
            all_tables = self.cursor.fetchall()
            for table in all_tables:
                table_name = str(table[0])
                print(f"Deleting {table_name}")
                self.cursor.execute(f'DELETE FROM {table_name};')
            self.cursor.execute("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';")
            self.connection.commit()
            return "Database deletion successful!"
        except pymssql.Error as e:
            self.connection.rollback()
            return f"Deletion Error {e}"

    def repopulate(self):
        print("Repopulating database...\nExpect 8 minutes to run 95k inserts...")
        try:
            self.run_sql_file(insert_path)
            return "Database repopulation successful!"
        except pymssql.Error as e:
            self.connection.rollback()
            return f"Repopulation Error {e}"
        
    def recreate(self):
        print('Recreating database...')
        try:
            self.run_sql_file(create_path)
            return "Database creation successful!"
        except pymssql.Error as e:
            self.connection.rollback()
            return f"Database creation error {e}"
    
    def run_sql_file(self, file_path):
        save = ''
        self.connection.autocommit(False)
        with open(Path(__file__).parent / file_path, 'r') as file:
            for line in file:
                if not line.strip(): continue

                save += line
                if line.strip().endswith(';'):
                    self.cursor.execute(save)
                    save = ''
        print('Now Time to Commit')
        self.connection.commit()

help_string = """
Available Commands:
search title <query>      - List information about the matching titles?
search actor <query>      - List the filmography of the selected actor?
search director <query>   - List the filmography of the selected director?
language title <query>    - List the languages associated with the title?

top actors                - What 10 actors have the highest filmography revenue?
top directors             - What 10 directors have the highest average IMDB rating?
top composers             - What 10 composers have the highest popularity?
top writers               - What 10 writers have the highest average IMDB ratings?
top movies                - What 10 movies have the highest revenue to budget?
top genre                 - What 10 genres have the most movies?
top genre decades         - What is the most popular genre in each decade?
top runtime               - What movies have the longest runtimes?
top cast_size             - What movies have the largest mediaCastsizes?
top company               - Find the top 10 companies that have made the most movies
top country <countryName> - Find the top 10 movies by revenue for a <countryName>
top actor_director        - Find the top 10 most frequent actor-director combinations?

delete                    - Delete the database content.
repopulate                - Repopulate the database.
recreate                  - Recreate the database assuming the tables were all deleted
help                      - Show this help page.
quit                      - Leave the database.
"""

look_at_help_string = "Please type 'help' for a list of valid commands and their syntax."

def parseCommand(command: str, db: Database):
    command_parts = command.strip().lower().split(" ")
    if not command_parts:
        return "Command is empty"
    
    cmd = command_parts[0]
    args = command_parts[1:]
    try:
        match cmd:
            case 'search':
                query = ' '.join(args[1:])
                match args[0]:
                    case 'title': return db.searchTitle(query)
                    case 'actor': return db.actorMovies(query)
                    case 'director': return db.directorMovies(query)
                    case _: return f"{args[0]} is an unknown argument for search. {look_at_help_string}"
            case 'language':
                match args[0]:
                    case 'title': return db.languageTitle(' '.join(args[1:]))
                    case _: return f"{args[0]} is an unknown argument for language. {look_at_help_string}"
            case 'top':
                match args[0]:
                    case 'actors': return db.topActors()
                    case 'directors': return db.topDirectors()
                    case 'composers': return db.topComposers()
                    case 'writers': return db.topWriters()
                    case 'movies': return db.topMovies()
                    case 'runtime': return db.topRuntime()
                    case 'genre': 
                        if len(args) == 1: return db.countGenre() 
                        elif args[1] == 'decades': return db.topGenreDecade() 
                        else: return f"{args[1]} is an invalid argument for the top genre command"
                    case 'company': return db.topCompany()
                    case 'country': return db.topCountry(' '.join(args[1:]))
                    case 'cast_size': return db.topCastSize()
                    case 'actor_director': return db.topActorDirector()
                    case _: return f"{args[0]} is an unknown argument for top. {look_at_help_string}"
                pass
            case 'delete': return db.delete()
            case 'repopulate': return db.repopulate()
            case 'recreate': return db.recreate()
            case 'help': return help_string
            case 'quit':
                print("Exiting Database...")
                exit(0)
            case _:
                return f"Unknown command: {cmd}.\n{look_at_help_string}"
    except pymssql.Error as e:
        print('Has the database been populated?')
        return f"SQL Error: {e}"

def loadConfig():
    try:
        with open('auth.cfg', 'r') as configFile:
            config = configFile.read().strip().split('\n')
            username, password = None, None
            for line in config:
                if line.startswith("username="):
                    username = line.split('=')[1]
                elif line.startswith("password="):
                    password = line.split('=')[1]

        if not username or not password:
            print("Username or password not provided in config file.")
            exit(1)
        
        return username, password

    except FileNotFoundError:
        print("Could not find config file.")
        return
    except Exception as ex:
        print(f"Error reading config file: {ex}")
        return

def main():
    username, password = loadConfig()
    connection = pymssql.connect(
        server='uranium.cs.umanitoba.ca',
        user=f'{username}',
        password=f'{password}',
        database=f'cs3380'
    )

    db = Database(connection)
    print("Database Connected!")

    print("Type 'help' for available commands.")
    while True:
        console = input('media > ')
        print(parseCommand(console, db))


if __name__ == "__main__":
    main()