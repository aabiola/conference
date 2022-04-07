from re import M
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,PasswordField

from wtforms.validators import DataRequired, Email,Length

class LoginForm(FlaskForm):
    username = StringField("Your email:", validators=[DataRequired(),Email()])  
    pwd = PasswordField("Enter Password:")
    
    loginbtn = SubmitField("Login")

class ContactusForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])  

    email = StringField("Your Email", validators=[Email()])

    message = TextAreaField("Message", validators=[DataRequired()]) 

    btn = SubmitField("Send")
    