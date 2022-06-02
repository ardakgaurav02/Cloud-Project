from logging import FileHandler
from tarfile import FIFOTYPE
from app import app
from flask import render_template, request, redirect, jsonify, make_response
from flask import send_file, send_from_directory, safe_join, abort


import os

from werkzeug.utils import secure_filename

@app.route("/")
def index():
    return render_template("public/index.html")

@app.route("/jinja")
def jinja():

    my_name = "Gaurav"
    age  = 30
    lang = ["python", "java"]

    friends = {
    "Tony": 43,
    "Cody": 28,
    "Amy": 26,
    "Clarissa": 23,
    "Wendell": 39
    }
    colors = ("Red", "Blue")

    cool = True

    class GitRemote:
        def __init__(self, name, description, url):
            self.name = name
            self.description = description 
            self.url = url

        def pull(self):
            return f"Pulling into {self.name}"

        def clone(self):
            return f"Cloning into {self.url}"
    
    my_remote = GitRemote(
        name="Flask jinja",
        description="Template desing tutorial",
        url="https://github.com/Julian-Nash/jinja.git"
    )

    def repeat(x, qty=1):
        return x * qty
   

    return render_template("public/jinja.html", my_name=my_name, age=age, 
        lang=lang, friends=friends, colors=colors, cool=cool, GitRemote=GitRemote, 
        repeat=repeat, my_remote=my_remote) 

@app.route("/about")
def about():
    return "<h1 style='color: red'>About.!!!</h1>"

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():

    if request.method == "POST":

        req = request.form
        username = req.get("username")
        email = req.get("email")
        password = request.form["password"]

        print(username, password, email)
        # You could also use 
        #password = request.form.get("password")

        return redirect(request.url)

    return render_template("public/sign_up.html")

users = {
    "mitsuhiko": {
        "name": "Armin Ronacher",
        "bio": "Creatof of the Flask framework",
        "twitter_handle": "@mitsuhiko"
    },
    "gvanrossum": {
        "name": "Guido Van Rossum",
        "bio": "Creator of the Python programming language",
        "twitter_handle": "@gvanrossum"
    },
    "elonmusk": {
        "name": "Elon Musk",
        "bio": "technology entrepreneur, investor, and engineer",
        "twitter_handle": "@elonmusk"
    }
}

@app.route("/profile/<username>")
def profile(username):

    user = None

    if username in users:
        user = users[username]

    return render_template("public/profile.html", username=username, user=user)

@app.route("/multiple/<foo>/<bar>/<baz>")
def multiple(foo, bar, baz):

    print(f"foo is {foo}")
    print(f"bar is {bar}")
    print(f"baz is {baz}")


    return f"foo is {foo}, bar is {bar}, baz is {baz}"

@app.route("/json", methods=["POST"])
def json():

    if request.is_json:

        req = request.get_json()

        response = {
            "message": "JSON received!",
            "name": req.get("name")
        }

        res = make_response(jsonify(response), 200)

        return res

    else:

        return make_response(jsonify({"message": "NO JSON received"}), 400)

@app.route("/query")
def query():
    return "No query string received", 200

app.config["IMAGE_UPLOADS"] = "app/static/images/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/upload_image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":
        
        if request.files:

            image = request.files["image"]

            if image.filename == "":
                print("No filename")
                return redirect(request.url)

            if not allowed_image(image.filename):
                print("Image extention is not allowed")
                return redirect(request.url)

            else:
                filename = secure_filename(image.filename)

                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

            print("image saved")

            print(image)

            return redirect(request.url)

    return render_template("public/upload_image.html")


app.config["CLIENT_IMAGES"] = "static\client\img"
app.config["CLIENT_CSV"] = "static\client\csv"

@app.route("/get-image/<filename>")
def get_image(filename):
    
    try:
        return send_from_directory(app.config["CLIENT_IMAGES"], path=filename , as_attachment=False)
    except FileNotFoundError:
         abort(404)

@app.route("/get-csv/<filename>")
def get_csv(filename):
    
    try:
        return send_from_directory(app.config["CLIENT_CSV"], path=filename , as_attachment=False)
    except FileNotFoundError:
         abort(404)