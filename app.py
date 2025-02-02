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
    #Get all reviews marked as public and pass to feed screen
    reviews = mongo.db.reviews.find({"is_public":True})
    return render_template("feed.html", reviews=reviews)

@app.route("/your_reviews")
def your_reviews():
    #get all reviews for current user and pass to your reviews screen
    reviews = mongo.db.reviews.find({"created_by": session['user']})
    return render_template("your_reviews.html", reviews=reviews)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        #get user document submitted
        user = user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        #checks if user submitted is in DB
        if user:
            #check if password is correct and if macth redirect to feed screen
            if check_password_hash(user["password"], request.form.get("password")):
                session['user'] = request.form.get("username").lower()
                flash(f"Welcome back {session['user']}!")
                return redirect(url_for('feed'))
            #if password incorrect show error
            else:
                print("failed login")
                flash(f'Password or username is incorrect')
                return redirect(url_for('signin'))
        #if user does not exsit show error
        else:
            flash(f'Password or username is incorrect')
            return redirect(url_for('signin'))

    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        #gets user submitted from DB
        user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        #check if user is already registered and shows error if true
        if user:
            flash(f'Unable to complete sign up, please try again')
            return redirect(url_for('signin'))
        #creates object to be added to DB
        new_user = {
            "username": request.form.get("username").lower(),
            "password":generate_password_hash(request.form.get("password"))
        }
        #adds user to DB
        mongo.db.users.insert_one(new_user)
        #adds username to session cookie
        session['user'] = request.form.get("username").lower()
        flash(f'Welcome {session['user']}!')
        return redirect(url_for('feed'))

    return render_template("signup.html")

@app.route("/signout")
def signout():
    #clear session cookie
    session.clear()
    return redirect(url_for('welcome'))

@app.route("/create_review", methods=["GET", "POST"])
def create_review():
    if request.method == "POST":
        #creates var to hold is_public checkbox as a boolean
        is_public = True if request.form.get("is_public") else False
        #Creates object to be added to DB
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
        #adds object to DB
        mongo.db.reviews.insert_one(new_review)
        flash('Review created')
        return redirect(url_for('your_reviews'))

    return render_template("create_review.html")

@app.route('/edit_review/<review_id>', methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        #creates var to hold is_public checkbox as a boolean
        is_public = True if request.form.get("is_public") else False
        #Creates object to be added to DB
        updated_review = {
            "channel_name": request.form.get("channel_name"),
            "channel_link": request.form.get("channel_link"),
            "rating": request.form.get("rating"),
            "genre": request.form.get("genre"),
            "description": request.form.get("description"),
            "is_public": is_public,
        }
        
        #updates review with new updates submitted
        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set":updated_review})
        flash('Review updated')
        return redirect(url_for('your_reviews'))

    #gets review needed to be placed into form
    review = mongo.db.reviews.find_one({"_id":ObjectId(review_id)})
    return render_template('edit_review.html', review=review)

@app.route('/delete_review/<review_id>')
def delete_review(review_id):
    #deletes document from DB based on ID
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    flash('Review deleted')
    return redirect(url_for('feed'))

#creates flask app
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
