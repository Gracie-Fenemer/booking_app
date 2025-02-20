<!-- view_data.php -->
<?php
// Database connection
$servername = "localhost";
$username = "your_username";
$password = "your_password";
$dbname = "your_database";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Query to retrieve data from Customer and Reservation tables
$sql = "SELECT Customer.FirstName, Customer.Surname, Customer.Email, Reservation.DateOfRes_Start, Reservation.DateOfRes_End, Reservation.No_Of_People, Reservation.Total_Amount, Reservation.Paid_Y_N 
        FROM Customer 
        JOIN Reservation ON Customer.CustID = Reservation.CustID";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    echo "<table border='1'><tr><th>First Name</th><th>Surname</th><th>Email</th><th>Start Date</th><th>End Date</th><th>People</th><th>Total Amount</th><th>Paid</th></tr>";
    while ($row = $result->fetch_assoc()) {
        echo "<tr><td>" . $row["FirstName"] . "</td><td>" . $row["Surname"] . "</td><td>" . $row["Email"] . "</td><td>" . $row["DateOfRes_Start"] . "</td><td>" . $row["DateOfRes_End"] . "</td><td>" . $row["No_Of_People"] . "</td><td>" . $row["Total_Amount"] . "</td><td>" . $row["Paid_Y_N"] . "</td></tr>";
    }
    echo "</table>";
} else {
    echo "No records found.";
}

// Close connection
$conn->close();
?>
