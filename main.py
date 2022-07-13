from flask import Flask
from flask import Flask,abort, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from helper import login_required
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from flask_paginate import Pagination, get_page_args

  
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
connection.row_factory = sqlite3.Row
db = connection.cursor()



# Function to get Paginated data
def get_data(data, offset=0, per_page=10):
    return data[min(offset, len(data)):min(offset+per_page, len(data))]

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    page, per_page, offset = get_page_args(page_parameter='page',                                       per_page_parameter='per_page')

    if request.method=="POST":
        search= request.form.get("search")
        print(search)

        data=[]
        if search:
            al_tables=["alumni_me", "alumni_cs", "alumni_ee", "alumni_ch", "alumni_mt", "alumni_ce"]
            
            for al_table in al_tables:
                db.execute("SELECT * FROM " + al_table + " WHERE name LIKE ?", ("%"+search+"%",) )
                alumni=db.fetchall()

                for people in alumni:
                    data.append(people)

                db.execute("SELECT * FROM " + al_table + " WHERE email LIKE ?", ("%"+search+"%",) )
                alumni=db.fetchall()
                for people in alumni:  
                    data.append(people) 

                db.execute("SELECT * FROM " + al_table + " WHERE status LIKE ?", ("%"+search+"%",))
                alumni=db.fetchall()
                for people in alumni:
                    data.append(people)

                db.execute("SELECT * FROM " + al_table + " WHERE alumni_id LIKE ? ", ("%"+search+"%",) )
                alumni=db.fetchall()
                for people in alumni:
                    data.append(people)

                db.execute("SELECT * FROM " + al_table + " WHERE entry_no LIKE ? ", ("%"+search+"%",) )
                alumni=db.fetchall()
                for people in alumni:
                    data.append(people)  

            data=list(set(data))                 

            total=len(data)
            paginated_data = get_data(data=data, offset=offset, per_page=per_page)
            pagination = Pagination(page=page,per_page=per_page, total=total)

            return render_template("/index.html", data=paginated_data, page=page, per_page=10, pagination=pagination)

        degree=request.form.get("degree")
        year=request.form.get("year")
        dept=request.form.get("department")

        if dept!="null" and dept:
            al_table="alumni_"+str(dept)

            db.execute("SELECT * FROM " + al_table)
            alumni=db.fetchall()
            result=[]

            for people in alumni:
                data.append(people)

            if year!="null" and year:
                for person in data:
                    if person["year"]==int(year):
                        result.append(person)
            else:
                result=data            

            if degree!="null" and degree:
                result_final=[]
                for person in result:
                    if person["program"]==degree:
                        result_final.append(person)

                result=result_final
                                        

            data=result
            total=len(data)
            paginated_data = get_data(data=data, offset=offset, per_page=per_page)
            pagination = Pagination(page=page,per_page=per_page, total=total)

            return render_template("/index.html", data=paginated_data, page=page, per_page=10, pagination=pagination)

        al_tables=["alumni_me", "alumni_cs", "alumni_ee", "alumni_ch", "alumni_mt", "alumni_ce"]
            
        for al_table in al_tables:
            db.execute("SELECT * FROM " + al_table)
            alumni=db.fetchall()

            for people in alumni:
                data.append(people)

        if year and year!="null":
            result=[]
            for person in data:
                if person["year"]==int(year):
                    result.append(person)

            if degree!="null" and degree:
                for person in data:
                    if person["program"]==degree:
                        result.append(person)

            data=result
            total=len(data)
            paginated_data = get_data(data=data, offset=offset, per_page=per_page)
            pagination = Pagination(page=page,per_page=per_page, total=total)

            return render_template("/index.html", data=paginated_data, page=page, per_page=10, pagination=pagination)

        if degree!="null" and degree:
            result=[]
            for person in data:
                if person["program"]==degree:
                    result.append(person)

            data=result
            total=len(data)
            paginated_data = get_data(data=data, offset=offset, per_page=per_page)
            pagination = Pagination(page=page,per_page=per_page, total=total)

            return render_template("/index.html", data=paginated_data, page=page, per_page=10, pagination=pagination)    




    data=[]
    al_tables=["alumni_me", "alumni_cs", "alumni_ee", "alumni_ch", "alumni_mt", "alumni_ce"]
            
    for al_table in al_tables:
        db.execute("SELECT * FROM " + al_table)
        alumni=db.fetchall()

        for people in alumni:
            data.append(people)
    
    total=len(data)
    paginated_data = get_data(data=data, offset=offset, per_page=per_page)
    pagination = Pagination(page=page,per_page=per_page, total=total)

    return render_template("/index.html", data=paginated_data, page=page, per_page=10, pagination=pagination)

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
        if len(rows) != 1 or not check_password_hash(rows[0][2],password):
            return abort(400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        flash("Sign In Successfull!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


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
    app.run(debug=False, host="0.0.0.0")