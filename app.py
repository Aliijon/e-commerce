from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from config import Config
from extensions import db, login_manager, migrate, init_login_manager
from translations import translations
from models import Product

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

    return app

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