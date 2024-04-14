from flask import Flask, render_template,session
from flask_migrate import Migrate
app=Flask( __name__)



import config
import models
import routes

if __name__=='__main__':
    app.run(debug=True) 

