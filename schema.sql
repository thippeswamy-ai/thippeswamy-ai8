-- Database Schema for College Lost Things and Found System

DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Lost_Items;
DROP TABLE IF EXISTS Found_Items;
DROP TABLE IF EXISTS Claims;

-- Admin Table
CREATE TABLE Admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table (Students / Staff)
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_number TEXT,
    department TEXT NOT NULL,
    mobile TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lost Items Table
CREATE TABLE Lost_Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    roll_number TEXT NOT NULL,
    department TEXT NOT NULL,
    mobile TEXT NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    location_lost TEXT NOT NULL,
    date_lost DATE NOT NULL,
    image_path TEXT,
    status TEXT DEFAULT 'Active', -- 'Active', 'Resolved'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Found Items Table
CREATE TABLE Found_Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finder_name TEXT NOT NULL,
    department TEXT NOT NULL,
    mobile TEXT NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    place_found TEXT NOT NULL,
    date_found DATE NOT NULL,
    image_path TEXT,
    status TEXT DEFAULT 'Available', -- 'Available', 'Claimed', 'Under Review'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Claims Table
CREATE TABLE Claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    found_item_id INTEGER NOT NULL,
    claimant_name TEXT NOT NULL,
    roll_number TEXT NOT NULL,
    department TEXT NOT NULL,
    mobile TEXT NOT NULL,
    proof_ownership TEXT NOT NULL,
    description TEXT,
    proof_image TEXT,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (found_item_id) REFERENCES Found_Items (id) ON DELETE CASCADE
);
