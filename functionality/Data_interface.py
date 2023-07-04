import json
from abc import ABC, abstractmethod

class Data_manager(ABC):
    @abstractmethod
    def get_all_users(self):
        pass
    @abstractmethod
    def get_user_movies(self, user_id):
        pass

