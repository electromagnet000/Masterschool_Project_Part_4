from functionality.Data_managment import json_data_manager
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, request, redirect, url_for, flash, g
import json
from sqlalchemy import text, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship, sessionmaker
from data_models import db, Data, Movie, User
import os
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user

"""
I like to assign global variables at the top for ease of use
"""
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/Sergiu Howie/PycharmProjects/Masterschool_Project_part_4/Masterschool_Project_Part_4/data/webDatabase.sqlite"
db.init_app(app)
data_manager = json_data_manager("dataManagement/json_data.json")
Base = declarative_base()
engine = create_engine("sqlite:///C:/Users/Sergiu Howie/PycharmProjects/Masterschool_Project_part_4/Masterschool_Project_Part_4/data/webDatabase.sqlite",echo=True)

"""
Session
"""

Session = sessionmaker(bind=engine)
session = Session()

"""
Activates
"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
Classes
"""

# Sql-data-manager
class SQLDatamanager:

    def get_users():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users"))
            user_data = [{"id" : row[0], "username" : row[1], "password" : row[2]} for row in result]
            return user_data

    def get_movies(user_id):
        with engine.connect() as conn:
            user_movies_imdb_id = conn.execute(text("SELECT * From data WHERE user_id == :user_id "), user_id=user_id)

            for item in user_movies_imdb_id:
                L_F_M = Movie.query.filter_by(imdb_id=item.imdb_id).first()
                if L_F_M:
                    movie_obj = {"imdbID" : L_F_M.imdb_id, "Title": L_F_M.title, "year": L_F_M.year, "Poster": L_F_M.poster, "imdbRating" : L_F_M.imdb_rating}


    """
    sync all the current json data in sqlite database
    """

    def sync_data_users():
        with open("dataManagement/json_data.json", "r") as data:
            data = json.load(data)

            try:
                for item in data:
                    new_user = User(username=item["name"], password=item["password"])
                    session.add(new_user)

                session.commit()
            except Exception as e:
                print(f'there was a problem {e}')
                session.rollback()

    def sync_data_movies():
        with open("dataManagement/json_data.json", "r") as data:
            file_data = json.load(data)

            for user_data in file_data:
                movies_data = user_data.get('movies', [])
                try:
                    for item in movies_data:
                        imdb_id = item.get("imdbID")
                        sync_movie = Movie(
                            imdb_id=imdb_id,
                            title=item.get('Title'),
                            year=item.get('Year'),
                            poster=item.get('Poster'),
                            imdb_rating=item.get('imdbRating')
                        )
                        # skips duplicates
                        movie_exists = Movie.query.filter_by(imdb_id=imdb_id).first()
                        if movie_exists:
                            continue

                        session.add(sync_movie)

                    session.commit()

                except Exception as e:
                    print(f'there was a problem {e}')
                    session.rollback()

    def sync_data_user_movies_data():
        with open("dataManagement/json_data.json", "r") as data:
            file_data = json.load(data)

            try:
                # to get the user id
                for item in file_data:
                    # to get the users movie, list
                    movies = item.get("movies", [])
                    for movie_data in movies:
                        new_data_record = Data(
                            user_id=item["id"],
                            movie_imdb_id=movie_data["imdbID"]
                        )
                        session.add(new_data_record)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f'error {e}')


class UserForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    password = StringField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")


""" 
Alternate interactions
"""

# sql = text('SELECT * FROM movies')
# result = db.engine.execute(sql)
#
# for row in result:
#     print(row['title'])

"""
The list of users page
"""


@app.route("/", methods=["GET", "POST"])
def list_users():
    users = User.query.order_by(User.id)
    return render_template("users.html", users=users)


"""
The login function
"""


@app.route('/users/login/<int:user_id>', methods=["GET", "POST"])
def login(user_id):
    chosen_user = [user_data for user_data in SQLDatamanager.get_users() if user_data['id'] == user_id]

    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user:
            check_psw = request.form.get("password")
            if str(user.password) == str(check_psw):
                login_user(user)
                flash("login Successful!")
                return redirect(url_for("user_movies", user_id=user.id))
            else:
                flash("Wrong password - try again")
        else:
            flash("That user doesn't exist try again")

    return render_template("login_page.html", user_id=user_id, user=chosen_user[0])

"""
Log out function
"""
@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("list_users"))




"""
User Settings
I will use this as the inital hub for the all the possible settings the user might want to change
"""

@login_required
@app.route("/users/<int:user_id>/settings", methods=["GET", "POST"])
def user_settings(user_id):
    return render_template("settings.html", user_id=user_id)


"""
Delete account
"""

@login_required
@app.route("/users/<int:user_id>/delete_user", methods=["POST"])
def delete_user(user_id):
    chosen_user = [user_data for user_data in data_manager.list_all_users() if user_data["id"] == user_id]
    if request.form.get("delete_user") == chosen_user[0]["password"]:
        data_manager.delete_user(user_id)
        return redirect(url_for('list_users'))
    else:
        flash("Password not correct")
        return render_template("settings.html", user_id=user_id)


"""
Account settings
This will deal with a persons personal details
"""

@login_required
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
Personalise settings
"""

@login_required
@app.route("/users/<int:user_id>/settings/profile_settings")
def profile_settings(user_id):
    return render_template("Personalised settings.html", user_id=user_id)


"""
Accessibility settings
"""

@login_required
@app.route("/users/<int:user_id>/settings/accessibility_settngs")
def accessibility_settings(user_id):
    return render_template("Accessibility settings.html", user_id=user_id)


"""
The Movie Database of the user
"""

@login_required
@app.route('/users/<int:user_id>')
def user_movies(user_id):
    the_movies = data_manager.get_user_movies(user_id)
    return render_template("user_page.html", user_id=user_id, user=current_user, movies=the_movies)



"""
Adds a new user
"""


@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    form = UserForm()

    if request.method == "POST":
        try:
            new_user = request.form.get("name")
            new_user_psw = request.form.get("password")
            user = User.query.filter_by(username=new_user).first()
            if user is None:
                user = User(username=new_user, password=new_user_psw)
                db.session.add(user)
                db.session.commit()
                flash("User added Successfully")
                return redirect(url_for("list_users"))
            else:
                flash("sorry that username is already taken, please chose another")

        except Exception:
            flash("error occured")
            session.rollback()
            return redirect(url_for("list_users"))

    return render_template("add_user.html", form=form)


"""
Adds a movie to the users database
"""

@login_required
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

@login_required
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    if request.method == "POST":
        note_updates = request.form.get("notes")
        print(note_updates)
        success_message = data_manager.update_user_movie(user_id, movie_id, note_updates)

        return redirect(url_for("user_movies", user_id=user_id, success_message=success_message))
    return render_template("update.html", user_id=user_id, movie_id=movie_id)


"""
Deletes a film from the users database
"""

@login_required
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

if __name__ in "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
