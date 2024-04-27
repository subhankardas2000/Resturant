# Sharma's Cafe

Sharma's Cafe is a web application for managing orders and inquiries for a fictional restaurant. Customers can view the menu, place orders, and contact the restaurant for inquiries. Admin users have additional functionalities like viewing orders and managing menu items.

## Features

- **Customer Interface:**
  - View menu items and prices
  - Place orders with options for online payment
  - Contact the restaurant for inquiries
  
- **Admin Interface:**
  - View and manage orders
  - Add, edit, and delete menu items
  - View customer inquiries

## Technologies Used

- Python
- Flask (Python web framework)
- SQLite (Database)
- HTML/CSS
- JavaScript

## Setup Instructions

1. Clone the repository: `git clone https://github.com/subhankardas2000/Resturant.git`
2. Navigate to the project directory: `cd Resturant`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Access the application in your web browser at `http://localhost:5000`

## Project Structure

- **app.py:** Main Flask application file containing routes and logic.
- **templates:** HTML templates for rendering pages.
- **static:** Static files such as CSS stylesheets and JavaScript files.
- **database.db:** SQLite database file containing tables for users, menu items, orders, and inquiries.
