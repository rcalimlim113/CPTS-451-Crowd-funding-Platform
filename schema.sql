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
    description VARCHAR(2000) NOT NULL,
    funding_goal DECIMAL(12,2) NOT NULL CHECK (funding_goal > 0),
    start_date DATE DEFAULT CURRENT_DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    is_approved  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_date > start_date)
);
