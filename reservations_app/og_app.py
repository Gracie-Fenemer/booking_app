from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from db_connect import connect
from datetime import datetime, timedelta


app = Flask(__name__)


# Homepage Route
@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/form')
def form():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    # Fetch customer data
    try:
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()
        print("Fetched customers:", customers)  # Log the fetched data for debugging
    except mysql.connector.Error as err:
        print(f"Error fetching data from Customer table: {err}")
        customers = []  # Set customers to an empty list if there's an error

    conn.close()

    # Check for a message (success or error) from the URL
    message = request.args.get('message')

    return render_template('form.html', customers=customers, message =message)

@app.route('/reservations')
def show_data():
    conn = connect()
    sort = request.args.get('sort', 'future')  # Default to future bookings
    today = datetime.today().date()

    # Fetch all customers (unaffected by sorting)
    customer_cursor = conn.cursor(dictionary=True)
    query_customers = "SELECT * FROM Customer"
    try:
        customer_cursor.execute(query_customers)
        customer = customer_cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching customer data: {err}")
        customer = []
    finally:
        customer_cursor.close()

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

    # Fetch sorted reservations
    reservation_cursor = conn.cursor(dictionary=True)
    try:
        reservation_cursor.execute(query_reservations, params)
        reservation = reservation_cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching reservation data: {err}")
        reservation = []
    finally:
        reservation_cursor.close()

    conn.close()

    # Render the template with both customer and reservation data
    return render_template('reservations.html', customer=customer, reservation=reservation, today=today)


def get_available_dates():
    """
    Fetch available date ranges for reservations.
    """
    conn = connect()  # Open a new connection just for this function
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT DateOfRes_Start, DateOfRes_End FROM Reservation")
        reserved_dates = cursor.fetchall()

        # Create a list of reserved date ranges
        reserved_ranges = [(r['DateOfRes_Start'], r['DateOfRes_End']) for r in reserved_dates]

        # Logic to find available date ranges (e.g., within the next 30 days)
        available_dates = []
        from datetime import datetime, timedelta
        today = datetime.today()
        end_date = today + timedelta(days=30)

        current_date = today
        while current_date <= end_date:
            is_available = True
            for start, end in reserved_ranges:
                if start <= current_date.date() <= end:
                    is_available = False
                    break
            if is_available:
                available_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return available_dates

    except mysql.connector.Error as err:
        print(f"Error fetching available dates: {err}")
        return []
    
    finally:
        cursor.close()
        conn.close()  # Close the connection after fetching the dates


