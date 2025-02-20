<?php
// Database connection settings
$servername = "localhost:3306";
$username = "root";
$password = "Poppysuki7!";
$dbname = "bookngs";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Retrieve form data
$firstName = $_POST['firstName'];
$surname = $_POST['surname'];
$email = $_POST['email'];
$phone = $_POST['phone'];
$arrivalInfo = $_POST['arrivalInfo'];
$dateOfResStart = $_POST['dateOfResStart'];
$dateOfResEnd = $_POST['dateOfResEnd'];
$noOfPeople = $_POST['noOfPeople'];
$bookingSite = $_POST['bookingSite'];
$totalAmount = $_POST['totalAmount'];
$paid = $_POST['paid'];
$comments = $_POST['comments'];

// Prepare and bind
$stmt = $conn->prepare("INSERT INTO Customer (FirstName, Surname, Email, Phone, ArrivalInfo) VALUES (?, ?, ?, ?, ?)");
$stmt->bind_param("sssss", $firstName, $surname, $email, $phone, $arrivalInfo);
$stmt->execute();

// Get the last inserted Customer ID
$custId = $stmt->insert_id;

// Insert into Reservation table
$stmt = $conn->prepare("INSERT INTO Reservation (DateOfRes_Start, DateOfRes_End, No_Of_People, Booking_Site, Total_Amount, Paid_Y_N, Comments, CustID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
$stmt->bind_param("ssissssi", $dateOfResStart, $dateOfResEnd, $noOfPeople, $bookingSite, $totalAmount, $paid, $comments, $custId);
$stmt->execute();

// Close statements and connection
$stmt->close();
$conn->close();

// Redirect or display success message
echo "Reservation successfully submitted!";
?>
