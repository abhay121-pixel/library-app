from flask import render_template,request,url_for,flash
from app import  app
from models import db
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login')
def login():
    return  render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/register',methods=["POST"])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name=request.form.get('name')
    return  "username:"+ username + "password:"+ password +"confirm_password:"+confirm_password+ "name:"+name