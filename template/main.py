import os
from flask import Flask, session, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import psycopg2
import hashlib


# Decorator used to exempt route from requiring login
def login_exempt(f):
    f.login_exempt = True
    return f

# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")


# Enforce user authentication on each request
@app.before_request
def default_login_required():
    # exclude 404 errors and static routes
    # uses split to handle blueprint static routes as well
    if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
        return

    view = app.view_functions[request.endpoint]

    if getattr(view, 'login_exempt', False):
        return

    if 'userid' not in session:
        return redirect(url_for('login'))
    


# ------------------------ BEGIN FUNCTIONS ------------------------ #
# Function to retrieve DB connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    return conn

# Get all items from the "items" table of the db (Jordan's example code)
# def get_all_items():
#     # Create a new database connection for each request
#     conn = get_db_connection()  # Create a new database connection
#     cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
#     # Query the db
#     query = "SELECT name, quantity FROM items"
#     cursor.execute(query)
#     # Get result and close
#     result = cursor.fetchall() # Gets result from query
#     conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
#     return result

def get_random_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT booktitle, authorfname, authorlname, isbn FROM book ORDER BY RANDOM() LIMIT 3"
    cursor.execute(query)
    recommended_books = cursor.fetchall()
    conn.close()
    return recommended_books

def get_user_info():
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT username, userid FROM welcomepageview"
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Get the User shelf View FIXME for only logged in user
def get_user_shelf_view():
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT * FROM usershelfview"
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Get the list view 
def get_list(id):
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT * from userlistview WHERE listid=" + id
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

