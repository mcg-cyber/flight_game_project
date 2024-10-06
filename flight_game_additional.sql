CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    co2_consumed DECIMAL(10, 2) DEFAULT 0,
    co2_budget DECIMAL(10, 2) DEFAULT 0,
    points INT DEFAULT 0,
    crash_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    method VARCHAR(50) NOT NULL,
    details VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS flight_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_country VARCHAR(255) NOT NULL,
    destination_country VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS game (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    co2_consumed DECIMAL(10, 2) NOT NULL,
    co2_budget DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS fun_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_description TEXT NOT NULL,
    action_required TEXT NOT NULL,
    additional_info TEXT
);

INSERT INTO fun_events (event_description, action_required, additional_info)
VALUES
('Turbulence Monster Trivia', 'Answer trivia questions to calm the monster', 'Earn bonus points for correct answers'),
('In-flight Joke Time', 'Tell a joke to entertain passengers', 'Receive funny responses from virtual passengers'),
('Pilot Prank Call', 'Dial the cockpit for a silly prank call', 'Enjoy a humorous conversation with the virtual pilot');