@app.route('/submit', methods=['POST'])
def submit_form():
    # Get form data
    first_name = request.form.get('FirstName')  
    surname = request.form.get('Surname')       
    email = request.form.get('Email')            
    phone = request.form.get('Phone')            
    arrival_info = request.form.get('ArrivalInfo')  
    date_start = request.form.get('DateOfRes_Start')  
    date_end = request.form.get('DateOfRes_End')      
    no_of_people = request.form.get('No_Of_People')   
    no_adults = request.form.get('No_Adults')          
    no_children = request.form.get('No_Children')      
    booking_site = request.form.get('Booking_Site')    
    total_amount = request.form.get('Total_Amount')    
    paid_yn = request.form.get('Paid_Y_N')             
    date_paid = request.form.get('Date_Paid') or None
    comments = request.form.get('Comments')              

    # Connect to the database
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Step 1: Check if the selected dates overlap with existing reservations
        cursor.execute("""
            SELECT * FROM Reservation 
            WHERE (DateOfRes_Start <= %s AND DateOfRes_End >= %s)
        """, (date_end, date_start))
        conflicting_reservations = cursor.fetchall()

        if conflicting_reservations:
            # Dates are already taken, render the form template with the dropdown message
            return render_template('form.html', message="Selected dates are already booked! Please choose different dates.")

        # Step 2: Insert customer information into the Customer table
        customer_query = """
        INSERT INTO Customer (FirstName, Surname, Email, Phone, ArrivalInfo)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(customer_query, (first_name, surname, email, phone, arrival_info))

        # Get the last inserted customer ID
        cust_id = cursor.lastrowid

        # Step 3: Insert reservation information into the Reservation table
        reservation_query = """
        INSERT INTO Reservation (DateOfRes_Start, DateOfRes_End, No_Of_People, No_Adults, No_Children,
                                 Booking_Site, Total_Amount, Paid_Y_N, Date_Paid, Comments, CustID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(reservation_query, (date_start, date_end, no_of_people, no_adults, no_children,
                                           booking_site, total_amount, paid_yn, date_paid, comments, cust_id))

        # Commit the transaction
        conn.commit()

        # Render the form page with a success message
        return render_template('form.html', message="Reservation added successfully!")

    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        return f"Error: {err}"

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()



@app.route('/delete_reservation', methods=['POST'])
def delete_reservation():
    conn = connect()
    cust_id = request.form['CustID']  # Get the CustID from the form

    try:
        # Start a transaction
        conn.start_transaction()

        # Delete from Customer table
        delete_customer_query = """
            DELETE FROM Customer
            WHERE CustID = %s
        """
        conn.cursor().execute(delete_customer_query, (cust_id,))

        # Delete from Reservation table
        delete_reservation_query = """
            DELETE FROM Reservation
            WHERE CustID = %s
        """
        conn.cursor().execute(delete_reservation_query, (cust_id,))

       

        # Commit the transaction
        conn.commit()

        # Return success message or redirect
        return redirect(url_for('show_data', message='Reservation deleted successfully!'))  # Adjust as necessary
    except mysql.connector.Error as err:
        # If an error occurs, rollback the transaction
        conn.rollback()
        print(f"Error deleting reservation or customer: {err}")
        return "Error deleting reservation."

    finally:
        conn.close()

    # return redirect(url_for('form', message='Reservation deleted successfully!'))


@app.route('/edit_reservation/<int:reservation_id>', methods=['GET'])
def edit_reservation(reservation_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Retrieve reservation data
        cursor.execute("""
            SELECT * FROM Reservation
            WHERE CustID = %s
        """, (reservation_id,))
        reservation = cursor.fetchone()

        # Retrieve customer data
        cursor.execute("""
            SELECT * FROM Customer
            WHERE CustID = %s
        """, (reservation_id,))
        customer = cursor.fetchone()

        message = request.args.get('message', '')  # Retrieve the message if it exists
        return render_template('edit_res.html', customer=customer, reservation=reservation, message=message)

    except mysql.connector.Error as err:
        print(f"Error retrieving data: {err}")
        reservation = None
        customer = None
    finally:
        cursor.close()
        conn.close()

    if reservation and customer:
        # Pass both customer and reservation data to the template
        return render_template('edit_res.html', reservation=reservation, customer=customer)
    else:
        return "Reservation or customer not found", 404


@app.route('/update_reservation/<int:reservation_id>', methods=['POST'])
def update_reservation(reservation_id):
    # Get the updated data from the form
    first_name = request.form['FirstName']
    surname = request.form['Surname']
    email = request.form['Email']
    phone = request.form['Phone']
    arrival_info = request.form['ArrivalInfo']
    date_start = request.form['DateOfRes_Start']
    date_end = request.form['DateOfRes_End']
    no_of_people = request.form['No_Of_People']
    no_adults = request.form['No_Adults']
    no_children = request.form['No_Children']
    booking_site = request.form['Booking_Site']
    total_amount = request.form['Total_Amount']
    paid_yn = request.form['Paid_Y_N']
    date_paid = request.form['Date_Paid'] or None  # Allow empty value for Date_Paid
    comments = request.form['Comments']

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if the new dates conflict with other reservations, excluding this reservation
        cursor.execute("""
            SELECT * FROM Reservation 
            WHERE (DateOfRes_Start <= %s AND DateOfRes_End >= %s)
            AND CustID != %s
        """, (date_end, date_start, reservation_id))
        
        conflicting_reservations = cursor.fetchall()

        if conflicting_reservations:
            # Dates are already taken, show a message and return to the edit form
            message = "Selected dates are already booked! Please choose different dates."
            return redirect(url_for('edit_reservation', reservation_id=reservation_id, message=message))

        # Update the customer data
        cursor.execute("""
            UPDATE Customer 
            SET FirstName = %s, Surname = %s, Email = %s, Phone = %s, ArrivalInfo = %s
            WHERE CustID = %s
        """, (first_name, surname, email, phone, arrival_info, reservation_id))

        # Update the reservation data
        cursor.execute("""
            UPDATE Reservation
            SET DateOfRes_Start = %s, DateOfRes_End = %s, No_Of_People = %s, No_Adults = %s, No_Children = %s,
                Booking_Site = %s, Total_Amount = %s, Paid_Y_N = %s, Date_Paid = %s, Comments = %s
            WHERE CustID = %s
        """, (date_start, date_end, no_of_people, no_adults, no_children, booking_site, total_amount, paid_yn, date_paid, comments, reservation_id))

        conn.commit()  # Commit the transaction
        message = "Reservation updated successfully!"
        
    except mysql.connector.Error as err:
        message = f"Error: {err}"
    
    finally:
        cursor.close()
        conn.close()

    # Redirect to the main data page with a message
    return redirect(url_for('show_data', message=message))




if __name__ == '__main__':
    app.run(debug=True)

