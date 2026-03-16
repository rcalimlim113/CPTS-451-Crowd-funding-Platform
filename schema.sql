-- TABLES

-- Users Table
CREATE TABLE Users (
    user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR2(20) NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT chk_user_role 
    CHECK (role IN ('admin', 'user'))
);

-- Campaigns table
CREATE TABLE campaigns (
    campaign_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organizer_id INT NOT NULL REFERENCES users(user_id),
    title VARCHAR(200) NOT NULL,
    description CLOB NOT NULL,
    funding_goal DECIMAL(12,2) NOT NULL CHECK (funding_goal > 0),
    start_date DATE DEFAULT CURRENT_DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    is_approved  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_date > start_date)
);

-- VIEWS

-- General user campaign view
CREATE VIEW active_campaigns_view AS
SELECT 
    campaign_id,
    title,
    description,
    funding_goal,
    start_date,
    end_date,
    created_at
FROM Campaigns
WHERE is_approved = TRUE;
-- Use with:
SELECT * FROM active_campaigns_view;

-- User created campaign view
CREATE VIEW user_campaigns_view AS
SELECT
    c.campaign_id,
    c.organizer_id,
    c.title,
    c.description,
    c.funding_goal,
    c.start_date,
    c.end_date,
    c.is_approved,
    c.created_at,
    u.user_id,
    u.first_name,
    u.last_name
FROM Campaigns c
JOIN Users u ON c.organizer_id = u.user_id;
-- Use with:
SELECT * 
FROM user_campaigns_view
WHERE user_id = organizer_id;
