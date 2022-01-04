from flask import Flask, session, send_file, request, flash, redirect, render_template
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
import nacl.pwhash
import json

app = Flask(__name__)
#TODO make an ENV var
app.config['SECRET_KEY'] = b'5cc3b1d033e1c56c84376684a9a6122de864f1cd5da93f540e127e0a0caf2e1e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommends.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    hash = db.Column(db.BINARY)
    data = db.Column(db.TEXT)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html.jinja')

    username = request.form['uname']
    password = bytes(request.form['psw'], 'utf-8')
    user = Users.query.filter_by(username=username).first()
    if user is None:
        return render_template('login.html.jinja', error='error: invalid username')

    try:
        if nacl.pwhash.verify(user.hash, password):
            pass
    except:
        return render_template('login.html.jinja', error='error: invalid password')
    
    # username and password are valid
    login_user(user)
    return redirect(f'/{user.username}')


# main routes
@app.route('/')
def index():
    # serves main page
    return send_file("index.html")

@app.route('/<user_name>')
def user_page(user_name):
    # Serves a user's Recommends page
    # TODO user_data = jsonified data from the database
    # TODO editable = True if user is logged in and viewing their own page

    user = Users.query.filter_by(username=user_name).first_or_404(description='invalid username!')

    editable = False
    if current_user.is_authenticated and current_user == user:
        editable = True

    return render_template("user_page.html.jinja", user_data=json.loads(user.data), username=user_name, editable=editable, is_editing=False)

@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit_user_page():
    # Edit a user's own Recommends page
    # TODO user_data = jsonified data from the database
    if request.method == "GET":
        return render_template("user_page.html.jinja", user_data=json.loads(current_user.data), username=current_user.username, is_editing=True)
    else:
        # TODO add the request data to the user's database entry
        # TODO redirect the user to their own page
        print(request.get_json())
        return "<p>editing complete</p>"

# logouts user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

    # TODO make sure a user can't make their username "login", "logout", "signup", "static", "data", or any other url used specifically by the server
