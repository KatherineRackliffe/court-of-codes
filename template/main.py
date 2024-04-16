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

# Get the User Shelf View
def get_user_shelf_view():
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT * FROM usershelfview WHERE userid=" + str(session["userid"])
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Gets the necessary data to display a user's list
def get_books_in_list(id):
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT b.isbn, b.booktitle, b.authorfname, b.authorlname FROM userlist JOIN bookinlist bil ON bil.listid = userlist.listid JOIN book b ON bil.isbn = b.isbn WHERE (userlist.listid='" + id + "' AND userlist.userid='" + str(session["userid"]) + "')"
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Gets the listid, listname, userid for a specific list
def get_list_info(user_id):
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT listid, listname FROM userlist WHERE userid = %s"
    cursor.execute(query, (user_id,))
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result


def get_book_details(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()

    # First, fetch the necessary details using the ISBN
    query_isbn = "SELECT isbn, booktitle, authorfname, authorlname, datepublished, pagecount FROM book WHERE isbn = %s"
    cursor.execute(query_isbn, (isbn,))
    book_details = cursor.fetchone()

    if book_details:
        # If book details are found, fetch additional details from the bookview
        query_additional = "SELECT averagereview FROM bookview WHERE isbn = %s"
        cursor.execute(query_additional, (isbn,))
        additional_details = cursor.fetchone()

        if additional_details:
            # Merge additional details into the book_details dictionary
            book_details += additional_details

    conn.close()
    return book_details


def get_searched_books(search_term):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT isbn, booktitle, authorfname, authorlname FROM book WHERE booktitle ILIKE %s OR authorfname ILIKE %s OR authorlname ILIKE %s OR isbn ILIKE %s"
    cursor.execute(query, ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
    result = cursor.fetchall()
    conn.close()
    return result

def retrieve_random_book_details(): #used for debugging, probably should delete
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT isbn, booktitle, authorfname, authorlname, datepublished, pagecount, averagereview, userid, username FROM bookview ORDER BY RANDOM() LIMIT 1"
    cursor.execute(query)
    random_book = cursor.fetchone()
    conn.close()
    return random_book

# Creates a new list with the new list name
def create_new_list(new_list_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    #FIXME add query w/ user and insert new list
    query = "INSERT INTO userlist (listname, userid) VALUES (%s, '" + str(session["userid"]) + "')"
    result = cursor.execute(query, (new_list_name,))
    conn.commit() #Saves the changes to the database
    conn.close()
    return query

# Deletes an old list by id
def delete_old_list(old_list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM userlist WHERE (listid = %s AND userid= '" + str(session["userid"]) + "')"
    result = cursor.execute(query, (old_list_id,))
    conn.commit() #Saves the changes to the database
    conn.close()
    return query


def add_review_to_database(isbn, rating):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if a review from the same user for the same book already exists
    query_check = "SELECT 1 FROM userreview WHERE userid = %s AND isbn = %s"
    cursor.execute(query_check, (session["userid"], isbn))
    existing_review = cursor.fetchone()

    if existing_review:
        # If a review already exists, update it instead of inserting a new one
        query_update = "UPDATE userreview SET numericalreview = %s WHERE userid = %s AND isbn = %s"
        cursor.execute(query_update, (rating, session["userid"], isbn))
    else:
        # If no existing review found, insert a new one
        query_insert = "INSERT INTO userreview (numericalreview, userid, isbn) VALUES (%s, %s, %s)"
        cursor.execute(query_insert, (rating, session["userid"], isbn))

    conn.commit()
    conn.close()


def add_tag_to_database(tagname, isbn):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Retrieve userid from the session
        userid = session.get("userid")
        if not userid:
            print("User ID not found in session.")
            return

        # Check if the tag already exists for the book
        query_check = "SELECT 1 FROM usertag WHERE isbn = %s AND userid = %s AND tagname = %s"
        cursor.execute(query_check, (isbn, userid, tagname))
        existing_tag = cursor.fetchone()

        if existing_tag:
            # If the tag already exists, update it
            query_update = "UPDATE usertag SET updated_at = CURRENT_TIMESTAMP WHERE isbn = %s AND userid = %s AND tagname = %s"
            cursor.execute(query_update, (isbn, userid, tagname))
            print("Tag already exists. Updated timestamp.")
        else:
            # If the tag doesn't exist, insert it
            query_insert = "INSERT INTO usertag (tagname, userid, isbn) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (tagname, userid, isbn))
            print("New tag added successfully.")

        conn.commit()
    except Exception as e:
        # Handle any errors that occur during the insertion
        print("Error inserting tag:", e)
        conn.rollback()  # Rollback changes if an error occurs
    finally:
        conn.close()



# Add book to list in the database
def add_book_to_list(isbn, list_id):
    if list_id is None or list_id == "":
        # Handle the case where list_id is not provided or is empty
        print("Error: list_id is not provided or is empty")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO bookinlist (isbn, listid) VALUES (%s, %s)"
    cursor.execute(query, (isbn, list_id))
    conn.commit()
    conn.close()

    
def get_tags_for_book(isbn):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT tagname FROM usertag WHERE isbn = %s"
        cursor.execute(query, (isbn,))
        tags = [tag[0] for tag in cursor.fetchall()]
        print("Tags for book with ISBN", isbn, ":", tags)  # Debug print statement
        conn.close()
        return tags
    except Exception as e:
        print("Error fetching tags for book:", e)
        return []

# ------------------------ END FUNCTIONS ------------------------ #


# ------------------------ BEGIN ROUTES ------------------------ #
# Get request for listView 
@app.route("/shelf/list/<id>", methods=['GET'])
# FIXME only allow to work for logged in user w/ try catch
def retrieve_list(id):
    list = get_books_in_list(id)
    list_info = get_list_info(id)
    url=request.base_url
    # Just grab the domain, not anything including a slash or afterwards (for local only, won't work on server b/c htts:// #FIXME)
    url = url.split("/")[0]
    return render_template("listview.html", list=list, list_info=list_info, url=url) # Return the page to be rendered

# Get request for userShelf
@app.route("/shelf", methods=["GET"])
def retrieve_shelf():
    lists = get_user_shelf_view() # Call defined function to get all items
    return render_template("usershelf.html", url=request.base_url, lists=lists) # Return the page to be rendered
 
# Shelf POST REQUEST
@app.route("/shelf", methods=["POST"])
def createlist():
    try:
        # Get items from the form
        data = request.form
        new_list_name = data["newlistname"] # This is defined in the input element of the HTML form on index.html

        # FIXME go to function and fix
        result = create_new_list(new_list_name)
        print(result)
        
        # Send message to page. There is code in index.html that checks for these messages
        flash("List created successfully", "success")
        # Redirect to current page.
        return redirect(request.base_url)
    # If an error occurs, this code block will be called
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error") # Send the error message to the web page
        return redirect(request.base_url)
    
# Delete request for a user's list
@app.route("/delete", methods=["POST"])
def deletelist():
    try:
        # Get old list name from the form
        data = request.form
        oldlistid = data["oldlistname"] # This is defined in the input element of the HTML form

        # Call the function that deletes the list using SQL
        query = delete_old_list(oldlistid) 
    
        print(query)
        # Redirect to shelf view.
        return redirect(url_for("retrieve_shelf"))
    # If an error occurs, this code block will be called
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error") # Send the error message to the web page
        return redirect(url_for("retrieve_shelf"))
      
    
@app.route("/bookview/<isbn>", methods=["GET", "POST"])
def retrieve_book(isbn):
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_review":
            try:
                rating = int(request.form.get("rating"))

                # Check if the rating is within the valid range (1 to 10)
                if rating < 1 or rating > 10:
                    flash("Rating must be between 1 and 10", "error")
                else:
                    add_review_to_database(isbn, rating)
                    flash("Review added successfully", "success")
            except ValueError:
                flash("Invalid rating format", "error")

        elif action == "add_tag":
            tag = request.form.get("tag")
            add_tag_to_database(tag, isbn)

        elif action == "add_to_list":
            list_id = request.form.get("list_id")
            add_book_to_list(isbn, list_id)

        return redirect(url_for("retrieve_book", isbn=isbn))

    book_details = get_book_details(isbn)
    tags = get_tags_for_book(isbn)
    user_lists = get_list_info(session.get("userid"))  # Fetch user's lists using user id

    # Check if user_lists is None, and if so, provide an empty list instead
    if user_lists is None:
        user_lists = []

    return render_template("bookview.html", book_details=book_details, tags=tags, user_lists=user_lists)


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
@app.route("/search", methods=['GET', 'POST'])
def retrive_search():
    if request.method == "GET":
        return render_template('search.html')
    #once they search
    elif request.method == "POST":
        search_term = request.form['search_term']
        results = get_searched_books(search_term)
        return render_template('results.html', results=results)

@app.route("/", methods=["GET"])
def home():
    recommended_books = get_random_books()
    return render_template("home.html", recommended_books=recommended_books) # Return the page to be rendered

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