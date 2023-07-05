from .Data_interface import Data_manager
import json
import csv
import pandas as pd
import requests


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
        users = [dict(zip(users_id, users_names))]

        # Lastly I return the information
        return users

    """
    Returns a list of all users and their data from the json file
    """

    def list_all_users(self):
        # Using list comprehension im able to extract specific information from the json data
        users = [user for user in self.data]
        # Lastly I return the information
        return users

    """
    Creates a brand new user
    """

    def add_user(self, new_username):
        new_id = self.generate_id()

        new_user = {"id": new_id, "name": new_username, "movies": []}

        self.data.append(new_user)

        with open(self.filename, "w") as new_file:
            json.dump(self.data, new_file)
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
                return [f"No movies found for user : {user['name']}"]

            return user_movies
        except ValueError as e:
            print("User ID not found")

    """
    Update Function : offers users a way to update the film ratings
    """

    def update_user_movie(self,user_id, chosen_title, notes):

        # now I filter through the movie data for chosen title
        for user in range(len(self.data)):
            if self.data[user]["id"] == user_id:
                for movie in self.data[user]["movies"]:
                    # here I filter through the chosen users movies with a simple if statement
                    if movie["id"] == chosen_title:
                        # now we assign the new rating and return a confirmation message
                        movie["Notes"] = notes

                # lastly we store the updated data
                with open(self.filename, "w") as new_file:
                    json.dump(self.data, new_file)
                    return "success"

    """
    Add movie function
    """

    def add_movie(self, user_id, title, user_notes):

        # using my api key I can get access to the OMDB api
        API_KEY = "ae79a6f6"
        # sends a get request to gather specific information from Movies API
        api_url = "http://www.omdbapi.com/?t={}&apikey={}".format(title, API_KEY)
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        # if the response status is 200 then it proceeds with the request
        if response.status_code == requests.codes.ok:
            # creates a variable for the text repsonse

            fetched_data = response.json()

            # creates an empty dict with an id number for the film
            requested_data = {}

            movies = [movie for sublist in self.data if sublist['id'] == user_id for movie in sublist["movies"]]

            requested_data['id'] = len(movies) + 1

            # creates the parameters we need to get
            requested_parameters = ['Title', 'Year', 'imdbRating', 'Poster', 'imdbID']

            # iterates through the keys to get the correct parameters and stores them in requested_data
            for key, value in fetched_data.items():
                if key in requested_parameters:
                    requested_data[key] = value

            requested_data["Notes"] = user_notes

            # checks if anything was actually fetched
            try:
                if not requested_data['Title']:
                    return f"Movie {title} not found in API"
            except KeyError as e:
                return f"Movie {title} not found in API database"

            for data in range(len(self.data)):
                if self.data[data]["id"] == user_id:
                    self.data[data]["movies"].append(requested_data)

            # creates a new file with all the added information
            with open(self.filename, "w") as new_file:
                json.dump(self.data, new_file)
                return f"Movie {title} successfully added"

    """
    A function to Delete movies
    """
    def delete_movie(self, user_id, movie_id, title):

        # Using a for loop we can filter information until we get the desired info
        for user in range(len(self.data)):
            # here we check if the user id is correct
            if self.data[user]["id"] == int(user_id):
                # here we loop over each film and check if the parameters are correct such as title and film id
                for movie in self.data[user]["movies"]:
                    if movie["Title"] == title and movie["id"] == int(movie_id):
                        # If the parameters are correct then delete the film
                        self.data[user]["movies"].remove(movie)

        """
        Now theres a potential issue, when you delete a film the total films will reduce by 1 each time you use this 
        function this will cause problems when adding new films when generating their id. Because the generate a film Id
        uses len("movies) + 1 this will cause problems
        """

        """
        My solution is to make a for loop that updates the film Id when the delete function activated
        """

        updated_id = 1

        for user in range(len(self.data)):
            if self.data[user]["id"] == int(user_id):
                for movie in self.data[user]["movies"]:
                    movie["id"] = updated_id
                    updated_id += 1
        """
        Now the film IDs are unique 
        """

        with open(self.filename, "w") as new_file:
            json.dump(self.data, new_file)


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

    def csv_get_all_users(self):
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

    def csv_get_user_movies(self, user_id):
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

    def csv_update_user_movie(self, user_id, movie_name):
        pass

    def csvdelete_movie(self, user_id, title):

        movies = self.get_user_movies(user_id)
        return movies




