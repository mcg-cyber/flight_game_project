import mysql.connector
import random
import os
import time
import random
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import secrets

# Connect to the database
db_connection = mysql.connector.connect(
    host = "172.17.0.2",
    port = "3306",
    database = secrets.db_name,
    user = secrets.db_user,
    password = secrets.db_password,
    autocommit = True
)

# Create a cursor object to execute SQL queries
cursor = db_connection.cursor()

# Ensure the users table has the necessary columns
cursor.execute(
    """
ALTER TABLE users
ADD COLUMN IF NOT EXISTS co2_consumed DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS co2_budget DECIMAL(10, 2) DEFAULT 0
"""
)

# Create the payment_methods table if it doesn't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    method VARCHAR(50) NOT NULL,
    details VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""
)

# Create the country table if it doesn't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS country (
    iso_country VARCHAR(2) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
)
"""
)

# Create the flight_history table if it doesn't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS flight_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_country VARCHAR(255) NOT NULL,
    destination_country VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""
)

# Create the game table if it doesn't exist
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS game (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    co2_consumed DECIMAL(10, 2) NOT NULL,
    co2_budget DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""
)


# Function to create a new user or retrieve existing user details
def get_or_create_user():
    name = input("Enter your name: ")
    try:
        cursor.execute("SELECT id, age FROM users WHERE name = %s", (name,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None, None

    if user:
        user_id, age = user
        print(f"Welcome back, {name}!")
        cursor.execute(
            "SELECT source_country, destination_country FROM flight_history WHERE user_id = %s",
            (user_id,),
        )
        flights = cursor.fetchall()
        if flights:
            print("Your previous flights:")
            for flight in flights:
                print(f"From {flight[0]} to {flight[1]}")
        continue_game = input("Do you want to continue playing the game? (y/n): ")
        if continue_game.lower() != "y":
            print("Thank you for visiting! Goodbye!")
            exit()
        return user_id, name, age
    else:
        print("User not found. Please create a new user.")
        while True:
            try:
                age = int(input("Enter your age: "))
                if age < 16:
                    print("Sorry! You cannot play the game.")
                    exit()
                break
            except ValueError:
                print("Please enter a valid integer for age.")

        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", (name, age))
        db_connection.commit()
        user_id = cursor.lastrowid
        print("User created successfully!")
        return user_id, name, age


# Function to book a flight
def book_flight():
    print("Welcome to the flight booking system!")

    # Display available countries with their codes for booking
    try:
        cursor.execute("SELECT iso_country, name FROM country")
        countries = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None, None, None, None
    print("Available countries for booking:")
    for code, name in countries:
        print(f"{code}: {name}")

    # Player selects source and destination countries by code
    source_country_code = input("Enter the source country code: ").strip().upper()
    destination_country_code = (
        input("Enter the destination country code: ").strip().upper()
    )

    # Fetch and display airports for the selected source country
    cursor.execute(
        "SELECT name FROM airport WHERE iso_country = %s", (source_country_code,)
    )
    source_airports = cursor.fetchall()
    print("Available airports in the source country:")
    for idx, airport in enumerate(source_airports, start=1):
        print(f"{idx}. {airport[0]}")
    source_airport_idx = (
        int(input("Select the source airport (Enter the number): ")) - 1
    )
    source_airport = source_airports[source_airport_idx][0]

    # Fetch and display airports for the selected destination country
    cursor.execute(
        "SELECT name FROM airport WHERE iso_country = %s", (destination_country_code,)
    )
    destination_airports = cursor.fetchall()
    print("Available airports in the destination country:")
    for idx, airport in enumerate(destination_airports, start=1):
        print(f"{idx}. {airport[0]}")
    destination_airport_idx = (
        int(input("Select the destination airport (Enter the number): ")) - 1
    )
    destination_airport = destination_airports[destination_airport_idx][0]

    source_country = next(
        name for code, name in countries if code == source_country_code
    )
    destination_country = next(
        name for code, name in countries if code == destination_country_code
    )

    print(
        f"Booking flight from {source_country} to {destination_country}... Fasten your seatbelt, it's going to be a bumpy ride!"
    )

    # Fetch and display weather data for the destination country
    weather_data = fetch_weather_data(destination_country)
    if weather_data:
        temperature = weather_data.get("main", {}).get("temp")
        weather_condition = weather_data.get("weather", [{}])[0].get("main")
        print(
            f"Current weather in {destination_country}: {temperature}°C, {weather_condition}. Perfect weather for flying... or maybe not!"
        )
    else:
        print("Could not retrieve weather data for the destination.")
    # Calculate and display the flight price in euros
    distance, time_hours = calculate_distance_time(source_country, destination_country)
    price = (distance / 100) * 10  # Calculate price based on distance
    print(f"The price for this flight is: €{price:.2f}")
    print("Select a payment method:")
    print("1. Apple Pay")
    print("2. Google Pay")
    print("3. Visa")
    payment_choice = int(input("Enter the number of your choice: "))

    if payment_choice == 1:
        method = "Apple Pay"
        details = input("Enter your Apple Pay email: ")
    elif payment_choice == 2:
        method = "Google Pay"
        details = input("Enter your Google Pay email: ")
    elif payment_choice == 3:
        method = "Visa"
        details = input("Enter your Visa card number: ")
    else:
        print("Invalid choice. Defaulting to Visa.")
        method = "Visa"
        details = input("Enter your Visa card number: ")

    # Add a humorous twist based on the payment method
    prank_messages = {
        "Visa": "Oh no! Your Visa card is reported stolen!",
        "Google Pay": "Oops! Your Google account has been hacked!",
        "Apple Pay": "Yikes! Your Apple account has been hacked!",
    }

    if method in prank_messages:
        print(prank_messages[method])
        print("Just kidding! All is informed to the police. Enjoy your flight!")

    return source_country, destination_country, method, details, price


# Function to calculate distance and time between countries using geopy
def calculate_distance_time(source_country, destination_country):
    geolocator = Nominatim(user_agent="flight_simulator")

    source_location = geolocator.geocode(source_country)
    destination_location = geolocator.geocode(destination_country)

    distance = geodesic(
        (source_location.latitude, source_location.longitude),
        (destination_location.latitude, destination_location.longitude),
    ).kilometers

    time_hours = distance / 800  # Assuming average speed of 800 km/h

    return distance, time_hours


# Function to fetch current weather data for a location using OpenWeatherMap API
def fetch_weather_data(location):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OpenWeather API key not found.")
        return None

    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch weather data: {e}")
        return None


def display_plane_art():
    plane_art_options = [
        """
            -|-
        --o-(+)--o--
        """,
        """
           __|__
    --o--o--(_)--o--o--
           """,
        """
             __|__
    --o---o--( * )--o---o--
           """,
    ]

    plane_art = random.choice(plane_art_options)
    print("Plane taking off! Make sure your seatbelt is on during the take off!")
    print(plane_art)
    time.sleep(1)


# Function to fetch and execute a random fun event from the database
def trigger_fun_event():
    cursor.execute(
        "SELECT event_description, action_required, additional_info FROM fun_events ORDER BY RAND() LIMIT 1"
    )
    event_data = cursor.fetchone()

    if event_data:
        event_description, action_required, additional_info = event_data
        print(f"\nFun Event: {event_description}")
        print(f"Action Required: {action_required}")
        print(f"Additional Info: {additional_info}")
    else:
        print("No fun events available at the moment. Enjoy your flight!")


# Function to check CO2 consumption and assign a funny title
def check_co2_consumption(user_id):
    co2_consumed = random.uniform(0, 100)  # Random value between 0 and 100
    co2_budget = random.uniform(50, 150)   # Random value between 50 and 150

    print(f"\nCO2 Consumed: {co2_consumed:.2f} kg, CO2 Budget: {co2_budget:.2f} kg")

    cursor.execute(
        "UPDATE users SET co2_consumed = %s, co2_budget = %s WHERE id = %s",
        (co2_consumed, co2_budget, user_id),
    )
    db_connection.commit()

    if float(co2_consumed) < float(co2_budget) * 0.5:
        print("Title: Eco-Friendly Traveler 🌿")
    elif float(co2_consumed) < float(co2_budget):
        print("Title: Conscious Commuter 🚴")
    else:
        print("Title: Carbon Footprint Champion 🏆")


# Function to simulate plane landing with ASCII art
def display_fun_fact(destination_country):
    fun_facts = {
        "France": "Did you know? France is the most visited country in the world!",
        "Japan": "Fun Fact: Japan has more than 5 million vending machines!",
        "Brazil": "Did you know? Brazil is home to the Amazon Rainforest, the largest rainforest in the world!",
        "Australia": "Fun Fact: Australia is wider than the moon!",
        "Canada": "Did you know? Canada has the longest coastline in the world!",
    }
    fact = fun_facts.get(
        destination_country, "No fun fact available for this destination."
    )
    print(f"\nFun Fact about {destination_country}: {fact}")


def simulate_plane_landing():
    print("\nThe plane will be landing in a few minutes. Please fasten your seatbelt.")
    print("Oh no! The pilot has fallen asleep and the landing gear is broken!")
    print("Just kidding! Everything is under control. Enjoy the landing!")
    landing_art = """
        __|__
 --o--o--(O)--o--o--
    """
    print(landing_art)
    time.sleep(2)


# Function to simulate a lighthearted "hijack" scenario
def hijack_scenario():
    print("\nOh no! The plane has been 'hijacked' by mischievous characters!")
    print("They demand 100,000 euros to release control of the plane.")
    payment = input("Do you want to pay the ransom? (y/n): ")
    if payment.lower() == "y":
        print("You have paid the ransom. The plane is now safe.")
    else:
        print(
            "You chose not to pay. The hijackers are now remotely controlling the plane!"
        )
        print(
            "Just kidding! Everything is under control. Enjoy the rest of your flight!"
        )


def main():
    while True:
        user_id, name, age = get_or_create_user()

        source_country, destination_country, method, details, price = book_flight()

        cursor.execute(
            "INSERT INTO payment_methods (user_id, method, details) VALUES (%s, %s, %s)",
            (user_id, method, details),
        )
        db_connection.commit()

        price = random.uniform(
            100, 1000
        )  # Generate a random price between 100 and 1000
        cursor.execute(
            "INSERT INTO flight_history (user_id, source_country, destination_country, price) VALUES (%s, %s, %s, %s)",
            (user_id, source_country, destination_country, price),
        )
        db_connection.commit()
        print(f"You paid ${price:.2f} using {method}.")

        distance, time_hours = calculate_distance_time(
            source_country, destination_country
        )

        print(f"Flight booked from {source_country} to {destination_country}.")
        print(f"Estimated distance: {distance:.2f} km")
        print(f"Estimated flight time: {time_hours:.2f} hours")

        display_fun_fact(destination_country)
        display_plane_art()
        # Simulate hijack scenario
        hijack_scenario()
        simulate_plane_landing()
        check_co2_consumption(user_id)

        play_again = input("Do you want to play again? (y/n): ")
        if play_again.lower() != "y":
            print("Thank you for playing! Goodbye!")
            break

    # Close the cursor and database connection
    cursor.close()
    db_connection.close()


if __name__ == "__main__":
    main()