def get_book_details(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM bookview WHERE isbn = %s"
    cursor.execute(query, (isbn,))
    book_details = cursor.fetchone()
    conn.close()
    return book_details

def get_searched_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM bookview WHERE title ILIKE %s OR authorfname ILIKE %s OR authorlname ILIKE %s OR pagecount ILIKE %s OR averagereview ILIKE %s"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def retrieve_random_book_details(): 
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT isbn, booktitle, authorfname, authorlname, datepublished, pagecount, averagereview, userid, username FROM bookview ORDER BY RANDOM() LIMIT 1"
    cursor.execute(query)
    random_book = cursor.fetchone()
    conn.close()
    return random_book

#Function to create a new list
def create_new_list(new_list_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    #FIXME add query w/ user and insert new list
    query = ""
    cursor.execute(query)
    conn.close()
    return

# ------------------------ END FUNCTIONS ------------------------ #


# ------------------------ BEGIN ROUTES ------------------------ #

# Get request for listView 
@app.route("/shelf/list/<id>", methods=['GET'])
# FIXME only allow to work for logged in user w/ try catch
def retrieve_list(id):
    list = get_list(id)
    url=request.base_url
    # Just grab the domain, not anything including a slash or afterwards (for local only, won't work on server b/c htts:// #FIXME)
    url = url.split("/")[0]
    return render_template("listview.html", list=list, url=url) # Return the page to be rendered

# Get request for userShelf
@app.route("/shelf", methods=["GET"])
# FIXME make work for logged in user, using session id linked to user w/ try catch
def retrieve_shelf():
    lists = get_user_shelf_view() # Call defined function to get all items
    return render_template("usershelf.html", url=request.base_url, lists=lists) # Return the page to be rendered
 
# Shelf POST REQUEST #FIXME
@app.route("/shelf", methods=["POST"])
def createlist():
    try:
        # Get items from the form
        data = request.form
        new_list_name = data["newlistname"] # This is defined in the input element of the HTML form on index.html

        # FIXME go to function and fix
        create_new_list(new_list_name)
        
        # Send message to page. There is code in index.html that checks for these messages
        flash("Item added successfully", "success")
        # Redirect to home. This works because the home route is named home in this file

    # If an error occurs, this code block will be called
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error") # Send the error message to the web page
        return redirect(url_for("home")) # Redirect to home

# # Get request for bookView
@app.route("/bookview/<isbn>", methods=["GET"])
def retrieve_book(isbn):
    book_details = get_book_details(isbn)
    url=request.base_url
    # Just grab the domain, not anything including a slash or afterwards (for local only, won't work on server b/c htts:// #FIXME)
    url = url.split("/")[0]
    return render_template("bookview.html", book_details=book_details, url=url)

@app.route("/book", methods=["GET"])
def retrieve_random_book(): 
    random_book = retrieve_random_book_details()
    return render_template("bookview.html", book_details=random_book)

# Get request for home
@app.route("/home", methods=["GET"])
def retrieve_home():
    recommended_books = get_random_books()
    return render_template("home.html", recommended_books=recommended_books)

# Get request for search
@app.route("/search", methods=["GET"])
def retrieve_search():
    lists = get_searched_books() # Call defined function to get all items FIXME
    return render_template("search.html", url=request.base_url, lists=lists) # Return the page to be rendered

# Get request for userShelf
@app.route("/welcome", methods=["GET"])
def retrieve_welcome():
    lists = get_user_shelf_view() # Call defined function to get all items FIXME
    return render_template("welcome.html", url=request.base_url, lists=lists) # Return the page to be rendered


# EXAMPLE OF GET REQUEST
@app.route("/", methods=["GET"])
def home():
    recommended_books = get_random_books()
    return render_template("home.html", recommended_books=recommended_books) # Return the page to be rendered

# EXAMPLE OF POST REQUEST
@app.route("/new-item", methods=["POST"])
def add_item():
    try:
        # Get items from the form
        data = request.form
        item_name = data["name"] # This is defined in the input element of the HTML form on index.html
        item_quantity = data["quantity"] # This is defined in the input element of the HTML form on index.html

        # TODO: Insert this data into the database
        
        # Send message to page. There is code in index.html that checks for these messages
        flash("Item added successfully", "success")
        # Redirect to home. This works because the home route is named home in this file
        return redirect(url_for("home"))

    # If an error occurs, this code block will be called
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error") # Send the error message to the web page
        return redirect(url_for("home")) # Redirect to home

# Log users in
@app.route('/login', methods=['GET', 'POST'])
@login_exempt
def login():
    # If user is signed in, redirect them to home
    if 'userid' in session:
        return redirect(url_for('home'))
    # Render page for GET
    if request.method == "GET":
        return render_template('login.html')
    # Handle login logic
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Execute the SQL query to fetch the hashed password associated with the username
            query = "SELECT passwordhash, salt, userid, emailaddress FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            # If no result found for the given username, return False
            if not result:
                flash(f"Username or password is invalid", 'error')
                return render_template("login.html")
            
            # Extract the salt and hashed password from the result
            hashed_password_in_db, salt, userid, email = result[:4]

            # Verify the password
            if not verify_password(password, salt, hashed_password_in_db):
                flash("Username or password is invalid", 'error')
                return render_template("login.html")
            
            # Set user as logged in
            session["username"] = username
            session["userid"] = userid
            session["email"] = email

            # Render home page
            return redirect(url_for('home'))

        # Handle errors
        except Exception as err:
            flash(f"Unknown error occured during login.", 'error')
            return render_template("login.html")
        finally:
            conn.close()

# Helper function to help verify password hash
def verify_password(password, salt, hashed_password_in_db):
    # Hash the provided password with the salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
    # Compare the hashed passwords
    return hashed_password.hex() == hashed_password_in_db

# Log users out
@app.route('/logout')
@login_exempt
def logout():
    # Remove session variables
    session.pop('email', None)
    session.pop('username', None)
    session.pop('userid', None)
    return redirect(url_for('login'))

# Handle user registration
@app.route('/register', methods=['GET', 'POST'])
@login_exempt
def register():
    # If user is signed in, send them to the index page
    if 'userid' in session:
        return redirect(url_for('home'))
    # If user is trying to view the page, render the page
    if request.method == "GET":
        return render_template('register.html')
    # Handle logic for user registration
    elif request.method == "POST":
        # Get form values
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']

        # Confirm that passwords match
        if password != confirm_password:
            flash("Password and confirm password do not match", 'error')
            return render_template("register.html")

        # Hash the password
        salt, hashed_password = hash_password(password)
        
        # Insert
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (emailaddress, username, passwordhash, salt) VALUES (%s, %s, %s, %s) RETURNING userid;", (email, username, hashed_password, salt))
            conn.commit()
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result == None:
                flash(f"Failed to insert user into database.", 'error')
                print("Failed to create new user in database.")
                return render_template("register.html")
            session["userid"] = result[0]
            session["username"] = username
            session["email"] = email

            # All done, send user home
            return redirect(url_for('home'))
        except Exception as err:
            flash(f"Registration failed: unknown error occured.", 'error')
            return render_template("register.html")
        finally:
            conn.close()

# Helper function to hash passwords
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a random 16-byte salt
    else:
        salt = bytes.fromhex(salt)  # Convert hex string salt back to bytes
    
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex(), hashed_password.hex()
# ------------------------ END ROUTES ------------------------ #


# listen on port 8080
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
