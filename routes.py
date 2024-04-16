from flask import render_template, request, url_for, flash, redirect,session
from app import app  # Assuming your Flask app instance is named 'app'
from models import db, User,Genre,Book,BookRequest,Feedback
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from functools import wraps
from datetime  import datetime



def is_admin():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_admin:
            return True
    return False

    
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
        return redirect(url_for('login'))
    
    user=User.query.get(session['user_id'])
    if not check_password_hash (user.passhash,cpassword):
        flash ("Password is incorrect","danger")
        return redirect(url_for('login'))
    
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
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    genres=Genre.query.all()
    
    approved_requests = BookRequest.query.filter(BookRequest.status == 'approved').join(Book).join(User).all()
    book_requests = BookRequest.query.join(Book).join(User).all()
    pending_book_requests = BookRequest.query.filter(BookRequest.status == 'pending').join(Book).join(User).all()
    approved_book_requests = BookRequest.query.filter(BookRequest.status == 'approved').join(Book).join(User).all()
    return render_template('admin.html', genres=genres, book_requests=pending_book_requests,
                           approved_requests=approved_book_requests)


@app.route('/genre/add')
def  add_genre():
    if not is_admin():
        flash('Access denied: You must be an admin to view this page.')
        return redirect(url_for('profile'))
    return  render_template('genre/add.html')


@app.route('/genre/add', methods=["POST"])
def  add_genre_post():
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    name=request.form['name']
    if not name:
        flash('Please fill out all fields')
        return  redirect(url_for('add_genre'))
    genres=Genre(genrename=name)
    db.session.add(genres)
    db.session.commit()
    flash('New Genre added Successfully','success')
    return  redirect(url_for('admin'))



