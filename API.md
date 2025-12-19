API.md

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

