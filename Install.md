### Installation Guide

## Setting Up the Database

1. Create a new database named `flight_game` in your MySQL server.
2. Connect to your MariaDB server and run the following SQL command to create the database:

   ```sql
   CREATE DATABASE flight_game;
   ```

## Creating Tables

1. Use the `flight_game` database for creating tables related to the game.
2. Run the following SQL commands to create the necessary tables:

### Creating the `fun_events` Table

```sql
CREATE TABLE fun_events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    event_description TEXT,
    action_required TEXT,
    additional_info TEXT
);
```

### Creating Other Tables (e.g., `airport`, `country`, `game`, `goal`, `goal_reached`)

Add SQL commands here to create other tables as needed.

## Inserting Sample Data

1. Populate the `fun_events` table with sample data for fun events.
2. Run the following SQL commands to insert sample data into the `fun_events` table:

```sql
INSERT INTO fun_events (event_description, action_required, additional_info)
VALUES
('Turbulence Monster Trivia', 'Answer trivia questions to calm the monster', 'Earn bonus points for correct answers'),
('In-flight Joke Time', 'Tell a joke to entertain passengers', 'Receive funny responses from virtual passengers'),
('Pilot Prank Call', 'Dial the cockpit for a silly prank call', 'Enjoy a humorous conversation with the virtual pilot');
```

3. Optionally, add instructions for inserting sample data into other tables if needed.

## Setting Up Environment Variables

1. Set the OpenWeatherMap API key as an environment variable:

   ```bash
   export OPENWEATHER_API_KEY=your_api_key
   ```

## Configuring Database Credentials

1. Ensure the `secrets.py` file contains the correct database credentials:

   ```python
   db_name = "your_database_name"
   db_user = "your_database_user"
   db_password = "your_database_password"
   ```

## Installing Required Python Dependencies

pip install -r requirements.txt

## Installation Complete

The database setup, table creation, and sample data insertion steps have been completed.
Your database is now ready for use with the flight simulator game.
