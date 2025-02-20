<?php
// DB Connection
$servername = "localhost:3306";
$username = "root";
$password = "Poppysuki7!";
$dbname = "bookngs";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Capture form data
$firstName = $_POST['firstName'];
$surname = $_POST['surname'];
$email = $_POST['email'];
$phone = $_POST['phone'];
$arrivalInfo = $_POST['arrivalInfo'];
$dateStart = $_POST['dateStart'];
$dateEnd = $_POST['dateEnd'];
$noOfPeople = $_POST['noOfPeople'];
$noAdults = $_POST['noAdults'];
$noChildren = $_POST['noChildren'];
$bookingSite = $_POST['bookingSite'];
$totalAmount = $_POST['totalAmount'];
$paidYN = strtoupper($_POST['paidYN']);
$comments = $_POST['comments'];

// Insert into Customer table
$customerStmt = $conn->prepare("INSERT INTO Customer (FirstName, Surname, Email, Phone, ArrivalInfo) VALUES (?, ?, ?, ?, ?)");
$customerStmt->bind_param("sssss", $firstName, $surname, $email, $phone, $arrivalInfo);
$customerStmt->execute();
$custID = $conn->insert_id; // Get the last inserted customer ID

// Insert into Reservation table
$reservationStmt = $conn->prepare("INSERT INTO Reservation (DateOfRes_Start, DateOfRes_End, No_Of_People, No_Adults, No_Children, Booking_Site, Total_Amount, Paid_Y_N, Comments, CustID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
$reservationStmt->bind_param("ssiiiiissi", $dateStart, $dateEnd, $noOfPeople, $noAdults, $noChildren, $bookingSite, $totalAmount, $paidYN, $comments, $custID);
$reservationStmt->execute();

// Confirm success
if ($customerStmt && $reservationStmt) {
    echo "Reservation successfully created!";
} else {
    echo "Error: " . $conn->error;
}

// Close connections
$customerStmt->close();
$reservationStmt->close();
$conn->close();
?>
