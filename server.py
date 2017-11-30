from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import time
import re
import md5

app = Flask(__name__)
app.secret_key = "TheSercretKey"
mysql = MySQLConnector(app,'TheWallsdb') #connect with TheWallsdb mysql

@app.route('/') 
def index(): #main page
    session["logIn"] = False #made "logIn" to use with session to tell when log in fails, render to index.html
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def create(): #/process route just takes input from the users 
    if request.form['action'] == 'loggedIn': # if statement - action string to connect with html
        email = request.form['email'] #if input email(id/name in html) = with email in user table
        password = request.form['password'] #if input password(id/name in html) = with password in user table
        hashed_password = md5.new(password).hexdigest() #md5 hashed password
        Datacheck = "SELECT * FROM users"  #accessing all the users data for users (for above password and email)
        for i in (mysql.query_db(Datacheck)): #for statement when checking database
            if i['email'] == email and i['password'] == hashed_password: 
                session['email'] = email 
                session['logIn'] = True 
                q1 = "SELECT first_name FROM users where email = '{}'".format(session['email']) 
                l1 = mysql.query_db(q1)
                session['name'] = l1[0]['first_name']  
                print session['name'] #print out the name of the user
                flash("Welcome {} {}!".format(i['first_name'], i['last_name'])) #welcoming message after you log in 
                return redirect('/message') #directs to message.html
        flash('incorrect email/password combo')
        return redirect('/')
    else: #else to register
        first = request.form['first_name'] #first name input from html
        last = request.form['last_name']#last name input from html
        email = request.form['email']#email name input from html
        password = request.form['password']#password name input from html
        hashed_password = md5.new(password).hexdigest()
        confirm = request.form['confirm'] #confirms the password
        

        data = { #data for input info
                'first_name': first,
                'last_name': last,
                'email': email,
                'password': hashed_password
                }
        #it query to insert the input info to database
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"

    FIRSTLAST_REGEX = re.compile(r'^(?=.*[0-9]).+$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    UPPERDIGIT_REGEX = re.compile(r'^(?=.*[0-9])(?=.*[A-Z]).+$')

    if len(first_name) < 1: #checks first name length is below 1
        flash("First Name cannot be empty!") #sends out flash message
        return redirect('/') 

    elif FIRSTLAST_REGEX.match(first_name): #checks variable set above which only takes letters
        flash("Invalid First Name") #sends out flash message
        return redirect('/')

    elif len(last_name) < 1: #checks if last name length is below 1
        flash("Last Name cannot be empty!") #sends out flash message
        return redirect('/')

    elif FIRSTLAST_REGEX.match(last_name): #checks variable set above which only takes letters
        flash("Invalid Last Name") #sends out flash message
        return redirect('/')

    elif len(email) < 1: #checks if the email length is below 1
        flash("Email cannot be empty!") #sends out flash message
        return redirect('/')

    elif not EMAIL_REGEX.match(email): #checks variable set above which only takes letters
        flash("Invalid Email") #sends out flash message
        return redirect('/')   

    elif len(password) < 1: #checks if password is below 1
        flash("Password cannot be empty!")#sends out flash message
        return redirect('/')

    elif len(password) < 8: #checks to make sure password length is at least 8 char
        flash("Password must be longer than 8 characters!")#sends out flash message
        return redirect('/')

    elif not UPPERDIGIT_REGEX.match(password): #checks variable set above which only takes letters
        flash("Password must contain at least one upper case letter and one digit")#sends out flash message
        return redirect('/')

    elif len(confirm_password) < 1: #checks if its empty
        flash("Please confirm password")#sends out flash message
        return redirect('/')

    elif password != confirm_password: #checks with password 
        flash("Password must match!")#sends out flash message
        return redirect('/')
    else:
        return redirect('/')


@app.route('/message')
def success(): 
    print session['email'] 
    if session['logIn'] == False: #if not logged in,
        flash("you must be signed in to see this content")#sends out flash message
        return redirect('/') #directs to main


    #query selects users info and JOIN with message with user ID
    query = "SELECT users.first_name, messages.message, messages.id FROM users JOIN messages ON users.id = messages.users_id ORDER BY messages.id DESC"
    messages = mysql.query_db(query) #checks with messages 
    #query selects users info and JOIN with comments with user ID
    query2 = "SELECT users.first_name, messages.id, comments.comment FROM comments JOIN messages ON messages.id = comments.messages_id JOIN users ON users.id = comments.users_id"
    comments = mysql.query_db(query2) #checks with comments
    return render_template("message.html", messages = messages, comments = comments) #updates with messages and comments

@app.route('/process2', methods=['POST'])
def update(): 
    q1 = "SELECT id FROM users where email = '{}'".format(session['email']) #selects user with email
    d1 = mysql.query_db(q1)
    current_id = d1[0]['id'] 
    
    if request.form['action'] == 'message': #if statement to take messege action from html
        message = request.form['message'] 
        data = {'message': message, 'id' : current_id} #sets route on message and user id
        query = "INSERT INTO messages (message, created_at, users_id) VALUES (:message, NOW(), :id)" #insert message info to message table 
        messages = mysql.query_db(query, data)

    else: #else statement for comments
        mID = request.form['action'] #comment action input from html
        print mID 
        comment = request.form['comment'] 
        data = {'comment': comment, 'id' : current_id, 'messages_id': mID} #set route on comment table and user id
        query = "INSERT INTO comments (comment, created_at, users_id, messages_id) VALUES (:comment, NOW(), :id, :messages_id)" #insert comments on users id 
        comments = mysql.query_db(query, data)
    return redirect('/message') #redirect to message page

    


app.run(debug=True)



        # properLogin = True
        # if len(first) < 3:
        #     flash("first name must be at least 2 letters long")
        #     properLogin = False

        # if len(last) < 3:
        #     flash("last name must be at least 2 letters long")
        #     properLogin = False

        # my_re = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        # check = "SELECT * FROM users"
        # for i in (mysql.query_db(check)):
        #     if i['email'] == email:
        #         flash("email already in database")
        #         properLogin = False
        # if not my_re.match(email):
        #     flash("please use a proper email")
        #     properLogin = False
        
        # if len(password) < 8:
        #     flash("password must be at least 8 characters long")
        #     properLogin = False
        # if password != confirm:
        #     flash("passwords must match")
        #     properLogin = False
        
        # if properLogin:
        #     mysql.query_db(query, data)
        #     flash("Welcome to this pointless website {} {}!".format(first, last))
        #     session['loggedOn'] = True
        #     session['email'] = email
        #     return redirect('/success')
        # else:
        #     return redirect('/')
