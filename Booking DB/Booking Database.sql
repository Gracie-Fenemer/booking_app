DROP DATABASE IF EXISTS Bookings;
CREATE DATABASE IF NOT EXISTS Bookings;
USE Bookings;

CREATE TABLE Customer (
    CustID INT NOT NULL PRIMARY KEY auto_increment,
    FirstName VARCHAR(20) NOT NULL,
    Surname VARCHAR(20) NOT NULL,
    Email VARCHAR(50) NOT NULL,
    Phone CHAR(20) NOT NULL,
    ArrivalInfo VARCHAR(200)
);


CREATE TABLE Reservation (
    CustID INT,
    DateOfRes_Start DATE NOT NULL, 
    DateOfRes_End DATE NOT NULL,
    No_Of_People INT NOT NULL,
    No_Adults INT NOT NULL,
    No_Children INT,
    Booking_Site VARCHAR(25) NOT NULL,
    Total_Amount INT NOT NULL,
    Paid_Y_N CHAR(3) NOT NULL CHECK (Paid_Y_N IN ('Yes', 'No')),
    Date_Paid DATE,
    Comments VARCHAR(200),
    FOREIGN KEY (CustID) REFERENCES Customer(CustID) ON DELETE CASCADE,
    CHECK (DateOfRes_Start < DateOfRes_End) -- Table-level CHECK constraint
);

ALTER TABLE Reservation
ADD CONSTRAINT unique_dates UNIQUE (DateOfRes_Start, DateOfRes_End);

SELECT * FROM Customer;

SELECT * FROM Reservation;

-- DELETE FROM Customer WHERE CustID = 4;

ALTER TABLE Reservation
DROP COLUMN Reservation_Date;


DROP PROCEDURE IF EXISTS fillReservationDates;

DELIMITER $$

CREATE PROCEDURE fillReservationDates(IN custID INT, IN dateStart DATE, IN dateEnd DATE, noOfPeople INT)
BEGIN
  DECLARE currentDate DATE;

  SET currentDate = dateStart;

  -- Loop through each date in the range and insert a new row for each date
  WHILE currentDate <= dateEnd DO
    INSERT INTO Reservation (CustID, DateOfRes_Start, DateOfRes_End, Reservation_Date)
    VALUES (custID, dateStart, dateEnd, currentDate, noOfPeople);
    SET currentDate = DATE_ADD(currentDate, INTERVAL 1 DAY);  -- Move to the next date
  END WHILE;

END $$

DELIMITER ;

-- CALL fillReservationDates(3, '2024-11-18', '2024-11-23', 4);
