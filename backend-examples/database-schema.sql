-- Database Schema Updates for Google OAuth Integration

-- Add Google OAuth columns to existing users table
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN google_email VARCHAR(255);
ALTER TABLE users ADD COLUMN google_name VARCHAR(255);
ALTER TABLE users ADD COLUMN google_picture_url TEXT;
ALTER TABLE users ADD COLUMN google_linked_at TIMESTAMP;
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;

-- Create index for faster Google ID lookups
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_google_email ON users(google_email);

-- Optional: Create separate table for Google account data
CREATE TABLE user_google_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    google_email VARCHAR(255) NOT NULL,
    google_name VARCHAR(255),
    google_picture_url TEXT,
    google_locale VARCHAR(10),
    email_verified BOOLEAN DEFAULT FALSE,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    google_data JSONB, -- Store full Google user data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for the Google accounts table
CREATE INDEX idx_google_accounts_user_id ON user_google_accounts(user_id);
CREATE INDEX idx_google_accounts_google_id ON user_google_accounts(google_id);
CREATE INDEX idx_google_accounts_google_email ON user_google_accounts(google_email);

-- Create audit table for Google authentication events
CREATE TABLE google_auth_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    google_id VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- 'login', 'link', 'create', 'unlink'
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for audit logs
CREATE INDEX idx_google_auth_logs_user_id ON google_auth_logs(user_id);
CREATE INDEX idx_google_auth_logs_created_at ON google_auth_logs(created_at);
CREATE INDEX idx_google_auth_logs_action ON google_auth_logs(action);

-- Example queries for common operations

-- Find user by Google ID
-- SELECT * FROM users WHERE google_id = 'google_user_id_here';

-- Find user by Google ID or email
-- SELECT * FROM users 
-- WHERE google_id = 'google_user_id_here' 
--    OR google_email = 'user@example.com';

-- Link Google account to existing user
-- UPDATE users 
-- SET google_id = 'google_user_id_here',
--     google_email = 'user@example.com',
--     google_name = 'User Name',
--     google_picture_url = 'https://...',
--     google_linked_at = CURRENT_TIMESTAMP
-- WHERE id = user_id_here;

-- Create new user with Google account
-- INSERT INTO users (
--     username, name, email, password_hash, 
--     google_id, google_email, google_name, google_picture_url,
--     is_manager, approved, google_linked_at, created_at
-- ) VALUES (
--     'username', 'Full Name', 'email@example.com', NULL,
--     'google_user_id', 'email@example.com', 'Full Name', 'https://...',
--     FALSE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- Log Google authentication event
-- INSERT INTO google_auth_logs (
--     user_id, google_id, action, ip_address, user_agent, success
-- ) VALUES (
--     user_id_here, 'google_user_id', 'login', '192.168.1.1', 'User Agent', TRUE
-- );

-- Get users with Google accounts linked
-- SELECT u.*, 
--        CASE WHEN u.google_id IS NOT NULL THEN TRUE ELSE FALSE END as has_google_account
-- FROM users u
-- WHERE u.google_id IS NOT NULL;

-- Get authentication statistics
-- SELECT 
--     action,
--     COUNT(*) as total_attempts,
--     COUNT(CASE WHEN success THEN 1 END) as successful_attempts,
--     COUNT(CASE WHEN NOT success THEN 1 END) as failed_attempts
-- FROM google_auth_logs 
-- WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
-- GROUP BY action;

-- Clean up old audit logs (optional maintenance)
-- DELETE FROM google_auth_logs 
-- WHERE created_at < CURRENT_DATE - INTERVAL '1 year';
