import os
from flask import (
       Flask, flash, render_template,
       redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
import bson

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    category = list(mongo.db.genres.find().sort("category_name", 1))
    return render_template("index.html", category=category)


@app.route("/about")
def about():
    category = list(mongo.db.genres.find().sort("category_name", 1))
    return render_template("about.html", category=category)


@app.route("/methodology")
def methodology():
    category = list(mongo.db.genres.find().sort("category_name", 1))
    return render_template("methodology.html", category=category)


@app.route("/documentary")
def documentary():
    category = list(mongo.db.genres.find().sort("category_name", 1))
    return render_template("documentary.html", category=category)


# create signup functionality
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check the username if already occupied in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
        }
        mongo.db.users.insert_one(signup)

        # use cookie for the  new session user
        session["user"] = request.form.get("username").lower()
        flash("Thanks! your account has been successfuly created")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("signup.html")


#  login-logout functionality
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    THIS IS FUNCTION DOCUMENTATION
    """
    if request.method == "POST":
        # check if the username is occupied in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            # ensure the hash password it was matced with the user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))

            else:
                # wrong password matched
                flash("Wrong Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username dont exist in the db
            flash("Wrong Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # logout user from session cookies
    session.pop("user")
    flash("You have been logged out of your account!")
    return redirect(url_for("login"))


# stories functionality
@app.route("/get_stories")
def get_stories():
    """
    Finds all stories in the database and sorts the cards
    chronologically with more recent items first based on
    the datetime info stored in '_id'
    """
    stories = list(mongo.db.stories.find().sort("_id", -1))
    return render_template("stories.html", stories=stories)


# search functionality
@app.route("/search", methods={"GET", "POST"})
def search():
    query = request.form.get("query")
    stories = list(mongo.db.stories.find({"$text": {"$search": query}}))
    return render_template("stories.html", stories=stories)


@app.route("/add_story", methods=["GET", "POST"])
def add_story():
    if request.method == "POST":
        """
        If post method is executed, creates a dictionary for form
        and inserts user input into the database
        """
        stories = {
            "category_name": request.form.get("category_name"),
            "stories_name": request.form.get("stories_name"),
            "stories_description": request.form.get("stories_description"),
            "img_url": request.form.get("img_url"),
            "created_by": session["user"]
        }
        mongo.db.stories.insert_one(stories)
        flash("Your Story Was Successfully Added")
        return redirect(url_for("get_stories"))

    """Sort form values in alphabetical order"""
    categories = mongo.db.categories.find().sort("category_name", 1)
    stories = mongo.db.categories.find().sort("stories", 1)
    return render_template(
        "add_story.html", stories=stories,  categories=categories)


@app.route("/edit_stories/<stories_id>", methods=["GET", "POST"])
def edit_stories(stories_id):
    if request.method == "POST":
        """
        If post method is executed, finds stories by id
        and updates database with updated form input
        """
        submit = {
            "category_name": request.form.get("category_name"),
            "stories_name": request.form.get("stories_name"),
            "stories_description": request.form.get("stories_description"),
            "img_url": request.form.get("img_url"),
            "created_by": session["user"]
        }
        mongo.db.stories.update({"_id": ObjectId(stories_id)}, submit)
        flash("Your Story Updated Successfully!")

    stories = mongo.db.stories.find_one({"_id": ObjectId(stories_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_stories.html", stories=stories, categories=categories)


@app.route("/delete_stories/<stories_id>")
def delete_stories(stories_id):
    """Finds stories by id and removes it from the database"""
    mongo.db.stories.remove({"_id": ObjectId(stories_id)})
    flash("Your Story is Successfully Deleted")
    return redirect(url_for("get_stories"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("You Just Added a new Category")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash(" Your Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Your Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# 500 page function
@app.errorhandler(500)
def internal_server(error):
    # the 500 status is set explicitly
    return render_template('500.html', title='500'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
