from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from datetime import datetime
import json
import os

# Load configuration from config.json
with open('config.json', 'r') as file:
    config_data = json.load(file)
    params = config_data["params"]

# Flask app setup
app = Flask(__name__)
app.secret_key = "super-secret-key"

# MongoDB configuration
app.config["MONGO_URI"] = params["mongo_uri"]
mongo = PyMongo(app)

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

# MongoDB Collections
users_collection = mongo.db.users
products_collection = mongo.db.products
contacts_collection = mongo.db.contacts

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})

# Home route
@app.route('/')
def home():
    products = list(products_collection.find())
    return render_template('index.html', products=products)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({"username": username})
        if user and password == params['admin_password']:
            login_user(UserMixin())
            session['user'] = username
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
    products = list(products_collection.find())
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
            new_product = {
                "p_name": name,
                "p_price": price,
                "p_details": details,
                "slug": slug,
                "img_file": filename
            }
            products_collection.insert_one(new_product)
            flash("Product added successfully!", "success")
            return redirect(url_for('dashboard'))

    return render_template('admin_dashboard.html')

# Edit product route
@app.route('/admin/edit/<string:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        details = request.form['details']
        file = request.files.get('img_file')

        update_data = {
            "p_name": name,
            "p_price": price,
            "p_details": details
        }
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_data["img_file"] = filename

        products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        flash("Product updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_product.html', product=product)

# Delete product route
@app.route('/admin/delete/<string:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    products_collection.delete_one({"_id": ObjectId(product_id)})
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
    product = products_collection.find_one({"slug": slug})
    if request.method == 'POST':
        flash(f"{product['p_name']} added to cart!", "success")
        return redirect(url_for('product_page', slug=slug))
    return render_template('product.html', product=product)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_no = request.form.get('phone')
        msg = request.form.get('message')
        date = datetime.now().strftime("%Y-%m-%d")

        contact = {
            "name": name,
            "email": email,
            "phone_no": phone_no,
            "msg": msg,
            "date": date
        }
        contacts_collection.insert_one(contact)
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
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total_price = sum(float(item['price']) * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
