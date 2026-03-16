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

-- Campaign Updates table
CREATE TABLE campaign_updates (
    campaign_id INT NOT NULL REFERENCES campaigns(campaign_id),
    update_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content CLOB NOT NULL,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campaign_id, update_id)
);

-- Campaign Share table
CREATE TABLE campaign_share (
    campaign_id INT NOT NULL REFERENCES campaigns(campaign_id),
    share_id INT NOT NULL,
    platform VARCHAR(50),
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campaign_id, share_id)
);



-- Payment
create table Payment_Methods(
    payment_method_id INT PRIMARY KEY,
    payment_token VARCHAR(100) NOT NULL,
    method_type VARCHAR(50) NOT NULL
);

-- Donations
create table Donations(
    donation_id NUMBER PRIMARY KEY,
    message VARCHAR2(500),
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- donation time
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded'))
);

create table pays_to(
    donation_id INT PRIMARY KEY,
    payment_method_id INT,
    campaign_id INT,
    user_id INT,
    CONSTRAINT fk_paysTo_to_paymentMethodID FOREIGN KEY (payment_method_id) REFERENCES Payment_Methods(payment_method_id),
    CONSTRAINT fk_paysTo_to_campaignID FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CONSTRAINT fk_paysTo_to_donationID FOREIGN KEY (donation_id) REFERENCES donations(donation_id),
    CONSTRAINT fk_paysTo_to_userID FOREIGN KEY (user_id) REFERENCES users(user_id)
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
    status,
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
    c.status,
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

-- Admin campaign view
CREATE VIEW admin_campaigns_view AS
SELECT
    c.campaign_id,
    c.organizer_id,
    c.title,
    c.description,
    c.funding_goal,
    c.start_date,
    c.end_date,
    c.status,
    c.is_approved,
    c.created_at,
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.is_active AS user_status
FROM Campaigns c
JOIN Users u ON c.organizer_id = u.user_id;
-- Use with:
SELECT * FROM admin_campaigns_view;

-- Admin user view
CREATE VIEW admin_users_view AS
SELECT
    user_id,
    first_name,
    last_name,
    email,
    role,
    phone_number,
    created_at,
    is_active
FROM Users;
-- Use with:
SELECT * FROM admin_users_view;

