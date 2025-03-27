from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, LoginManager
from config import Config
from extensions import db, migrate, login_manager, init_login_manager
from translations import translations
from models import Product, User
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    init_login_manager()

    with app.app_context():
        # Import models
        from models import User, Product, Order, OrderItem, Favorite
        
        # Import blueprints
        from auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        # Import routes
        from routes import init_routes
        init_routes(app)

        # Create tables
        db.create_all()

        # Add sample data if the database is empty
        if not Product.query.first():
            add_sample_data()

    return app

def add_sample_data():
    # Sample products data
    products = [
        {
            'name': 'sports_shoe_1',
            'description': 'High quality sports shoe',
            'price': 89.99,
            'stock': 10,
            'image_url': 'images/IMG-20241118-WA0023.jpg',
            'category': 'shoes'
        },
        {
            'name': 'sports_shoe_2',
            'description': 'Professional running shoe',
            'price': 129.99,
            'stock': 8,
            'image_url': 'images/IMG-20241118-WA0017.jpg',
            'category': 'shoes'
        },
        {
            'name': 'sports_shirt_1',
            'description': 'Breathable sports shirt',
            'price': 34.99,
            'stock': 15,
            'image_url': 'images/IMG-20241014-WA0032.jpg',
            'category': 'clothing'
        },
        # Add more sample products as needed
    ]

    for product_data in products:
        product = Product(**product_data)
        db.session.add(product)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sample data: {e}")

app = create_app()

# Language support
def get_language():
    return session.get('language', 'en')

def get_translation(key):
    try:
        lang = get_language()
        keys = key.split('.')
        value = translations[lang]
        for k in keys:
            value = value[k]
        return value
    except (KeyError, AttributeError):
        # If key not found in current language, try English, then return the key itself
        try:
            value = translations['en']
            for k in keys:
                value = value[k]
            return value
        except (KeyError, AttributeError):
            return key

# Make translation function available to templates
@app.context_processor
def utility_processor():
    return {
        'get_translation': get_translation,
        't': get_translation  # Add a shorter alias
    }

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 