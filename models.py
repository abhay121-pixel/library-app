from  app import app
from flask_sqlalchemy import  SQLAlchemy
from sqlalchemy.orm import backref
from  werkzeug.security import generate_password_hash,check_password_hash



db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32),unique=True)
    passhash = db.Column(db.String(256),nullable=False)
    name=db.Column(db.String(64),nullable=True)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)

class Genre(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    genrename=db.Column(db.String(32),unique=True)
    books=db.relationship('Book',backref='genre' ,lazy='select')#lazy here we use bz when i will acces then give it not everytime
     
class Book(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    author=db.Column(db.String(30))
    price=db.Column(db.Float,nullable=False)
    genre_id=db.Column(db.Integer,db.ForeignKey("genre.id"),nullable=False)
    #publisher=db.Column(db.String(30))
    pubdate=db.Column(db.Date,nullable=False)
    #feedback=db.relationship("Feedback", backref="books_feedback_relationship",lazy=True)
    #bookcover=db.Column(db.LargeBinary)
    #summary=db.Column(db.Text)
    #pagecount=db.Column(db.Integer)
    #language=db.Column(db.String(8))
    #label=db.relationship("Label",uselist=False,backref=db.backref("book"))
    #genre=db.Column(db.Integer,db.ForeignKey('genre.id'))
    #user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    carts=db.relationship("Cart",backref='book',lazy='dynamic')
    orders=db.relationship("Order",backref='book',lazy='dynamic')
    #feedback = db.relationship("Feedback", back_populates="book", overlaps="books_feedback_relationship")

class Feedback(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    book_id=db.Column(db.Integer,db.ForeignKey('book.id'),nullable=False)
    text=db.Column(db.Text,nullable=False)
    rating=db.Column(db.SmallInteger,nullable=False)
    feed_book=db.relationship("Book",backref='book_feedback_relationship',lazy=True)
    #book = db.relationship("Book", back_populates="feedback", overlaps="books_feedback_relationship")
class Cart(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer,db.ForeignKey('book.id'),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)

class Transaction(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)  
    datetime=db.Column(db.DateTime,nullable=False)
    orders=db.relationship("Order",backref="transaction",lazy='dynamic') 

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    transaction_id=db.Column(db.Integer,db.ForeignKey('transaction.id'),nullable=False)
    book_id=db.Column(db.Integer,db.ForeignKey('book.id'),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    #status=db.Column(db.SmallString,nullable=False)#paied/unpaied/shipping/completed

    #items = db.relationship('orderItem', backref=backref('order', lazy=True), lazy=True)

with app.app_context():
    db.create_all()
    #if admin exists,else create admin
    admin=User.query.filter_by(is_admin=True).first()
    if  not admin:
       passhash=generate_password_hash('admin')
       admin=User(username='admin',passhash=passhash,name='Admin', is_admin=True)
       db.session.add(admin)
       db.session.commit()