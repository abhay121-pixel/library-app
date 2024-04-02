from flask import render_template, request, url_for, flash, redirect,session
from app import app  # Assuming your Flask app instance is named 'app'
from models import db, User,Genre
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
@app.route('/')
def index():
    if 'user_id' in  session:
        return render_template('index.html')
    else:
        flash ("Please login first!", "danger")
        return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get("username")
    password = request.form.get('password')

    if not username or not password:
        error = "Username and Password required"
        return render_template('login.html', error=error)

    user = User.query.filter_by(username=username).first()

    if not user:
        error = "No such user found"
        return render_template("login.html", error=error)
    
    if not check_password_hash(user.passhash, password):
        error = "Invalid Password"
        return render_template("login.html", error=error)
    session['user_id']=user.id
    flash ("Logged In Successfully","success")
    return redirect(url_for('profile'))

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
        return redirect(url_for('register'))

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()
    if user:   # A user with this username already exists
        flash("Username already taken")
        return redirect(url_for('register'))
    
    passhash = generate_password_hash(password)
    new_user = User(username=username, passhash=passhash, name=name)
    db.session.add(new_user)      # Adds a new user to the database session
    db.session.commit()           # Commit the changes to the database
    
    flash("Registration successful. Please log in.")
    return redirect(url_for('login'))

#------
'''def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return func(*args, **kwargs)
        else:
            flash('Please log in to continue')
            return redirect(url_for('login'))
    return  wrapper'''

@app.route('/profile', methods=["GET"])
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return render_template('profile.html', user=user)
        else:
            flash("User not found", "danger")
            return redirect(url_for('login'))
    else: 
        flash("Please login first!", "danger")
        return redirect(url_for('login'))
@app.route('/profile',methods=["POST"])
def profile_post():
    username=request.form.get("username")
    cpassword=request.form.get("cpassword")
    password=request.form.get("password")
    name=request.form.get("name")

    if not  username or not cpassword or not password:
        flash("Missing fields", "warning")
        return redirect(url_for('profile'))
    
    user=User.query.get(session['user_id'])
    if not check_password_hash (user.passhash,cpassword):
        flash ("Password is incorrect","danger")
        return redirect(url_for('profile'))
    
    if username != user.username :
        new_username=User.query.filter_by(username=username).first()
        if new_username:
            flash("Username already exists","danger")
            return  redirect(url_for('profile'))
    new_password_hash=generate_password_hash(password)
    user.username=username
    user.passhash=new_password_hash
    user.username=name
    db.session.commit()
    flash('Profile updated successfully','success')
    return  redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)       # Removes the 'user_id' key from the session dictionary
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))
 # admin pages
@app.route('/admin')
def admin():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return render_template('admin.html')
        else:
            flash("Access denied: You must be an admin to view this page.", "danger")
            return redirect(url_for('profile'))
    else:
        flash("Please login first!", "danger")
        return redirect(url_for('login'))

@app.route('/genre/add')
def  add_genre():
    return  render_template('genre/add.html')

@app.route('/genre/add', methods=["POST"])
def  add_genre_post():
    name=request.form['name']
    if not name:
        flash('Please fill out all fields')
        return  redirect(url_for('add_genre'))
    genre=Genre(genrename=name)
    db.session.add(genre)
    db.session.commit()
    flash('New Genre added Successfully','success')
    return  redirect(url_for('admin'))



@app.route('/genre/<int:id>/')
def show_genre(id):
    return "show_genre"

@app.route('/genre/<int:id>/edit')
def edit_genre(id):
    return "edit_genre"

@app.route('/genre/<int:id>/delete')
def delete_genre(id):
    return "delete_genre"