@app.route('/genre/<int:id>/')
def show_genre(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    genre = Genre.query.filter_by(id=id).first()
    if not genre :
        flash('This genre does not exist ')
        return redirect(url_for('admin'))
    return  render_template('genre/show.html',genre=genre)

@app.route('/genre/<int:id>/edit')
def edit_genre(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    genre=Genre.query.get(id)
    if not  genre:
        flash  ('Error: Genre does not exist')
        return  redirect ( url_for('admin') )
    return render_template('genre/edit.html',genre=genre)
    #return render_template ('genre/edit.html')


@app.route('/genre/<int:id>/edit',methods = ['POST'])
def edit_genre_post(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    genre=Genre.query.get(id)
    if not  genre:
        flash  ('Error: Genre does not exist')
        return  redirect ( url_for('admin') )
    name=request.form['name']
    if  not name :
        flash('Please enter the field')
        return  redirect(url_for('edit_genre', id = genre.id))
    genre.genrename=name
    db.session.commit()
    flash('The Genre has been Updated successfully')
    return  redirect(url_for('admin'))
    #return  redirect(url_for('show_genre',id=genre.id))


@app.route('/genre/<int:id>/delete')
def delete_genre(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.', 'danger'");
        return redirect(url_for('profile'));
    genre=Genre.query.get(id)
    if not  genre:
        flash   ("Error: Genre doesn't exists")
        return   redirect(url_for("admin"))
    return render_template ('genre/delete.html', genre=genre)



@app.route('/genre/<int:id>/delete',methods=["POST"])
def delete_genre_post(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.', 'danger'");
        return redirect(url_for('profile'));
    genre=Genre.query.get(id)
    if not  genre:
        flash   ("Error: Genre doesn't exists")
        return   redirect(url_for("admin"))
    db.session.delete(genre)
    db.session.commit()
    flash   ("Successfully deleted!")
    return   redirect(url_for("admin"))



@app.route('/book/add/<int:genre_id>')
def  add_book(genre_id):
    if not is_admin():
        flash('Access denied: You must be an admin to view this page.')
        return redirect(url_for('profile'))
    genres=Genre.query.all()
    genre=Genre.query.get(genre_id)
    if  not genre:
        flash( "Error: The selected genre does not exist.")
        return redirect( url_for('admin'))
    return render_template('books/add.html',genre=genre,genres=genres)


    
@app.route('/book/add/', methods=["POST"])
def  add_book_post():
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.");
        return redirect(url_for('profile'));
    title=request.form.get('title')
    price=request.form.get('price')
    author=request.form.get('author')
    booksnum=request.form.get('booksnum')
    genre_id=request.form.get('genre_id')
    content = request.form.get('content')
    pubdate= request.form.get('pubdate')
    try:
        price = float(price)  # Convert price to float
        pubdate = datetime.strptime(pubdate, '%Y-%m-%d')  # Convert string to datetime
    except ValueError:
        flash("Invalid input for price or publication date.")
        return redirect(url_for('add_book', genre_id=genre_id))
    genre=Genre.query.get(genre_id)
    if not  genre :
        flash("Genre does not exist")
        return redirect(url_for('admin'))

    if not title or  not price or not  author or not pubdate:
        flash('Please fill out all fields')
        return redirect(url_for('add_book', genre_id = genre_id))
    
    book=Book(title=title,price=price,author=author,booksnum=booksnum,genre=genre,pubdate=pubdate,content=content)
    db.session.add(book)
    db.session.commit()
    flash ('Book added!','success')
    return redirect(url_for('admin'))
    #return redirect (url_for('show_genre', genre_id=genre.id))


@app.route('/add_feedback', methods=['POST'])
def add_feedback():
    book_id = request.form['book_id']
    comment = request.form['comment']
    rating = int(request.form['rating'])  # Get the rating as an integer

    # Validate the rating
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.')
        return redirect(url_for('books'))

    if book_id and comment and rating:
        feedback = Feedback(book_id=book_id, comment=comment, rating=rating)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback and rating added successfully.')
    else:
        flash('Error adding feedback and rating.')
    return redirect(url_for('books'))




@app.route('/book/<int:id>/update')
def edit_book(id):
    book = Book.query.get_or_404(id)
    return render_template('books/updatebook.html', book=book)

@app.route('/book/<int:id>/update', methods=['POST'])
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.price = float(request.form['price'])
        book.pubdate = datetime.strptime(request.form['pubdate'], '%Y-%m-%d')

        try:
            db.session.commit()
            flash('Book successfully updated.', 'success')
        except:
            db.session.rollback()
            flash('Error updating book.', 'danger')

        return redirect(url_for('update_book', id=id))
    return render_template('books/show.html', book=book)



@app.route('/book/<int:id>/delete')
def delete_book(id):
    if not is_admin():
        flash("Access denied: You must be an admin to view this page.', 'danger'");
        return redirect(url_for('profile'));
    book=Book.query.get(id)
    if not  book:
        flash   ("Error: Genre doesn't exists")
        return   redirect(url_for("admin"))
    return render_template ('books/deletebook.html', book=book)


@app.route('/book/delete/<int:id>', methods=['POST'])
def delete_book_post(id):
    if not is_admin():
        flash("Access denied: You must be an admin to perform this action.", 'danger')
        return redirect(url_for('profile'))

    book = Book.query.get_or_404(id)  # This will automatically return a 404 error page if not found
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')

    return redirect(url_for('admin'))

    

#--- user routes


@app.route('/')
def index():
    # Check if 'user_id' is in the session
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return render_template('admin.html')
    genres = Genre.query.all()
    parameter=request.args.get('genre')
    query=request.args.get('query')

    return render_template('index.html', genres=genres)

    
    
@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in

    book = Book.query.get(book_id)
    if not book:
        flash('Error: Book doesn\'t exist.', 'danger')
        return redirect(url_for('index'))

    booksnum = request.form.get('booksnum')
    try:
        booksnum = int(booksnum)
    except ValueError:
        flash('Error: You must enter a number.', 'danger')
        return redirect(url_for('index'))

    if booksnum <= 0 or booksnum > book.booksnum:
        flash('Error: You must enter a number greater than 0 and less than or equal to the number of books in stock.', 'danger')
        return redirect(url_for('index'))

    cart = Cart.query.filter_by(user_id=session['user_id'], book_id=book_id).first()
    if cart:
        if cart.booksnum + booksnum > book.booksnum:
            flash('Error: You must enter a number less than or equal to the number of books in stock.', 'danger')
            return redirect(url_for('index'))
        cart.booksnum += booksnum
    else:
        cart = Cart(user_id=session['user_id'], book_id=book_id, booksnum=booksnum)
        db.session.add(cart)

    db.session.commit()
    flash('Book added to cart.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    selected_genre_id = request.args.get('genre_id')
    if selected_genre_id:
        books = Book.query.filter_by(genre_id=selected_genre_id).all()
    else:
        books = Book.query.all()

    # Fetch books that are associated with approved requests
    approved_books = Book.query.join(BookRequest).filter(BookRequest.status == 'approved').all()

    genres = Genre.query.all()

    return render_template('dashboard.html', books=books, approved_books=approved_books, genres=genres, selected_genre_id=selected_genre_id)



@app.route('/request-book', methods=['POST'])
def request_book():
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    book_id = request.form.get('book_id')
    user_id = 1  # Replace with session or authentication mechanism to get the current user's ID

    if book_id is None or user_id is None:
        flash('Invalid request.')
        return redirect(url_for('dashboard'))

    new_request = BookRequest(user_id=user_id, book_id=book_id)
    db.session.add(new_request)
    db.session.commit()
    flash('Book request sent successfully!')
    return redirect(url_for('dashboard'))


@app.route('/approve_request/<int:request_id>')
def approve_request(request_id):
    if not is_admin():
        flash("Access denied: You must be an admin to perform this action.")
        return redirect(url_for('admin'))

    request = BookRequest.query.get_or_404(request_id)
    request.status = 'approved'  # This line updates the request status to approved
    db.session.commit()
    flash('Book request approved.')
    return redirect(url_for('admin'))

@app.route('/deny_request/<int:request_id>')
def deny_request(request_id):
    if not is_admin():
        flash("Access denied: You must be an admin to perform this action.")
        return redirect(url_for('admin'))

    request = BookRequest.query.get_or_404(request_id)
    request.status = 'denied'  # This line updates the request status to denied
    db.session.commit()
    flash('Book request denied.')
    return redirect(url_for('admin'))



@app.route('/end_access/<int:request_id>')
def end_access(request_id):
    if not is_admin():
        flash("Access denied: You must be an admin to perform this action.")
        return redirect(url_for('profile'))

    request = BookRequest.query.get_or_404(request_id)
    request.status = 'access ended'  # Update status or perform other logic
    db.session.commit()
    flash('Access for the book request has been ended.')
    return redirect(url_for('admin'))

    
@app.route('/read_book/<int:book_id>', methods=['GET', 'POST'])
def read_book(book_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        try:
            rating = float(request.form['rating'])
            book.rating = rating
            db.session.commit()
            flash('Thank you for your rating!', 'success')
        except ValueError:
            flash('Invalid input for rating. Please enter a valid number.', 'error')
        return redirect(url_for('read_book', book_id=book_id))
    
    return render_template('read_book.html', book=book)


@app.route('/view_content', methods=['POST'])
def view_content():
    content = request.form.get('content')
    return render_template('view_content.html', content=content)


@app.route('/submit_rating/<int:book_id>', methods=['POST'])
def submit_rating(book_id):
    rating = request.form.get('rating')
    # Assume you have a Book model and you fetch the book instance by id
    book = Book.query.get_or_404(book_id)
    book.rating = rating
    db.session.commit()
    flash('Thank you for your rating!', 'success')
    return redirect(url_for('read_book', book_id=book_id))


@app.route('/book_details/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('read_book.html', book=book)
