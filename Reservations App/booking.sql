DROP DATABASE IF EXISTS bookings;
CREATE DATABASE bookings;
USE bookings;

CREATE TABLE Customer (
CustID INT NOT NULL PRIMARY KEY,
FirstName VARCHAR(20) NOT NULL,
Surname VARCHAR(20) NOT NULL,
Email VARCHAR(50) NOT NULL,
Phone VARCHAR(20) NOT NULL,
ArrivalInfo VARCHAR(200)
);

CREATE TABLE Reservation(
DateOfRes_Start DATE NOT NULL, 
DateOfRes_End DATE NOT NULL,
No_Of_People INT NOT NULL,
No_Adults INT NOT NULL,
No_Children INT,
Booking_Site VARCHAR(25) NOT NULL,
Total_Amount INT NOT NULL,
Paid_Y_N VARCHAR(5) NOT NULL,
Date_Paid DATE,
Comments VARCHAR(200),
CustID INT, 
FOREIGN KEY (CustID) REFERENCES Customer(CustID)
);