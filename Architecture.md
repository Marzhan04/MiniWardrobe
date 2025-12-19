Architecture.md

System Architecture

1. Architecture Style
The system follows a client-server architecture, where the front end communicates with the back end via HTTP requests.

2. System Components
- Front end: The user interface built with HTML, CSS, and JavaScript.
- Back end: Flask app that handles API requests, user authentication, and outfit generation logic.
- Database: SQLite for storing user data and wardrobe items.

3. Component Diagram

x-apple-ql-id2://9BCFA2F8-D2C8-48ED-88BA-8565042EA3C0/x-apple-ql-magic/5A46363C-147C-4370-AC9A-EE319C05EDB3.png
4. Data Flow
When a user uploads a clothing item, the front end sends a POST request to the back end, which stores the data in the database. When the user generates an outfit, the front end requests an outfit from the back end.

5. Database Schema
- Users: id, username, email, password_hash
- Wardrobe Items: id, user_id, item_name, category

6. Technology Decisions
- Flask: Lightweight framework for handling HTTP requests.
- SQLite: Simple database solution for small-scale projects.

4. API.md

# API Specification

## Base URL
http://localhost:5000

---

## Endpoint: /users/register
Method: POST

Request Body:
{
 "username": "john_doe",
 "email": "john@example.com",
 "password": "password123"
}

Response:
{
 "message": "User registered successfully"
}

Error Codes:
- 400: Invalid input
- 409: Email already exists

---

## Endpoint: /outfits/generate
Method: GET

Parameters:
- style: casual, formal, etc.
- color: red, blue, etc.

Response:
{
 "outfit": [
   "Red shirt",
   "Blue jeans",
   "Black shoes"
 ]
}

