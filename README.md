# court-of-codes
# BESTREADS

**IT&C 350 DATABASE DESIGN PROJECT**  
**WINTER 2024**  
**Megan Johnson**  
**Taylor Parent**  
**Katherine Rackliffe**

---

## PROJECT OVERVIEW

### PROJECT OBJECTIVE STATEMENT

Create a site containing a database of fantasy novels where users can view, tag, sort, and search books, as well as save them to a personal list.

### PROJECT STAKEHOLDERS

The stakeholders are our users and our team. Our users (including our team) are fantasy readers who want to find new, interesting reads that fit their preferences.

The stakeholders are looking for the following in our app. Stakeholders want to be able to access standard book information, including the title, the book number in the series, the authors’ name, the published date, the page count, the book description, and the book cover art. The features the stakeholders want included are the ability to search by book tags, add tags to books, rate books, add books to their custom lists, and create and maintain an account. Since there are similar sites to rate and discover books, the stakeholders want to ensure BestReads is different enough to justify the app creation. Thus, the focus of BestReads is the user-populated tagging system. Overall BestReads will combine features of Goodreads and AO3 to create a unique user experience.

### APP REQUIREMENTS

#### FUNCTIONAL REQUIREMENTS

- Users can modify the following attributes of their account: name, username, password, and email.
- Users can do the following: view all books including their attributes and tags, sort books by tags, tag books, create private lists, add books to their private lists, and rate books.

#### NON-FUNCTIONAL REQUIREMENTS

**Security**
- Individuals will only be able to access their own book list after logging in. Additionally, individuals will only be able to edit the tags and ratings they create.
- Users will be required to change a password yearly. Password requirements will be 8+ characters, a capital letter, a special character, and a number.
- Any user input will be parsed to prevent cross-site scripting and SQL injection.

**Portability**
- Site will be available on mobile and laptop so they will be able to view their lists from anywhere they can access Wi-Fi.

**Maintainability**
- Regular maintenance will occur on the site to ensure everything is working properly and to add new book releases.

**Reliability**
- The site will be taken down for once per month maintenance periods, to ensure the site is in good repair.

**Performance**
- The site will load within 20 seconds and pull information from the database without significant delays.
- Information inserted by the users such as tags and ratings will be uploaded every 5 minutes to the database.

**Availability**
- The system should be available for users except during scheduled maintenance times, for a total of 95% uptime.
- The site will support 300 users at a time.

**Usability**
- Interface should be easy for users to understand and figure out.
- The site will be accessible for screen readers, and colorblind individuals.

**Scalability**
- More books and users should be able to be added to the system as needed. We plan for 100% increase in our databases at this time.

## DATABASE REQUIREMENTS

### ER DIAGRAM IMAGES

### SCHEMA DIAGRAM

### BUSINESS RULES

While users will be able to interact and add input to our databases, we strive to ensure that our data remains confidential, accurate, and a clear representation of our clients. In order to maintain the validity and privacy of the data we may collect, we have imposed the following business rules.

## DATABASE DOCUMENTATION

Link to database: [court-of-codes](https://github.com/KatherineRackliffe/court-of-codes.git)

The software used in our project as of March 2, 2024, is github and Postgres.

### Data to collect

#### Shown to user

Core data fields (C) or Derived fields (D)

- Book
  - Immutable attributes
    - ISBN (C)
    - BookTitle (C)
    - BookCover (C)
    - AuthorFName (C)
    - AuthorLName (C)
    - DatePublished (C)
    - PageCount (C)
  - Mutable attributes
    - AverageReview (D)
- User
  - UserID (C)
  - Username (C)
  - EmailAddress (C)
  - PasswordHash (D)
- ...

#### Not shown to user

- Password hashes (C)
  - Part of User

---

## Data Needed for Application Pages

### Welcome page

#### All Users

- UserID
- Username
- EmailAddress
- PasswordHash

### Home page

#### All Books

- ISBN
- BookTitle
- BookCover
- AuthorFName
- AuthorLName
- AverageReview
- List of all userTag
  - ISBN
  - TagName
  - UserID

...

---

## API DOCUMENTATION

---

## FRONT-END DOCUMENTATION

---

## APPENDIX 1: LOW-FIDELITY PAPER PROTOTYPES

---

## APPENDIX 2: HIGH-FIDELITY PAPER PROTOTYPES

