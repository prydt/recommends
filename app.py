from flask import Flask, session, send_file, render_template
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import test_data

app = Flask(__name__)
#TODO make an ENV var
app.config['SECRET_KEY'] = b'5cc3b1d033e1c56c84376684a9a6122de864f1cd5da93f540e127e0a0caf2e1e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommends.db'

"""
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    hash = db.Column(db.Binary)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
"""


# main routes
@app.route('/')
def index():
    # serves main page
    return send_file("index.html")

@app.route('/<user_name>')
def user_page(user_name):
    # Serves a user's Recommends page
    return render_template("user_page.html.jinja", user_data=test_data.data)

# logouts user
@app.route('/logout')
@login_required
def logout():
    logout_user()

if __name__ == '__main__':
    app.run(debug=True)

    # TODO make sure a user can't make their username "login", "logout", "signup", "static", "data", or any other url used specifically by the server
