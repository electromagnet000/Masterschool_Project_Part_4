from functionality.Data_managment import json_data_manager, CSVDataManager
from flask import Flask, render_template, request, redirect, url_for

"""
I like to assign global variables at the top for ease of use
"""
app = Flask(__name__)

data_manager = json_data_manager("dataManagement/json_data.json")


@app.route('/')
def home():
    return "welcome user"


@app.route("/users")
def list_users():
    users = data_manager.list_all_users()
    return render_template("users.html", users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    the_movies = data_manager.get_user_movies(user_id)
    return str(the_movies)


@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        new_user = request.form.get("name")
        data_manager.add_user(new_user)
        return redirect(url_for("list_users"))

    return render_template("add_user.html")


@app.route('/users/<user_id>/add_movie')
def add_movie():
    pass


@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie():
    pass


@app.route("/users/<user_id>/delete_movie/<movie_id>")
def delete_movie():
    pass


if __name__ in "__main__":
    app.run(debug=True)

# json_data = json_data_manager("dataManagement/json_data.json")
# users = json_data.update_user_movie(1)
# csv_data = CSVDataManager("dataManagement/json_data.json")
# csv_user = csv_data.get_user_movies(1)
# print(users)
