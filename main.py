from flask import Flask
from flask import Flask,abort, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from helper import login_required
import sqlite3
  
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)    

# connect withe the myTable database
connection = sqlite3.connect("database.db", check_same_thread=False)

# cursor object
db = connection.cursor()
  
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route("/")
@login_required
def index():
    db.execute("SELECT * FROM alumni")

    data=db.fetchall()
    return render_template("index.html", data=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        password=request.form.get("password")
        username=request.form.get("username")
        
        # Ensure username was submitted
        if not username:
            return abort(400)

        # Ensure password was submitted
        elif not password:
            return abort(400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          (username,))
        
        rows=db.fetchall()
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not rows[0][2]==password:
            return abort(400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        flash("Sign In Successfull!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("./login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
  
# main driver function
if __name__ == '__main__':
  
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()