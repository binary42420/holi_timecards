-- Google OAuth Database Migration for EasyShifts
-- Add Google OAuth columns to the users table

-- Add google_id column (unique identifier from Google)
ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE NULL;

-- Add email column
ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL;

-- Add google_picture column (URL to profile picture)
ALTER TABLE users ADD COLUMN google_picture VARCHAR(500) NULL;

-- Add last_login column
ALTER TABLE users ADD COLUMN last_login DATETIME NULL;

-- Make password column nullable for Google OAuth users
ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL;

-- Add indexes for better performance
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);

-- Verify the changes
DESCRIBE users;
