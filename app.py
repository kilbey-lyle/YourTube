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
@app.route("/feed")
def feed():
    reviews = mongo.db.reviews.find()
    return render_template("feed.html", reviews=reviews)

@app.route("/your_reviews")
def your_reviews():
    reviews = mongo.db.reviews.find()
    return render_template("your_reviews.html", reviews=reviews)

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print("this is a post")
        #check if user is already registered
        user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if user:
            return redirect(url_for('signin'))
    
        new_user = {
            "username": request.form.get("username").lower(),
            "password":generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(new_user)

        session['user'] = request.form.get("username").lower()
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
