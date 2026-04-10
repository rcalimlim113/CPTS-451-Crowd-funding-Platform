from flask import Flask, request, render_template
#from . import database

#app = Flask(__name__)

def create_app():
    app = Flask(__name__)
    

    @app.route("/")
    def hello():
        return render_template('hello.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            name = request.form['username']
            return f"Hello {name}, POST request received"
        return render_template('tempName.html')

    if __name__ == '__main__':
        app.run(debug=True)


    # import database 
    from . import db
    db.init_app(app)

    return app

