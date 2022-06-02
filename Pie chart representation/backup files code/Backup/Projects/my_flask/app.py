from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
# Intialize the database
db = SQLAlchemy(app) 

#Create DB Model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id


subscribers = []

@app.route('/delete/<int:id>')
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')
    except:
        return "There was a problem deleting that friend"


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    friend_to_update = Friends.query.get_or_404(id)
    if request.method == "POST":
        friend_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was a problem updating that friend"
    else:
        return render_template('update.html', friend_to_update=friend_to_update)

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    title = "My friends list"

    if request.method == "POST":
        friend_name = request.form['name']
        new_friend = Friends(name=friend_name)

        # Push to Database
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')    
        except:
            return "There was an error adding your friend.."
    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template("friends.html", title=title, friends=friends)

@app.route('/')
def index():
    title = "Gaurav's Blog"
    return render_template("index.html", title=title )

@app.route('/about')
def about():
    title = "About Gaurav Ardak.!"
    name = ['Gaurav', 'Chandrakant', 'Ardak']
    return render_template("about.html", name=name, title=title)
 
@app.route('/subscribe')
def subscribe():
    title = "Gaurav's to my channel"
    return render_template("subscribe.html", title=title )

@app.route('/form', methods=["POST"])
def form():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name") 
    email = request.form.get("email")

    if not first_name or not last_name or not email:
        error_statement = "All the Feilds are required"
        return render_template("subscribe.html", 
        error_statement=error_statement, 
        first_name=first_name, 
        last_name=last_name, 
        email=email)

    subscribers.append(f" {first_name} {last_name} | {email} ")
    title = "Thank You!"
    return render_template("form.html", subscribers=subscribers)