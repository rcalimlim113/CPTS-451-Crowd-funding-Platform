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
    method_type VARCHAR(50) NOT NULL,
    user_id INT,
    CONSTRAINT fk_paymentMethods_to_users FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Donations
create table Donations(
    donation_id NUMBER PRIMARY KEY,
    message VARCHAR2(500),
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- donation time
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded'))
);

-- Pays relationship
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


-- Check user and campaigns
insert into USERS
values (default, 'John', 'Smith', 'johnS@gmail.com', 'password1234', 'user', '123-456-7890',CURRENT_TIMESTAMP,TRUE);
insert into USERS values (default, 'Alex', 'Bones', 'AlexB@gmail.com', '123456789', 'user', '598-123-4512',CURRENT_TIMESTAMP,TRUE);

select * from users;

insert into CAMPAIGNS
values (default, 1, 'Help my Cat!', 'My cat needs help, anything helps!', 1000.95, DATE '2026-01-01', DATE '2027-01-01', 'active', TRUE, CURRENT_TIMESTAMP);

select * from campaigns;

select first_name, last_name, campaigns.title from campaigns, users
where organizer_id = user_id;

-- test donations
insert into donations
values (1, 'Get well soon!', 50.13, CURRENT_TIMESTAMP, 'pending');

-- test payment to user connection
insert into PAYMENT_METHODS
values (1, 'SECRETTOKEN', 'VISA', 2);

select * from PAYMENT_METHODS;

-- check user payment_method donations campaign connection
insert into pays_to
values (1, 1, 1, 2);

select * from pays_to;

select (first_name || ' ' || last_name) as Name, donations.amount, method_type, campaigns.title 
from campaigns, donations, payment_methods, users, pays_to
where pays_to.donation_id = donations.donation_id and pays_to.payment_method_ID = payment_methods.payment_method_id
    and pays_to.campaign_id = campaigns.campaign_id and pays_to.user_id = users.user_id;