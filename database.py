from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField,HiddenField,SelectField,FieldList
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired,Email
from datetime import datetime
from extensions import db

from flask import make_response
from werkzeug.exceptions import HTTPException
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})
    email = StringField(validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder": "Email Address"})
    address = StringField(validators=[InputRequired(), Length(min=4, max=255)], render_kw={"placeholder": "Address"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=4, max=255)])
    submit = SubmitField('Update Profile')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {'error_code': error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(message), status_code)


class AddProducts(FlaskForm):
    id = HiddenField()
    name = StringField(validators=[InputRequired()], render_kw={"placeholder": "Product's Name"})
    price = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Product's Price"})
    stock = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Quantity"})
    description = StringField(validators=[InputRequired()], render_kw={"placeholder": "Product's Description"})
    category = SelectField(validators=[InputRequired()], render_kw={"placeholder": "Select a category"})

    def __init__(self, *args, **kwargs):
        super(AddProducts, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]
        self.category.choices.insert(0, ("", "Select a category"))

class UpdateCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Update')


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref='carts', primaryjoin='Cart.product_id == Product.id')
    user = db.relationship('User', backref='carts', primaryjoin='Cart.user_id == User.id')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)



