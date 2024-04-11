import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import psycopg2


# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")


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

# ------------------------ END FUNCTIONS ------------------------ #


# ------------------------ BEGIN ROUTES ------------------------ #

# Get request for listView 
@app.route("/shelf/list/<id>", methods=['GET'])
# FIXME only allow to work for logged in user w/ try catch
def retrieve_list(id):
  list = get_list(id)
  return render_template("listview.html", list=list) # Return the page to be rendered

# Get request for userShelf
@app.route("/shelf", methods=["GET"])
# FIXME make work for logged in user, using session id linked to user w/ try catch
def retrieve_shelf():
    lists = get_user_shelf_view() # Call defined function to get all items
    return render_template("usershelf.html", url=request.base_url, lists=lists) # Return the page to be rendered

# # Get request for bookView
@app.route("/bookview/<isbn>", methods=["GET"])
def retrieve_book(isbn):
    book_details = get_book_details(isbn)
    return render_template("bookview.html", book_details=book_details)

# Get request for home
@app.route("/home", methods=["GET"])
def retrieve_home():
    recommended_books = get_random_books()
    return render_template("home.html", recommended_books=recommended_books)

# Get request for search
@app.route("/search", methods=["GET"])
def retrieve_search():
    lists = get_user_shelf_view() # Call defined function to get all items FIXME
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
        
# ------------------------ END ROUTES ------------------------ #


# listen on port 8080
if __name__ == "__main__":
    app.run(port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
