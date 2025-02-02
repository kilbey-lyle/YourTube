import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def welcome():
    #if user is still signed in take them to feed
    try:
        if session['user']:
            return redirect(url_for('feed'))
    except:
        print("No user logged in")
    #if no user logged in show welcome page
    return render_template('welcome.html')


@app.route("/feed")
def feed():
    #get all reviews marked as public
    reviews = mongo.db.reviews.find({"is_public":"on"})
    return render_template("feed.html", reviews=reviews)

@app.route("/your_reviews")
def your_reviews():
    reviews = mongo.db.reviews.find({"created_by": session['user']})
    return render_template("your_reviews.html", reviews=reviews)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        user = user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if user:
            if check_password_hash(user["password"], request.form.get("password")):
                session['user'] = request.form.get("username").lower()
                flash(f"Welcome back {session['user']}!")
                return redirect(url_for('feed'))
            else:
                print("failed login")
                flash(f'Password or username is incorrect')
                return redirect(url_for('signin'))
        else:
            flash(f'Password or username is incorrect')
            return redirect(url_for('signin'))

    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        #check if user is already registered
        user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if user:
            flash(f'Unable to complete sign up, please try again')
            return redirect(url_for('signin'))
    
        new_user = {
            "username": request.form.get("username").lower(),
            "password":generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(new_user)
        session['user'] = request.form.get("username").lower()
        flash(f'Welcome {session['user']}!')
        return redirect(url_for('feed'))

    return render_template("signup.html")

@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route("/create_review", methods=["GET", "POST"])
def create_review():
    if request.method == "POST":
        is_public = "on" if request.form.get("is_public") else "off"
        new_review = {
            "channel_name": request.form.get("channel_name"),
            "channel_link": request.form.get("channel_link"),
            "rating": request.form.get("rating"),
            "genre": request.form.get("genre"),
            "description": request.form.get("description"),
            "is_public": is_public,
            "created_by": session['user'],
            "date_created": datetime.today().strftime('%d/%m/%y')
        }

        mongo.db.reviews.insert_one(new_review)
        flash('Review created')
        return redirect(url_for('your_reviews'))

    return render_template("create_review.html")

@app.route('/edit_review/<review_id>', methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        is_public = "on" if request.form.get("is_public") else "off"
        updated_review = {
            "channel_name": request.form.get("channel_name"),
            "channel_link": request.form.get("channel_link"),
            "rating": request.form.get("rating"),
            "genre": request.form.get("genre"),
            "description": request.form.get("description"),
            "is_public": is_public,
        }
        

        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set":updated_review})
        flash('Review updated')
        return redirect(url_for('your_reviews'))

    review = mongo.db.reviews.find_one({"_id":ObjectId(review_id)})
    return render_template('edit_review.html', review=review)

@app.route('/delete_review/<review_id>')
def delete_review(review_id):
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    flash('Review deleted')
    return redirect(url_for('feed'))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
