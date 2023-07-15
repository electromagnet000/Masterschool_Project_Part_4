from .Data_interface import User_data

class User(User_data):
    def __init__(self, user_data):
        self.name = user_data["name"]
        self.password = user_data['password']
        self.movies = user_data['movies']
    def get_username(self):
        return self.name

    def get_password(self):
        return self.password

    def movie_list(self):
        return self.movies


