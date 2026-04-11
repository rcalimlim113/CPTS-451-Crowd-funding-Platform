import os
from flask import Flask, request, render_template
from . import db

#app = Flask(__name__)

def create_app(test_config=None):
    app = Flask(__name__)

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

    
    # load hello.html page
    @app.route("/")
    def hello():
        return render_template('hello.html')

    # load tempName.html page
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            name = request.form['username']
            return f"Hello {name}, POST request received"
        return render_template('tempName.html')


    # import database 
    db.init_app(app)



    return app

