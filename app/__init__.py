import os
from flask import Flask, request, render_template, jsonify
from . import db
import sqlite3
import re

#app = Flask(__name__)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # this value should be randomized
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    
    # load campaigns.html page
    @app.route("/")
    def index():
        db_conn = db.get_db()
        campaigns = db_conn.execute("""
            SELECT c.*, u.first_name || ' ' || u.last_name AS organizer_name
            FROM campaigns c
            JOIN users u ON c.organizer_id = u.user_id
        """).fetchall()
        return render_template('campaigns.html', campaigns=campaigns)

    # load tempName.html page
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            name = request.form['username']
            return f"Hello {name}, POST request received"
        return render_template('tempName.html')

    # --- CRUD route (handles all tables via JSON API) ---
    @app.route('/crud')
    def crud():
        return render_template('crud.html')

    @app.route('/api/crud/<table>', methods=['GET'])
    def crud_read(table):
        ALLOWED = ['users', 'campaigns', 'donations', 'payment_methods', 'user_donations', 'campaign_updates']
        if table not in ALLOWED:
            return jsonify({'error': 'Table not allowed'}), 400
        rows = db.get_db().execute(f"SELECT * FROM {table}").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/users', methods=['POST'])
    def add_user():
        d = request.json
        try:
            db_conn = db.get_db()
            db_conn.execute("""
                INSERT INTO users (first_name, last_name, email, password_hash, role, phone_number)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [d['first_name'], d['last_name'], d['email'], d['password_hash'], d['role'], d.get('phone_number')])
            db_conn.commit()
            return jsonify({'status': 'success', 'message': 'User added successfully'})
        except sqlite3.IntegrityError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    @app.route('/api/campaigns', methods=['POST'])
    def add_campaign():
        d = request.json
        try:
            db.get_db().execute("""
                INSERT INTO campaigns (organizer_id, title, description, funding_goal, end_date)
                VALUES (?, ?, ?, ?, ?)
            """, [d['organizer_id'], d['title'], d['description'], d['funding_goal'], d['end_date']])
            db.get_db().commit()
            return jsonify({'status': 'success', 'message': 'Campaign added successfully'})
        except sqlite3.IntegrityError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    @app.route('/api/donations', methods=['POST'])
    def add_donation():
        d = request.json
        try:
            db_conn = db.get_db()
            db_conn.execute("""
                INSERT INTO donations (donation_id, amount, payment_status, message)
                VALUES (?, ?, ?, ?)
            """, [d['donation_id'], d['amount'], d['payment_status'], d.get('message')])
            db_conn.commit()
            return jsonify({'status': 'success', 'message': 'Donation added successfully'})
        except sqlite3.IntegrityError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    @app.route('/api/payment_methods', methods=['POST'])
    def add_payment_method():
        d = request.json
        try:
            db_conn = db.get_db()
            db_conn.execute("""
                INSERT INTO payment_methods (payment_method_id, user_id, payment_token, method_type)
                VALUES (?, ?, ?, ?)
            """, [d['payment_method_id'], d['user_id'], d['payment_token'], d['method_type']])
            db_conn.commit()
            return jsonify({'status': 'success', 'message': 'Payment method linked successfully'})
        except sqlite3.IntegrityError as e:
            return jsonify({'status': 'error', 'message': f'Database Error: {str(e)}'}), 400

    @app.route('/api/delete/<table>/<int:id>', methods=['DELETE'])
    def delete_record(table, id):
        ALLOWED = {'users': 'user_id', 'campaigns': 'campaign_id', 'donations': 'donation_id', 'payment_methods' : 'payment_method_id', 'user_donations': 'donation_id'}
        if table not in ALLOWED:
            return jsonify({'status': 'error', 'message': 'Invalid table'}), 400
        try:
            db_conn = db.get_db()
            db_conn.execute(f"DELETE FROM {table} WHERE {ALLOWED[table]} = ?", [id])
            db_conn.commit()
            return jsonify({'status': 'success', 'message': 'Deleted successfully'})
        except sqlite3.IntegrityError as e:
            return jsonify({'status': 'error', 'message': 'Cannot delete due to active dependencies.'}), 400

    @app.route('/api/update/<table>/<int:id>', methods=['POST'])
    def update_record(table, id):
        d = request.json 
        db_conn = db.get_db()
        
        column = list(d.keys())[0]
        value = d[column]
        
        pk_map = {
            'users': 'user_id',
            'campaigns': 'campaign_id',
            'donations': 'donation_id',
            'payment_methods': 'payment_method_id'
        }

        try:
            db_conn.execute(f"UPDATE {table} SET {column} = ? WHERE {pk_map[table]} = ?", [value, id])
            db_conn.commit()
            return jsonify({'status': 'success', 'message': f'Updated {column} successfully!'})
        except sqlite3.Error as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    # --- Advanced queries route ---
    @app.route('/queries')
    def queries():
        return render_template('queries.html')

    @app.route('/api/query/<query_id>')
    def run_query(query_id):
        # We use a string-based dictionary to allow for both 1-10 and b1-b12
        QUERIES = {
            # --- BASIC CRUD ---
            'b1': ("New User Account", "INSERT INTO users (user_id, first_name, last_name, email, password_hash, role, is_active) VALUES (999, 'Test', 'User', 'test@test.edu', 'pw123', 'user', 1)", "A new user is stored.", "", ""),
            'b2': ("New Donation Record", "INSERT INTO donations (donation_id, campaign_id, amount, payment_status, message) VALUES (999, 1, 25.00, 'completed', 'Test Donation')", "A donation is added.", "", ""),
            'b3': ("New Payment Method", "INSERT INTO payment_methods (payment_method_id, user_id, payment_token, method_type) VALUES (999, 1, 'tok_test', 'credit_card')", "A new payment method is linked.", "", ""),
            'b4': ("Update Goal Date", "UPDATE campaigns SET end_date = '2027-01-01' WHERE campaign_id = 1", "Extending the deadline.", "", ""),
            'b5': ("Complete Campaign", "UPDATE campaigns SET status = 'completed' WHERE campaign_id = 1", "Marking as finished.", "", ""),
            'b6': ("Toggle User Activity", "UPDATE users SET is_active = 0 WHERE user_id = 999", "Deactivating the test account.", "", ""),
            'b7': ("Delete Test User", "DELETE FROM users WHERE user_id = 999", "Removing the test user account.", "", ""),
            'b8': ("Delete Test Donation", "DELETE FROM donations WHERE donation_id = 999", "Removing the test donation record.", "", ""),
            'b9': ("Delete Test Payment", "DELETE FROM payment_methods WHERE payment_method_id = 999", "Removing the test payment method.", "", ""),
            'b10': ("Active Campaigns", "SELECT * FROM campaigns WHERE status = 'active'", "Viewing current campaigns.", "", ""),
            'b11': ("Admin User Audit", "SELECT * FROM users", "Full list of users.", "", ""),
            'b12': ("Donation Ledger", "SELECT * FROM donations", "Viewing every donation.", "", ""),
            # --- ADVANCED RETRIEVAL ---
            '1': ("User Donation History", 
                "SELECT donations.amount, payment_methods.method_type, campaigns.title FROM donations, payment_methods, campaigns, user_donations WHERE user_donations.donation_id = donations.donation_id AND user_donations.payment_token = payment_methods.payment_token AND donations.campaign_id = campaigns.campaign_id AND user_donations.user_id = 2", 
                "Shows donation amount, payment method, and campaign for a specific user.", 
                "Amount is in donations, method type is in payment_methods, title is in campaigns — JOIN links all three for one user.", ""),

            '2': ("Organizer Directory", 
                "SELECT campaigns.title, (first_name || ' ' || last_name) AS Name FROM campaigns, users WHERE campaigns.organizer_id = users.user_id", 
                "Shows all campaigns and their associated organizer's full name.", 
                "Organizer name is stored in users, not in campaigns — JOIN connects them by organizer_id.", ""),

            '3': ("Campaign Ledger", 
                "SELECT donations.amount, donations.donated_at, donations.message, campaigns.title, (users.first_name || ' ' || users.last_name) AS organizer FROM donations, campaigns, users WHERE donations.campaign_id = campaigns.campaign_id AND campaigns.organizer_id = users.user_id AND campaigns.campaign_id = 1", 
                "Shows all donations for a campaign along with the campaign title and organizer name.", 
                "Donations link to campaigns via campaign_id, and campaigns link to users via organizer_id — combining all three gives full context.", ""),

            '4': ("Campaign Update Feed", 
                "SELECT campaigns.title AS Campaign_Name, campaign_updates.title AS Update_Headline, campaign_updates.content FROM campaigns, campaign_updates WHERE campaigns.campaign_id = campaign_updates.campaign_id AND campaigns.campaign_id = 1", 
                "Shows all updates for a specific campaign.", 
                "Update content is in campaign_updates, campaign title is in campaigns — JOIN links them by campaign_id.", ""),

            '5': ("Card Transaction Audit", 
                "SELECT payment_methods.payment_method_id, payment_methods.method_type, donations.amount FROM donations, payment_methods, user_donations WHERE user_donations.donation_id = donations.donation_id AND user_donations.payment_token = payment_methods.payment_token AND payment_methods.payment_method_id = 1", 
                "Shows a specific card's donation history.", 
                "Amount is in donations, card type is in payment_methods — JOIN through user_donations connects them by payment token.", ""),

            '6': ("Public Feed", 
                "SELECT (first_name || ' ' || last_name) AS Name, campaigns.title FROM campaigns, donations, users, user_donations WHERE user_donations.donation_id = donations.donation_id AND donations.campaign_id = campaigns.campaign_id AND user_donations.user_id = users.user_id", 
                "Shows who has donated to what campaign.", 
                "Donor names are in users, campaign titles are in campaigns — user_donations and donations bridge them together.", ""),

            '7': ("Organizer Contact Sheet", 
                "SELECT campaigns.title, (first_name || ' ' || last_name) AS Name, users.email FROM campaigns, users WHERE campaigns.organizer_id = users.user_id", 
                "Shows campaign title along with organizer contact info.", 
                "Email and name are in users, campaign title is in campaigns — JOIN connects organizer info to their campaigns.", ""),

            '8': ("Social Platform Reach", 
                "SELECT campaigns.title, campaign_share.platform FROM campaigns, campaign_share WHERE campaigns.campaign_id = campaign_share.campaign_id", 
                "Shows every platform a campaign has been shared on.", 
                "Platform data is stored in campaign_share, not in campaigns — JOIN links them by campaign_id.", ""),

            '9': ("Total Campaign Funds", 
                "SELECT campaigns.title, SUM(donations.amount) AS total_raised FROM campaigns, donations WHERE campaigns.campaign_id = donations.campaign_id GROUP BY campaigns.campaign_id, campaigns.title", 
                "Calculates the total donations received for each campaign.", 
                "Donations contain amounts and campaigns contain titles — combining them allows aggregation per campaign.", "Grouped so that totals are calculated per campaign instead of across all campaigns."),

            '10': ("Organizer Message Digest", 
                "SELECT campaigns.title, donations.message FROM campaigns, donations WHERE donations.campaign_id = campaigns.campaign_id AND campaigns.organizer_id = 1", 
                "Shows all donation messages for every campaign owned by a specific organizer.", 
                "Messages are in donations, campaign titles are in campaigns — JOIN links them by campaign_id.", "")
        }

        if query_id not in QUERIES:
            return jsonify({'error': 'Query not found'}), 404
        
        label, sql, scenario, why_join, why_groupby = QUERIES[query_id]
        db_conn = db.get_db()

        try:
            if any(re.search(r'\b' + cmd + r'\b', sql.upper()) for cmd in ["INSERT", "UPDATE", "DELETE"]):
                db_conn.execute(sql)
                db_conn.commit()
                return jsonify({
                    'label': label, 
                    'sql': sql, 
                    'scenario': scenario, 
                    'why_join': why_join,
                    'why_groupby' : why_groupby,
                    'rows': []
                })
            
            rows = db_conn.execute(sql).fetchall()
            return jsonify({
                'label': label, 
                'sql': sql, 
                'scenario': scenario, 
                'why_join': why_join,
                'why_groupby' : why_groupby,
                'rows': [dict(r) for r in rows]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # --- Edge cases route ---
    @app.route('/edge-cases')
    def edge_cases():
        return render_template('edge_cases.html')

    @app.route('/api/edge/<case>', methods=['POST'])
    def run_edge_case(case):
        db_conn = db.get_db()
        try:
            if case == 'duplicate_email':
                db_conn.execute("""INSERT INTO users (first_name, last_name, email, password_hash, role)
                                VALUES ('Test','User','duplicate@test.com','hash','user')""")
                db_conn.execute("""INSERT INTO users (first_name, last_name, email, password_hash, role)
                                VALUES ('Test2','User2','duplicate@test.com','hash','user')""")
                db_conn.commit()

            elif case == 'invalid_role':
                db_conn.execute("""INSERT INTO users (first_name, last_name, email, password_hash, role)
                                VALUES ('Bad','User','bad@test.com','hash','superadmin')""")
                db_conn.commit()

            elif case == 'negative_donation':
                db_conn.execute("""INSERT INTO donations (donation_id, amount, payment_status)
                                VALUES (9999, -50.00, 'pending')""")
                db_conn.commit()

            elif case == 'bad_date':
                db_conn.execute("""INSERT INTO campaigns 
                                (organizer_id, title, description, funding_goal, start_date, end_date)
                                VALUES (1,'Bad Campaign','Test',500,'2026-12-01','2026-01-01')""")
                db_conn.commit()

            elif case == 'orphan_campaign':
                db_conn.execute("""INSERT INTO campaigns (organizer_id, title, description, funding_goal, end_date)
                    VALUES (99999, 'Ghost', 'Test', 500, '2027-01-01')""")
                db_conn.commit()

            elif case == 'delete_with_deps':
                db_conn.execute("INSERT OR IGNORE INTO users (user_id, first_name, last_name, email, password_hash, role) VALUES (777, 'Dep', 'User', 'dep@test.com', 'hash', 'user')")
                db_conn.execute("INSERT OR IGNORE INTO campaigns (organizer_id, title, description, funding_goal, end_date) VALUES (777, 'Dep Campaign', 'Test', 100, '2027-01-01')")
                db_conn.commit()
                db_conn.execute("DELETE FROM users WHERE user_id = 777")
                db_conn.commit()

            return jsonify({'status': 'FAILED', 'note': 'Constraint should have blocked this!'})

        except sqlite3.IntegrityError as e:
            db_conn.rollback()
            return jsonify({'status': 'HANDLED', 'error': str(e),
                            'explanation': f'SQLite enforced the constraint for case: {case}'})
    
    # --- Business rules route ---
    @app.route('/business-rules')
    def business_rules():
        return render_template('business_rules.html')

    # import database 
    db.init_app(app)



    return app