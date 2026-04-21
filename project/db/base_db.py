from abc import ABC, abstractmethod

class BaseDatabase(ABC):
    def __init__(self, connection=None):
        self.connection = connection
        self.cursor = connection.cursor() if connection else None
        self.mock_mode = connection is None

    @abstractmethod
    def _execute_query(self, query, params=None):
        pass

    @abstractmethod
    def searchTitle(self, title_query: str):
        pass

    @abstractmethod
    def languageTitle(self, title_query: str):
        pass

    @abstractmethod
    def topActors(self):
        pass

    @abstractmethod
    def topDirectors(self):
        pass

    @abstractmethod
    def topComposers(self):
        pass

    @abstractmethod
    def topWriters(self):
        pass

    @abstractmethod
    def topMovies(self):
        pass

    @abstractmethod
    def countGenre(self):
        pass

    @abstractmethod
    def topGenreDecade(self):
        pass

    @abstractmethod
    def topRuntime(self):
        pass

    @abstractmethod
    def topCountry(self, country_query: str):
        pass

    @abstractmethod
    def topCompany(self):
        pass

    @abstractmethod
    def topActorDirector(self):
        pass

    @abstractmethod
    def topCastSize(self):
        pass

    @abstractmethod
    def directorMovies(self, director_query: str):
        pass

    @abstractmethod
    def actorMovies(self, actor_query: str):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def recreate(self):
        pass
    
    @abstractmethod
    def repopulate(self):
        pass
