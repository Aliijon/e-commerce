from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, LoginManager
from config import Config
from extensions import db, migrate, login_manager, init_login_manager, cache
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
    
    # Cache configuration
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes default timeout
    cache.init_app(app)

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
            'name': 'Elite Pro Training Ball',
            'description': 'Professional-grade training ball with enhanced grip and durability.',
            'price': 29.99,
            'stock': 50,
            'category': 'equipment',
            'image_url': 'images/ball1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Performance Basketball',
            'description': 'Competition-level basketball with superior bounce and control.',
            'price': 34.99,
            'stock': 40,
            'category': 'equipment',
            'image_url': 'images/ball2.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Advanced Tennis Racquet',
            'description': 'Lightweight carbon fiber racquet for precise shots.',
            'price': 89.99,
            'stock': 25,
            'category': 'equipment',
            'image_url': 'images/racquet1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'PowerFit Dumbbell Set',
            'description': 'Adjustable weight set with ergonomic grip design.',
            'price': 149.99,
            'stock': 20,
            'category': 'equipment',
            'image_url': 'images/dumbbell1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Competition Volleyball',
            'description': 'Official match volleyball with enhanced durability.',
            'price': 39.99,
            'stock': 35,
            'category': 'equipment',
            'image_url': 'images/ball3.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Pro Resistance Kit',
            'description': 'Complete resistance training set with multiple tension levels.',
            'price': 49.99,
            'stock': 30,
            'category': 'equipment',
            'image_url': 'images/resistance1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Premium Yoga Set',
            'description': 'High-density mat with alignment markers and accessories.',
            'price': 79.99,
            'stock': 25,
            'category': 'equipment',
            'image_url': 'images/yoga1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Champion Boxing Kit',
            'description': 'Professional boxing gloves with hand wraps and protectors.',
            'price': 129.99,
            'stock': 15,
            'category': 'equipment',
            'image_url': 'images/boxing1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Speed Runner Elite',
            'description': 'Lightweight running shoes with advanced cushioning.',
            'price': 119.99,
            'stock': 30,
            'category': 'shoes',
            'image_url': 'images/shoes1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Aero Cycling Helmet',
            'description': 'Aerodynamic helmet with integrated ventilation system.',
            'price': 89.99,
            'stock': 20,
            'category': 'equipment',
            'image_url': 'images/helmet1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Pro Swim Goggles',
            'description': 'Competition swimming goggles with anti-fog coating.',
            'price': 29.99,
            'stock': 40,
            'category': 'equipment',
            'image_url': 'images/goggles1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Tournament Badminton Set',
            'description': 'Complete badminton set with premium racquets.',
            'price': 69.99,
            'stock': 25,
            'category': 'equipment',
            'image_url': 'images/badminton1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Master Table Tennis Kit',
            'description': 'Professional table tennis set with competition paddles.',
            'price': 79.99,
            'stock': 20,
            'category': 'equipment',
            'image_url': 'images/tabletennis1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Premium Golf Set',
            'description': 'Complete golf club set with premium bag.',
            'price': 499.99,
            'stock': 10,
            'category': 'equipment',
            'image_url': 'images/golf1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Speed Jump Rope Pro',
            'description': 'Professional jump rope with adjustable length.',
            'price': 19.99,
            'stock': 50,
            'category': 'equipment',
            'image_url': 'images/jumprope1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Mountain Bike Pro Helmet',
            'description': 'Advanced protection helmet for mountain biking.',
            'price': 99.99,
            'stock': 25,
            'category': 'equipment',
            'image_url': 'images/helmet2.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Climbing Safety Kit',
            'description': 'Complete climbing gear set with harness and carabiners.',
            'price': 199.99,
            'stock': 15,
            'category': 'equipment',
            'image_url': 'images/climbing1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Pro Skateboard Complete',
            'description': 'Professional skateboard with custom artwork.',
            'price': 89.99,
            'stock': 30,
            'category': 'equipment',
            'image_url': 'images/skateboard1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Yoga Wheel Pro',
            'description': 'Premium yoga wheel for advanced poses and stretching.',
            'price': 44.99,
            'stock': 35,
            'category': 'equipment',
            'image_url': 'images/yoga2.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Training Boxing Bag',
            'description': 'Heavy-duty boxing bag with wall mount kit.',
            'price': 149.99,
            'stock': 20,
            'category': 'equipment',
            'image_url': 'images/boxing2.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Trail Running Shoes',
            'description': 'All-terrain running shoes with enhanced grip.',
            'price': 129.99,
            'stock': 25,
            'category': 'shoes',
            'image_url': 'images/shoes2.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Competition Swim Cap',
            'description': 'Professional silicone swim cap with ergonomic fit.',
            'price': 14.99,
            'stock': 60,
            'category': 'equipment',
            'image_url': 'images/swimcap1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Elite Tennis Balls',
            'description': 'Professional tennis balls for tournament play.',
            'price': 9.99,
            'stock': 100,
            'category': 'equipment',
            'image_url': 'images/tennisballs1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Basketball Training Set',
            'description': 'Complete training kit with cones and agility ladder.',
            'price': 79.99,
            'stock': 25,
            'category': 'equipment',
            'image_url': 'images/basketball1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        },
        {
            'name': 'Soccer Goal Set',
            'description': 'Portable soccer goal with training net.',
            'price': 129.99,
            'stock': 20,
            'category': 'equipment',
            'image_url': 'images/soccer1.jpg',
            'whatsapp': '93771749100',
            'telegram': 'Alijanelyasi'
        }
    ]

    # Add products to database
    for product_data in products:
        product = Product.query.filter_by(name=product_data['name']).first()
        if not product:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()

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
        't': get_translation,  # Add a shorter alias
        'get_language': get_language  # Add get_language to template context
    }

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['language'] = lang
        # Clear cache when language changes
        cache.clear()
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 