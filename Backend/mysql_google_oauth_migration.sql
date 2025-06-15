-- MySQL Database Schema Updates for Google OAuth Integration
-- Compatible with your existing EasyShifts MySQL database

-- First, let's add the basic Google OAuth columns to the existing users table
-- These match exactly what the Python code expects

-- Add google_id column (Google's unique identifier)
ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE NULL;

-- Add email column 
ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL;

-- Add google_picture column (URL to Google profile picture)
ALTER TABLE users ADD COLUMN google_picture VARCHAR(500) NULL;

-- Add last_login column (timestamp of last login)
ALTER TABLE users ADD COLUMN last_login DATETIME NULL;

-- Make password column nullable for Google OAuth users (they don't need passwords)
ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL;

-- Create indexes for better performance
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);

-- Verify the changes by showing the updated table structure
DESCRIBE users;

-- Show a sample of the users table to confirm changes
SELECT COUNT(*) as total_users FROM users;

-- Test query to verify Google OAuth columns work
SELECT id, username, name, email, google_id, google_picture, last_login 
FROM users 
LIMIT 5;
