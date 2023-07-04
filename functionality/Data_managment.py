from .Data_interface import Data_manager
import json
import csv
import pandas as pd


# handles all the json datafiles
class json_data_manager(Data_manager):

    # extracts the data, then it's ready to be used
    def __init__(self, filename):
        # opens the json file and stores it
        with open(filename, "r") as data:
            file_data = json.load(data)

        # assigns it to the class so that other functions are able to extract the data
        self.data = file_data
        self.filename = filename

    """
    A function that generates an ID
    """

    def generate_id(self):
        return len(self.list_all_users()) + 1

    """ 
    A function that gets the users information such as Name and ID number
    """

    def get_all_users(self):
        # Using list comprehension im able to extract specific information from the json data
        users_names = [user["name"] for user in self.data]
        users_id = [user["id"] for user in self.data]

        # I like to zip the information and turn it into a dictionary for a clear relationship between the id/name.
        users = dict(zip(users_id, users_names))

        # Lastly I return the information
        return users

    """
    returns a list of all users and their data
    """

    def list_all_users(self):
        # Using list comprehension im able to extract specific information from the json data
        users = [user for user in self.data]

        # Lastly I return the information
        return users

    """
    creates a brand new user
    """

    def add_user(self, new_username):
        users = self.list_all_users()
        new_id = self.generate_id()

        new_user = {"id": new_id, "name": new_username, "movies": []}

        users.append(new_user)

        with open(self.filename, "w") as new_file:
            json.dump(users, new_file)
            print(f"Successfully added {new_username}")

    """
    Gets the users movies
    Returns a list of dictionaries containing the films
    """

    def get_user_movies(self, user_id):
        try:
            # if the user id is not found within the data file then it will return a message stating that the user is not found
            if user_id not in range(1, len(self.data) + 1):
                raise ValueError
            # Using list comprehension im extracting the movies from the given user_id
            user_movies = [movie for sublist in self.data if sublist["id"] == user_id for movie in sublist["movies"]]

            # If there are no movies found then it returns a message saying nothing was found
            if not user_movies:
                user = self.data[user_id - 1]
                return f"No movies found for user : {user['name']}"

            return user_movies
        except ValueError as e:
            print("User ID not found")

    def update_user_movie(self, user_id):

        user_data = self.data
        movies = self.get_user_movies(user_id)

        """
        Usually the user would type the title of the film to update them 
        however I dyslexia and I want to minimise the error chance, so 
        I would rather have people type the id number or the title whichever makes them 
        more comfortable
        """
        print(movies)
        chosen_title = input("please either write the 'Id' or 'Name' of the movie you want to update")

        # now I filter through the movie data for chosen title
        for sublist in range(len(user_data)):
            if user_data[sublist]["id"] == user_id:
                for movie in user_data[sublist]["movies"]:
                    # here I filter through the chosen users movies with a simple if statement
                    if str(movie["id"]) == chosen_title or movie["name"].lower() == chosen_title.lower():

                        # if the movie is found I would like the user to see visual confirmation of the movie
                        print(movie)

                        # human error handling to make sure that the rating is between 0 - 10
                        while True:
                            new_rating = float(input("What is the new rating you want the movie to have : "))
                            if new_rating > 10 or new_rating < 0:
                                print("please enter a rating between 0 - 10")
                                continue
                            break

                        # now we assign the new rating and return a confirmation message
                        movie["rating"] = new_rating

                # lastly we store the updated data
                with open(self.filename, "w") as new_file:
                    json.dump(user_data, new_file)
                    return "success"


# here is a csv data manager
class CSVDataManager(Data_manager):
    def __init__(self, filename):

        """
        Because our initial file handler was a .json I need to make a converter for our json data into csv data
        """
        # self.filename is none, because now it is flexible to change according to whichever filetype is loaded
        self.filename = None

        # if a .json is loaded in the filename then a simple conversion is necessary to use ,and store it as a csv
        if ".json" in filename:
            with open(filename, "r") as data:
                # using pandas we are reading the json file and converting it into a csv
                df = pd.read_json(data)
                df.to_csv("csv_data.csv", index=False)

                # We now have the csv data file conversion of the json, now its appropriate as the self.filename
                self.filename = "csv_data.csv"

        # I only have two data types json and csv, so if its not a .json file loaded its a .csv
        else:
            self.filename = filename

    """ 
    A function that gets the users information such as Name and ID number
    """

    def get_all_users(self):
        # opening the filedata
        with open(self.filename, "r") as data:
            # using pandas to create a readable structure
            df = pd.read_csv(data)

            # extracting the user id/name using list comerhension
            user_names = [row for row in df.name]
            users_id = [row for row in df.id]

            # create the users information into a dictionary
            user_information = dict(zip(users_id, user_names))

            return user_information

    """
    Gets the users movies
    
    Because the csv format is different from json I cant copy and paste the same code from the json DataMangager, luckily 
    csv has its upsides so I can make it easier for myself
    
    Returns a list of dictionaries containing the films
    """

    def get_user_movies(self, user_id):
        # opens the csv
        with open(self.filename, "r") as data:
            df = csv.DictReader(data)

            # I like to implement try functions to handle errors
            try:
                # using list comprehension I am able to return the movies from the chosen user
                movies = [row for sublist in df if sublist["id"] == str(user_id) for row in sublist["movies"]]
                if not movies:
                    # If no movies were found I want to return a message
                    return "I'm sorry theres no movies saved for this user"
                return movies

            except Exception as e:
                return f"I'm sorry there seems to be an error {e}"

    def update_user_movie(self, user_id, movie_name):
        pass

    def delete_movie(self, user_id, title):

        movies = self.get_user_movies(user_id)
        return movies
