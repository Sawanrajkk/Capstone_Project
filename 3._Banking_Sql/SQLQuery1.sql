---------------------------------------------------------
-- 1. CREATE DATABASE
---------------------------------------------------------
DROP DATABASE IF EXISTS BankSystem;


CREATE DATABASE BankSystem;


USE BankSystem;


---------------------------------------------------------
-- 2. CREATE TABLES (SQL SERVER COMPATIBLE)
---------------------------------------------------------
CREATE TABLE Customers (
    CustomerID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100),
    Phone VARCHAR(20)
);
GO

CREATE TABLE Accounts (
    AccountNo VARCHAR(10) PRIMARY KEY,
    CustomerID VARCHAR(10),
    Balance FLOAT NOT NULL DEFAULT 0,  -- FIXED FOR SQL SERVER
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
GO

CREATE TABLE Transactions (
    ID INT IDENTITY(1,1) PRIMARY KEY,  -- SQL SERVER AUTO INCREMENT
    Timestamp DATETIME,
    AccountNo VARCHAR(10),
    Action VARCHAR(20),
    Amount FLOAT,
    FOREIGN KEY (AccountNo) REFERENCES Accounts(AccountNo)
);
GO

---------------------------------------------------------
-- 3. INSERT SAMPLE CUSTOMERS (5)
---------------------------------------------------------
INSERT INTO Customers VALUES
('C001','Sawan Kumar','sawan@gmail.com','999998888'),
('C002','Aman Verma','aman@gmail.com','888887777'),
('C003','Rohit Singh','rohit@gmail.com','777776666'),
('C004','Priya Sharma','priya@gmail.com','666665555'),
('C005','Neha Gupta','neha@gmail.com','555554444');
GO

---------------------------------------------------------
-- 4. INSERT SAMPLE ACCOUNTS (5)
---------------------------------------------------------
INSERT INTO Accounts VALUES
('A0001','C001',5000),
('A0002','C002',12000),
('A0003','C003',1500),
('A0004','C004',25000),
('A0005','C005',8000);
GO

---------------------------------------------------------
-- 5. INSERT SAMPLE TRANSACTIONS (10)
---------------------------------------------------------
INSERT INTO Transactions (Timestamp, AccountNo, Action, Amount) VALUES
(GETDATE(), 'A0001', 'deposit', 2000),
(GETDATE(), 'A0001', 'withdraw', 500),
(GETDATE(), 'A0002', 'deposit', 3000),
(GETDATE(), 'A0003', 'deposit', 1000),
(GETDATE(), 'A0004', 'withdraw', 2000),
(GETDATE(), 'A0004', 'interest', 750),
(GETDATE(), 'A0005', 'deposit', 2000),
(GETDATE(), 'A0005', 'withdraw', 1000),
(GETDATE(), 'A0002', 'interest', 360),
(GETDATE(), 'A0003', 'withdraw', 200);
GO

---------------------------------------------------------
-- FUNCTIONALITY COMMANDS
---------------------------------------------------------

---------------------------------------------------------
-- 6. ADD NEW CUSTOMER
---------------------------------------------------------
INSERT INTO Customers (CustomerID, Name, Email, Phone)
VALUES ('C006', 'Ravi Kumar', 'ravi@gmail.com', '999990000');
GO

---------------------------------------------------------
-- 7. CREATE NEW ACCOUNT
---------------------------------------------------------
INSERT INTO Accounts (AccountNo, CustomerID, Balance)
VALUES ('A0006', 'C006', 0);
GO

---------------------------------------------------------
-- 8. DEPOSIT
---------------------------------------------------------
UPDATE Accounts
SET Balance = Balance + 5000
WHERE AccountNo = 'A0001';
GO

INSERT INTO Transactions (Timestamp, AccountNo, Action, Amount)
VALUES (GETDATE(), 'A0001', 'deposit', 5000);
GO

---------------------------------------------------------
-- 9. WITHDRAW
---------------------------------------------------------
UPDATE Accounts
SET Balance = Balance - 2000
WHERE AccountNo = 'A0001';
GO

INSERT INTO Transactions (Timestamp, AccountNo, Action, Amount)
VALUES (GETDATE(), 'A0001', 'withdraw', 2000);
GO

---------------------------------------------------------
-- 10. ADD INTEREST (3%)
---------------------------------------------------------
UPDATE Accounts
SET Balance = Balance + (Balance * 0.03)
WHERE AccountNo = 'A0002';
GO

INSERT INTO Transactions (Timestamp, AccountNo, Action, Amount)
VALUES (
    GETDATE(),
    'A0002',
    'interest',
    (SELECT TOP 1 Balance * 0.03 FROM Accounts WHERE AccountNo='A0002')
);
GO

---------------------------------------------------------
-- REPORTS (WITH JOINS)
---------------------------------------------------------

---------------------------------------------------------
-- 11. VIEW ALL CUSTOMERS
---------------------------------------------------------
SELECT * FROM Customers;
GO

---------------------------------------------------------
-- 12. VIEW ALL ACCOUNTS
---------------------------------------------------------
SELECT * FROM Accounts;
GO

---------------------------------------------------------
-- 13. VIEW ACCOUNT + CUSTOMER DETAILS (JOIN)
---------------------------------------------------------
SELECT 
    A.AccountNo,
    C.Name,
    C.Email,
    A.Balance
FROM Accounts A
INNER JOIN Customers C ON A.CustomerID = C.CustomerID;
GO

---------------------------------------------------------
-- 14. FULL TRANSACTION HISTORY (3 TABLE JOIN)
---------------------------------------------------------
SELECT 
    T.ID,
    T.Timestamp,
    T.AccountNo,
    T.Action,
    T.Amount,
    C.Name
FROM Transactions T
INNER JOIN Accounts A ON T.AccountNo = A.AccountNo
INNER JOIN Customers C ON A.CustomerID = C.CustomerID
ORDER BY T.ID DESC;
GO

---------------------------------------------------------
-- 15. TOP 3 ACCOUNTS BY BALANCE (SQL SERVER USES TOP)
---------------------------------------------------------
SELECT TOP 3
    A.AccountNo,
    C.Name,
    A.Balance
FROM Accounts A
INNER JOIN Customers C ON A.CustomerID = C.CustomerID
ORDER BY A.Balance DESC;
GO

---------------------------------------------------------
-- 16. TOTAL BANK BALANCE
---------------------------------------------------------
SELECT SUM(Balance) AS TotalBankBalance
FROM Accounts;
GO

---------------------------------------------------------
-- 17. DELETE CUSTOMER + ACCOUNT + TRANSACTIONS
-- Example: Delete customer C003
---------------------------------------------------------

-- Delete transactions first
DELETE T
FROM Transactions T
INNER JOIN Accounts A ON T.AccountNo = A.AccountNo
WHERE A.CustomerID = 'C003';
GO

-- Delete accounts
DELETE FROM Accounts
WHERE CustomerID = 'C003';
GO

-- Delete customer
DELETE FROM Customers
WHERE CustomerID = 'C003';
GO

---------------------------------------------------------
-- 18. FULL BANK OVERVIEW (JOIN 3 TABLES)
---------------------------------------------------------
SELECT 
    C.CustomerID,
    C.Name,
    A.AccountNo,
    A.Balance,
    T.Action,
    T.Amount,
    T.Timestamp
FROM Customers C
LEFT JOIN Accounts A ON C.CustomerID = A.CustomerID
LEFT JOIN Transactions T ON A.AccountNo = T.AccountNo
ORDER BY C.CustomerID, T.Timestamp DESC;
GO
