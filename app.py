from flask import Flask, render_template, url_for, redirect, flash,request,session,abort
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from extensions import db
from database import *
import os
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "instance","database.db")
app.config['SECRET_KEY'] = 'thisisasecretkey'

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin_logged_in'):
            return f(*args, **kwargs)
        return abort(401)
    return decorated_function

#<!------------------------- Store Landing Page ------------------------->

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html',products=products)

#<!------------------------- User Login/Logout/Register Page ------------------------->

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_messages = []
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                session['user_id'] = user.id
                return redirect(url_for('user_dashboard'))
            else:
                error_messages.append('Wrong credentials! Please try again.')
        else:
            error_messages.append('Username does not exist.')

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.clear() 
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password,email=form.email.data,address=form.address.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    category_id = request.args.get('category_id')
    if category_id:
        selected_category = Category.query.get(category_id)
        if selected_category:
            products = selected_category.products
        else:
            products = []
    else:
        products = Product.query.all()
    categories = Category.query.all()
    return render_template('shop.html', categories=categories, products=products)



#<!------------------------- User's Dashbaord ------------------------->
@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    category_id = request.args.get('category_id')
    if category_id:
        selected_category = Category.query.get(category_id)
        if selected_category:
            products = selected_category.products
        else:
            products = []
    else:
        products = Product.query.all()
    categories = Category.query.all()
    return render_template('user_dashboard.html', categories=categories, products=products)

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.address.data = current_user.address
    return render_template('update_profile.html', form=form)

@app.route('/category')
def get_category():
    category_id = request.args.get('id', type=int)
    if category_id:
        category = Category.query.get_or_404(category_id)
        products = category.products
    else:
        products = []
    categories = Category.query.all()
    return render_template('category_products.html', categories=categories, products=products)

@app.route('/search')
def search_items():
    query = request.args.get('q')
    if not query:
        return render_template("user_dashboard.html")
    results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('search.html', products=results)

@app.route('/add_to_cart/<int:product_id>/<int:quantity>')
@login_required
def add_to_cart(product_id, quantity):
    user_id = session.get('user_id')
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return redirect(url_for('view_cart'))


#<!------------------------- Cart Functionalities ------------------------->
@app.route('/view_cart', methods=['GET', 'POST']) 
def view_cart():
    if request.method == 'POST':
        user_id = session.get('user_id')
        cart_items = Cart.query.filter_by(user_id=user_id).all()

        for item in cart_items:
            quantity_key = f"quantity{item.product.id}"
            new_quantity = int(request.form.get(quantity_key, 0))
            if 1 <= new_quantity <= item.product.stock:
                item.quantity = new_quantity

        db.session.commit()

    user_id = session.get('user_id')
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return render_template('view_cart.html', cart_items=cart_items)

@app.route('/empty_cart', methods=['POST'])
@login_required
def empty_cart():
    user_id = session.get('user_id')
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/update_cart_item/<int:product_id>', methods=['POST'])
@login_required
def update_cart_item(product_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item:
            new_quantity = int(request.form.get(f'quantity{product_id}', 0))
            if 1 <= new_quantity <= cart_item.product.stock:
                cart_item.quantity = new_quantity
                db.session.commit()

    return redirect(url_for('view_cart'))


@app.route('/delete_cart_item/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_cart_item(product_id):
    user_id = session.get('user_id')
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('view_cart'))

#<!------------------------- Payment Page ------------------------->
@app.route('/payment')
def payment():
    user_id = session.get('user_id')
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_amount=0
    for item in cart_items:
        total_amount+= item.product.price*item.quantity
    return render_template('payment.html',total_amount=total_amount)

@app.route('/order_placed')
@login_required
def order_placed():
    user_id = session.get('user_id')
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    total_amount = 0
    for item in cart_items:
        total_amount += item.product.price * item.quantity
    new_order = Order(user_id=user_id, total_amount=total_amount)
    db.session.add(new_order)
    db.session.commit()
    
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()

    return render_template('order_placed.html')


#<!------------------------- Admin Login ------------------------->
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin.html')

#<!------------------------- Admin's Dashboard ------------------------->
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

#<!------------------------- Category Management ------------------------->
@app.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category')
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
                flash('Category added successfully.', 'success')
                return redirect(url_for('add_products'))
            else:
                flash('Category already exists.', 'danger')
        else:
            flash('Invalid category name.', 'danger')
    return render_template('add_category.html')

@app.route('/update_category/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = UpdateCategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully.', 'success')
        return redirect(url_for('categories'))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('update_category.html', form=form, category=category)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    for product in category.products:
        db.session.delete(product)
    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully.', 'success')
    return redirect(url_for('categories'))

#<!------------------------- Product Management ------------------------->
@app.route('/products', methods=['GET', 'POST'])
@admin_required
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/add_products', methods=['GET', 'POST'])
@admin_required
def add_products():
    form = AddProducts()
    if form.validate_on_submit():
        selected_category_id = form.category.data
        category = Category.query.get(selected_category_id)
            
        if not category:
            category_name = form.category.choices[int(selected_category_id)][1]
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        new_product = Product(
        name=form.name.data,
        price=form.price.data,
        stock=form.stock.data,
        description=form.description.data,
        category=category
        )
        db.session.add(new_product)
        flash('Product added successfully.', 'success')

        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_products.html', form=form)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddProducts(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.description = form.description.data
        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('products'))
    return render_template('update_product.html', form=form, product=product)

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('products'))


#<!------------------------- Api ------------------------->

from api import api_blueprint
app.register_blueprint(api_blueprint)




with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)