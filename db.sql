USE freedb_MacroTrack;

-- Users table to store user information
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UserTokens table to store tokens for the "Remember Me" functionality
CREATE TABLE UserTokens (
    TokenID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Token VARCHAR(255) NOT NULL UNIQUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) 
);

-- Food table to store food items added by users
CREATE TABLE Food (
    FoodID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Name VARCHAR(50) NOT NULL,
    Proteins FLOAT NOT NULL, -- FLOAT for better precision
    Carbs FLOAT NOT NULL, -- FLOAT for better precision
    Fats FLOAT NOT NULL, -- FLOAT for better precision
    Calories FLOAT GENERATED ALWAYS AS (Proteins * 4 + Carbs * 4 + Fats * 9) STORED, -- FLOAT for better precision
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Logs table to store log entries for each date per user
CREATE TABLE Logs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Date DATE NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- LogFood table to store the food items and quantities for each log
CREATE TABLE LogFood (
    LogFoodID INT AUTO_INCREMENT PRIMARY KEY,
    LogID INT NOT NULL,
    FoodID INT NOT NULL,
    Quantity FLOAT NOT NULL, -- FLOAT for better precision
    FOREIGN KEY (LogID) REFERENCES Logs(LogID),
    FOREIGN KEY (FoodID) REFERENCES Food(FoodID) 
);
