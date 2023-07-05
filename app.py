from functionality.Data_managment import json_data_manager, CSVDataManager
from flask import Flask, render_template, request, redirect, url_for, jsonify

"""
I like to assign global variables at the top for ease of use
"""
app = Flask(__name__)
app.secret_key = "super_secret"
data_manager = json_data_manager("dataManagement/json_data.json")


"""
The list of users page
"""
@app.route("/", methods=["GET", "POST"])
def list_users():
    users = data_manager.list_all_users()

    return render_template("users.html", users=users)



"""
The Movie Database of the user
"""
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = [name for name in data_manager.list_all_users() if name["id"] == user_id]
    the_movies = data_manager.get_user_movies(user_id)

    return render_template("user_page.html", user_id=user_id, user=user, movies=the_movies)



"""
Adds a new user
"""
@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        new_user = request.form.get("name")
        data_manager.add_user(new_user)
        return redirect(url_for("list_users"))

    return render_template("add_user.html")



"""
Adds a movie to the users database
"""
@app.route('/users/<int:user_id>/add_movie', methods=["GET", "POST"])
def add_movie(user_id):
    user_movie = data_manager.get_user_movies(user_id)

    if request.method == "POST":
        movie_title = request.form.get("movie_name")
        movie_notes = request.form.get("movie_notes")

        success_message = data_manager.add_movie(user_id, movie_title, movie_notes)
        new_movie_list = data_manager.get_user_movies(user_id)

        return render_template("add_movie.html", movies=new_movie_list, id=user_id, success_message=success_message)
    return render_template("add_movie.html", movies=user_movie, id=user_id)



"""
Updates the users notes on the film
"""

@app.route('/users/<user_id>/update_movie/<movie_id>', methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    if request.method == "POST":
        note_updates = request.form.get("notes")
        print(note_updates)
        success_message = data_manager.update_user_movie(user_id, movie_id, note_updates)

        return redirect(url_for("user_movies", user_id=user_id, success_message=success_message))
    return render_template("update.html", id=user_id, movie_id=movie_id)


"""
Deletes a film from the users database
"""


@app.route("/users/<user_id>/delete_movie/<movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    movie_to_delete = request.form.get("delete_movie")
    success_message = data_manager.delete_movie(user_id, movie_id, movie_to_delete)
    return redirect(url_for("user_movies", user_id=user_id, success_message=success_message))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.route("/something")
def something():
    return render_template("something.html")

if __name__ in "__main__":
    app.run(debug=True)

