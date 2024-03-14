from flask import render_template, request, url_for, flash, redirect
from app import app  # Assuming your Flask app instance is named 'app'
from models import db
from models import  User
from werkzeug.security  import generate_password_hash, check_password_hash
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username=request.form.get("username")
    password = request.form.get('password')

    if  not username or  not password:
        error="Username and Password required"
        return  render_template("login.html")
    
    user=User.query.filter_by(username=username).first()

    if not user:
        error="No such user found"
        return  render_template("register.html")
    if  not check_password_hash(user.passhash, password):
        error="Invalid Password"
        return  render_template("login.html")
    return   render_template("index.html")



@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=["POST"])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    if not all([username, password, confirm_password]):
        flash("Please fill out the form completely")
        return redirect(url_for('register'))  # Import 'redirect' and 'url_for'
    if  password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('register'))
    
    user=User.query.filter_by(username=username).first()
    if user:   # A user with this username already exists
        flash ("Username already taken")
        return redirect(url_for('register'))
    
    passhash=generate_password_hash(password)
    new_user = User(username=username, passhash=passhash, name=name)
    db.session.add(new_user)      # Adds a new user to the database session
    db.session.commit()           # MAKE CHANGE IN DATA FILE
    return  redirect(url_for('login'))
