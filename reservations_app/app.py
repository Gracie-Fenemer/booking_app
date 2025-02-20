from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from db_connect import connect
from datetime import datetime, timedelta

app = Flask(__name__)

# Homepage Route
@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/customers')
def customers():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch customer data
    try:
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching customer data: {err}")
        customers = []
    finally:
        cursor.close()
        conn.close()

    # Check for a message from the URL
    message = request.args.get('message')
    return render_template('customers.html', customers=customers, message=message)

@app.route('/reservations')
def reservations():
    conn = connect()
    sort = request.args.get('sort', 'future')  # Default to future bookings
    today = datetime.today().date()

    # Set up the SQL query for sorting reservations
    if sort == 'past':
        query_reservations = """
            SELECT r.*, c.FirstName, c.Surname
            FROM Reservation r
            JOIN Customer c ON r.CustID = c.CustID
            WHERE r.DateOfRes_End < %s
            ORDER BY r.DateOfRes_Start DESC
        """
        params = (today,)
    else:
        query_reservations = """
            SELECT r.*, c.FirstName, c.Surname
            FROM Reservation r
            JOIN Customer c ON r.CustID = c.CustID
            WHERE r.DateOfRes_Start >= %s
            ORDER BY r.DateOfRes_Start ASC
        """
        params = (today,)

    # Fetch reservations
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query_reservations, params)
        reservations = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching reservation data: {err}")
        reservations = []
    finally:
        cursor.close()
        conn.close()

    # Check for a message from the URL
    message = request.args.get('message')
    return render_template('reservations.html', reservations=reservations, message=message)

@app.route('/form')
def form():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    # Fetch customer data
    try:
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching customer data: {err}")
        customers = []
    finally:
        cursor.close()
        conn.close()

    # Check for a message from the URL
    message = request.args.get('message')
    return render_template('form.html', customers=customers, message=message)

# Rest of your app logic stays the same

if __name__ == '__main__':
    app.run(debug=True)

