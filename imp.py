from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import pymysql
import json
import os

# Use pymysql for MySQL compatibility
pymysql.install_as_MySQLdb()

# Load configuration from config.json
with open('config.json', 'r') as file:
    config_data = json.load(file)
    params = config_data["params"]

# Flask app setup
app = Flask(__name__)
app.secret_key = "super-secret-key"

# MySQL database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/thrift_store"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)

# Mail configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'buyer', or 'donor'

# Product model
class Products(db.Model):
    p_no = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(80), nullable=False)
    p_price = db.Column(db.String(12), nullable=False)
    p_details = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    img_file = db.Column(db.String(20), nullable=True)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    products = Products.query.all()
    return render_template('index.html', products=products)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate credentials
        if username == params['admin_username'] and password == params['admin_password']:
            user = User.query.filter_by(username=username).first()

            if not user:
                # Create the admin user if it doesn't exist
                user = User(username=username, email="admin@example.com", password="admin", role='admin')
                db.session.add(user)
                db.session.commit()

            login_user(user)  # Log the user in with Flask-Login
            session['user'] = username  # Store username in session
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid username or password.", "danger")
    return render_template('login.html', params=params)

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user') != params['admin_username']:
        flash("Access denied. Please log in as admin.", "warning")
        return redirect(url_for('login'))

    products = Products.query.all()
    return render_template('dashboard.html', products=products)

# Add product route
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        details = request.form['details']
        slug = request.form['slug']
        file = request.files.get('img_file')

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_product = Products(p_name=name, p_price=price, p_details=details, slug=slug, img_file=filename)
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for('dashboard'))

    return render_template('admin_dashboard.html')

# Edit product route
@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)

    if request.method == 'POST':
        product.p_name = request.form['name']
        product.p_price = request.form['price']
        product.p_details = request.form['details']
        file = request.files.get('img_file')

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.img_file = filename

        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_product.html', product=product)

# Delete product route
@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

# Product Page Route
@app.route('/product/<string:slug>', methods=['GET', 'POST'])
def product_page(slug):
    print(f"Fetching product: {slug}")  # Debugging print
    product = Products.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        # Simulate adding the product to cart (or handle the form submission)
        print(f"Adding {product.p_name} to cart.")  # Debugging print
        flash(f"{product.p_name} added to cart!", "success")
        return redirect(url_for('product_page', slug=slug))  # Avoid direct render here

    return render_template('product.html', product=product)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phone')
        msg = request.form.get('message')
        date = datetime.now().strftime("%Y-%m-%d")

        entry = Contact(name=name, email=email, phone_no=phone_no, msg=msg, date=date)
        db.session.add(entry)
        db.session.commit()

        # Send an email (optional)
        mail.send_message(
            subject=f'New message from {name}',
            sender=email,
            recipients=[params['gmail-user']],
            html=f"""
            <h2>New Message from {name}</h2>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone_no}</p>
            <p><strong>Message:</strong> {msg}</p>
            """
        )
        flash("Message sent successfully!")
        return redirect(url_for('contact'))  # Refresh the page after submission

    return render_template('contact.html')


@app.route('/shop')
def shop():
    products = Products.query.all()  # Fetch all products from the database
    return render_template('shop.html', products=products)


@app.route('/about')
def about():
    return render_template('about.html')

# Sample cart data
cart_items = [
    {'product_id': 1, 'product_name': 'Nordic Chair', 'price': 50, 'quantity': 1, 'img_file': 'product-1.png'},
    {'product_id': 2, 'product_name': 'Kruzo Aero Chair', 'price': 75, 'quantity': 2, 'img_file': 'product-2.png'},
]


@app.route('/book_order')
def book_order():
    session.pop('cart', None)  # Clear the cart
    flash("Your order has been placed!", "success")
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Products.query.get_or_404(product_id)  # Get product by ID
    cart = session.get('cart', [])  # Retrieve cart from session or initialize empty list

    # Check if product is already in the cart, and update quantity if it exists
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        # If not in the cart, add it as a new item
        cart.append({
            'id': product.p_no,
            'name': product.p_name,
            'price': float(product.p_price),
            'image': product.img_file,
            'quantity': 1
        })

    # Save the updated cart back to the session
    session['cart'] = cart
    session.modified = True  # Ensure Flask detects session changes
    flash(f"{product.p_name} added to cart!", "success")

    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:p_no>', methods=['POST'], endpoint='remove_from_cart_2')
def remove_from_cart_alternate(p_no):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != p_no]
    session['cart'] = cart
    flash("Item removed from cart.", "success")
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart = session.get('cart', [])  # Retrieve cart from session, default to empty list
    # Calculate total price
    total_price = sum(float(item['price']) * item['quantity'] for item in cart)

    # Render the cart template with the cart items and total price
    return render_template('cart.html', cart=cart, total_price=total_price)


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
