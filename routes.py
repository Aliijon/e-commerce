from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from extensions import db, cache
from models import Product, Order, OrderItem, Favorite
from search_utils import search_engine

def init_routes(app):
    @app.route('/')
    @cache.cached(timeout=300)  # Cache for 5 minutes
    def index():
        # Get all products without pagination
        query = Product.query

        # Apply category filter if specified
        category = request.args.get('category', None)
        if category:
            query = query.filter_by(category=category)

        # Get all products at once
        products = query.all()
        
        # Get all unique categories for the sidebar
        categories = db.session.query(Product.category).distinct().all()
        categories = [cat[0] for cat in categories]
        
        favorite_ids = []
        if current_user.is_authenticated:
            favorite_ids = [f.product_id for f in current_user.favorites]
            
        return render_template('index.html', 
                             products=products, 
                             favorite_ids=favorite_ids,
                             categories=categories,
                             current_category=category)

    @app.route('/search')
    @cache.cached(timeout=60)  # Cache for 1 minute
    def search():
        query = request.args.get('q', '')
        if not query:
            return redirect(url_for('index'))

        # Get all products and update search index
        all_products = Product.query.all()
        search_engine.update_index(all_products)
        
        # Perform search
        products = search_engine.search(query)
        
        favorite_ids = []
        if current_user.is_authenticated:
            favorite_ids = [f.product_id for f in current_user.favorites]
        
        # Get categories for sidebar
        categories = db.session.query(Product.category).distinct().all()
        categories = [cat[0] for cat in categories]
        
        return render_template('search.html',
                             products=products,
                             favorite_ids=favorite_ids,
                             query=query,
                             categories=categories)

    @app.route('/cart')
    def cart():
        cart_items = []
        total = 0
        if 'cart' in session:
            for product_id, quantity in session['cart'].items():
                product = Product.query.get(int(product_id))
                if product:
                    item_total = product.price * quantity
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'total': item_total
                    })
                    total += item_total
        return render_template('cart.html', cart_items=cart_items, total=total)

    @app.route('/checkout')
    @login_required
    def checkout():
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty')
            return redirect(url_for('cart'))
            
        cart_items = []
        total = 0
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
                
        return render_template('checkout.html', cart_items=cart_items, total=total)

    @app.route('/cart/update/<int:product_id>', methods=['POST'])
    def update_cart(product_id):
        if 'cart' in session:
            quantity = request.form.get('quantity', type=int)
            if quantity and quantity > 0:
                session['cart'][str(product_id)] = quantity
                session.modified = True
                cache.clear()  # Clear cache when cart is updated
        return redirect(url_for('cart'))

    @app.route('/cart/remove/<int:product_id>')
    def remove_from_cart(product_id):
        if 'cart' in session:
            session['cart'].pop(str(product_id), None)
            session.modified = True
            cache.clear()  # Clear cache when cart is modified
        return redirect(url_for('cart'))

    @app.route('/favorites')
    @login_required
    def favorites():
        return render_template('favorites.html', favorites=current_user.favorites)

    @app.route('/toggle_favorite/<int:product_id>')
    @login_required
    def toggle_favorite(product_id):
        product = Product.query.get_or_404(product_id)
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if favorite:
            db.session.delete(favorite)
            flash('Removed from favorites')
        else:
            favorite = Favorite(user_id=current_user.id, product_id=product_id)
            db.session.add(favorite)
            flash('Added to favorites')

        db.session.commit()
        cache.clear()  # Clear cache when favorites are modified
        return redirect(request.referrer or url_for('index'))

    @app.route('/add_to_cart/<int:product_id>', methods=['POST'])
    def add_to_cart(product_id):
        if 'cart' not in session:
            session['cart'] = {}
        
        quantity = request.form.get('quantity', type=int, default=1)
        if quantity and quantity > 0:
            session['cart'][str(product_id)] = session['cart'].get(str(product_id), 0) + quantity
            session.modified = True
            cache.clear()  # Clear cache when cart is modified
        return redirect(url_for('cart'))

    @app.route('/place_order', methods=['POST'])
    @login_required
    def place_order():
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty')
            return redirect(url_for('cart'))
            
        try:
            # Create a new order
            order = Order(user_id=current_user.id)
            db.session.add(order)
            
            total_amount = 0
            # Add order items
            for product_id, quantity in session['cart'].items():
                product = Product.query.get(int(product_id))
                if product and product.stock >= quantity:
                    # Create order item
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity
                    )
                    db.session.add(order_item)
                    
                    # Update product stock
                    product.stock -= quantity
                    total_amount += product.price * quantity
                else:
                    db.session.rollback()
                    flash('Some items are no longer in stock')
                    return redirect(url_for('cart'))
            
            # Clear the cart
            session.pop('cart')
            
            # Commit the transaction
            db.session.commit()
            cache.clear()  # Clear cache when order is placed
            flash('Order placed successfully!')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while placing your order')
            return redirect(url_for('checkout')) 