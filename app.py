from flask import Flask, session, send_file, request, flash, redirect, render_template
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
import markupsafe
import nacl.pwhash
import json

app = Flask(__name__)
#TODO make an ENV var
app.config['SECRET_KEY'] = b'5cc3b1d033e1c56c84376684a9a6122de864f1cd5da93f540e127e0a0caf2e1e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommends.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

RESTRICTED_NAMES = {'login', 'logout', 'signup', 'static', 'data', 'edit'}

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('login.html.jinja', signup=True)

    username = request.form['uname']
    password = bytes(request.form['psw'], 'utf-8')
    user = Users.query.filter_by(username=username).first()
    if user is not None:
        # if user exists already: error
        return render_template('login.html.jinja', signup=True, error='error: the username is taken')

    if username in RESTRICTED_NAMES:
        return render_template('login.html.jinja', signup=True, error='error: the username is restricted')

    new_user = Users(username=username, hash=nacl.pwhash.str(password), data=json.dumps({}))
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect(f'/{username}')
    

# main routes
@app.route('/')
def index():
    # serves main page
    return send_file("index.html")

@app.route('/<user_name>')
def user_page(user_name):
    # Serves a user's Recommends page

    user = Users.query.filter_by(username=user_name).first_or_404(description='invalid username!')

    editable = False
    if current_user.is_authenticated and current_user == user:
        editable = True

    return render_template("user_page.html.jinja", user_data=json.loads(user.data), username=user_name, editable=editable, is_editing=False)

@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit_user_page():
    # Edit a user's own Recommends page

    if request.method == "GET":
        return render_template("user_page.html.jinja", user_data=json.loads(current_user.data), username=current_user.username, is_editing=True)
    else:
        data = request.get_json(silent=True)

        # Validate data
        if data and \
        "hue" in data and type(data["hue"]) is int and \
        "recommendationCategories" in data and type(data["recommendationCategories"]) is list and \
        "recommendations" in data and type(data["recommendations"]) is list and \
        len(data["recommendationCategories"]) == len(data["recommendations"]):

            for i in range(len(data["recommendations"])):
                if type(data["recommendationCategories"][i]) is not str or type(data["recommendations"][i]) is not list:
                    print("bad data")
                    return "<p>invalid data</p>"

                data["recommendationCategories"][i] = str(markupsafe.escape(markupsafe.Markup(data["recommendationCategories"][i]).unescape())).strip("\n")

                for j in range(len(data["recommendations"][i])):
                    if type(data["recommendations"][i][j]) is not str:
                        print("bad data")
                        return "<p>invalid data</p>"

                    data["recommendations"][i][j] = str(markupsafe.Markup(markupsafe.Markup(data["recommendations"][i][j]).unescape())).strip("\n")
                
            current_user.data = json.dumps(data)
            db.session.commit()
            return "<p>editing complete</p>"

        print("bad data")
        return "<p>invalid data</p>"


# logouts user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)