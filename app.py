from functionality.Data_managment import json_data_manager
from functionality.user_data import User
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import os

"""
I like to assign global variables at the top for ease of use
"""
app = Flask(__name__)
app.secret_key = os.urandom(24)
data_manager = json_data_manager("dataManagement/json_data.json")

"""
The list of users page
"""


@app.route("/", methods=["GET", "POST"])
def list_users():
    session.pop('user', None)
    users = data_manager.list_all_users()

    return render_template("users.html", users=users)


"""
The login function
"""


@app.route('/users/login/<int:user_id>', methods=["GET", "POST"])
def login(user_id):
    msg = ""
    chosen_user = [user_data for user_data in data_manager.list_all_users() if user_data["id"] == user_id]
    session_user = User(chosen_user[0])

    if request.method == "POST":
        session.pop("user", None)

        if request.form.get("password") == session_user.password and request.form.get("username") == session_user.name:
            print(session_user.password)
            session['user'] = request.form["username"]
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            msg = "Please make sure Username and Password are correct"

    return render_template("login_page.html", user_id=user_id, user=chosen_user[0], msg=msg)


"""
User Settings
I will use this as the inital hub for the all the possible settings the user might want to change
"""


@app.route("/users/<int:user_id>/settings", methods=["GET", "POST"])
def user_settings(user_id):
    return render_template("settings.html", user_id=user_id)


"""
Account settings
This will deal with a persons personal details
"""


@app.route("/users/<int:user_id>/settings/account_settings", methods=["GET", "POST"])
def account_settings(user_id):

    if request.method == "POST":
        chosen_user = [user_data for user_data in data_manager.list_all_users() if user_data["id"] == user_id]
        password = request.form.get("current_password")

        if password == chosen_user[0]['password']:
            username = request.form.get("username")
            new_password = request.form.get("new_password")

            if not new_password:
                new_password = chosen_user[0]['password']
            if not username:
                username = chosen_user[0]['name']

            data_manager.update_user_details(chosen_user[0], username, new_password)
            flash("details updated")
            return render_template("account settings.html", user_id=user_id)

        flash("Password not correct")
        return render_template("account settings.html", user_id=user_id)
    return render_template("account settings.html", user_id=user_id)


"""
The Movie Database of the user
"""


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    if g.user:
        the_movies = data_manager.get_user_movies(user_id)
        return render_template("user_page.html", user_id=user_id, user=session['user'], movies=the_movies)
    return redirect(url_for("list_users"))


"""
Adds a new user
"""


@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        new_user = request.form.get("name")
        new_user_psw = request.form.get("password")
        data_manager.add_user(new_user, new_user_psw)
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


"""
Error Handling
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/something")
def something():
    return render_template("something.html")


"""
User space protection
"""


@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']


if __name__ in "__main__":
    app.run(debug=True)
