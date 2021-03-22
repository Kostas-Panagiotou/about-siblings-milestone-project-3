import os
from flask import (
       Flask, flash, render_template,
       redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_superheroes")
def get_superheroes():
    superheroes = mongo.db.siblings.find()
    return render_template("superheroes.html", superheroes=superheroes)


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
    flash("You have been logged out of your account!")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")), 
            debug=True)
