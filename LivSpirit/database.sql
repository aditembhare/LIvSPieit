-- Living Spiritz Database Schema
-- Run this in phpMyAdmin (SQL tab) before starting the Flask app

CREATE DATABASE IF NOT EXISTS living_spiritz
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE living_spiritz;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habits (with streak tracking)
CREATE TABLE IF NOT EXISTS habits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT 1,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    icon VARCHAR(50) DEFAULT 'checklist',
    streak INT DEFAULT 0,
    last_completed DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Mood Logs
CREATE TABLE IF NOT EXISTS mood_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT 1,
    mood_level VARCHAR(20) NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reflection Journal
CREATE TABLE IF NOT EXISTS reflections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT 1,
    title VARCHAR(255) DEFAULT 'Untitled',
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Goals
CREATE TABLE IF NOT EXISTS goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT 1,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'Personal',
    target_value INT DEFAULT 100,
    current_value INT DEFAULT 0,
    unit VARCHAR(50),
    deadline DATE,
    priority TINYINT DEFAULT 2,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Goal Updates
CREATE TABLE IF NOT EXISTS goal_updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT NOT NULL,
    update_value INT DEFAULT 0,
    note VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
);

-- Seed default user (Flask will also do this automatically on first run)
INSERT IGNORE INTO users (id, username, email, password)
VALUES (1, 'Elena', 'elena@example.com', 'password123');
