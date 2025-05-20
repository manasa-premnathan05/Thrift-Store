
# Thrift Store E-Commerce Platform
A full-featured thrift store e-commerce web application built with Flask, MongoDB, and Bootstrap. This sustainable shopping platform allows users to browse second-hand products, add items to cart, and make purchases, while providing administrators with comprehensive product management capabilities.

## ✨ Features

### User Experience
- 🛍️ Product browsing with carousel and grid views
- 🔍 Product details pages
- 🛒 Shopping cart functionality
- 📱 Fully responsive design
- ✉️ Contact form with email notifications

### Admin Features
- 🔒 Secure admin authentication
- 📊 Product management dashboard
- ➕ Add/edit/delete products
- 📤 Image upload functionality

## 🛠️ Technologies Used

**Backend:**
- Python 3
- Flask
- Flask-PyMongo
- Flask-Login
- Flask-Mail

**Database:**
- MongoDB

**Frontend:**
- HTML5, CSS3, JavaScript
- Bootstrap 5
- Jinja2 templating

## 📂 Project Structure

```
thrift-store/
├── static/
│   ├── css/           # CSS files
│   ├── js/            # JavaScript files
│   └── images/        # Product images
├── templates/
│   ├── layout.html    # Base template
│   ├── index.html     # Home page
│   ├── shop.html      # Product listing
│   ├── product.html   # Single product
│   ├── cart.html      # Shopping cart
│   ├── contact.html   # Contact page
│   ├── about.html     # About page
│   ├── login.html     # Login page
│   ├── dashboard.html # Admin dashboard
│   └── ...            # Other templates
├── main.py            # Flask application
└── config.json        # Configuration file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- MongoDB
- Pip package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/thrift-store.git
   cd thrift-store
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure MongoDB:
   - Update `config.json` with your MongoDB URI
   - Set up email credentials for contact form

4. Run the application:
   ```bash
   python main.py
   ```

5. Access the application at `http://localhost:5000`

## 🌱 Sustainability Focus

This project promotes eco-friendly shopping by:
- ♻️ Giving pre-loved items a second life
- 🧵 Reducing textile waste
- 🌍 Supporting sustainable fashion



## 🙏 Acknowledgments
- Bootstrap 5 for responsive design
- Flask community for excellent documentation
- Unsplash for placeholder images
```

### Key Formatting Notes:
1. Used emojis for visual appeal and quick scanning
2. Added clear section headers with `##`
3. Included code blocks for installation instructions
4. Used lists for features and technologies
5. Added placeholder for project screenshot
6. Included clear project structure visualization
7. Added proper markdown syntax for code blocks and emphasis

You can customize this further by:
- Adding actual screenshots
- Including a demo link if hosted
- Adding contribution guidelines
- Expanding the features list
- Adding your personal information in an "About the Developer" section
