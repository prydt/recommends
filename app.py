from flask import Flask, session
from flask_login import LoginManager
import sqlite3

app = Flask(__name__)
#TODO make an ENV var
app.secret_key = b'5cc3b1d033e1c56c84376684a9a6122de864f1cd5da93f540e127e0a0caf2e1e'

login_manager = LoginManager()
login_manager.init_app(app)

con = sqlite3.connect('recommends.db')
cur = sqlite.cursor()

@login_manager.user_loader
def load_user(user_id):
    cur.execute('SELECT * FROM users WHERE id = ?', user_id)
    user = cur.fetchall()
    # TODO

@app.route('/login', methods=['GET', 'POST'])
def login():
    