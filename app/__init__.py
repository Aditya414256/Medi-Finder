import os
from flask import Flask, render_template, jsonify
from config import config_by_name
from app.extensions import db, migrate, login_manager
from app.models.user import User
from app.utils.helpers import humanize_time_ago
from app.services.notification_service import NotificationService

def create_app(config_name: str = 'development') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Ensure upload directories exist
    os.makedirs(app.config['PRESCRIPTIONS_DIR'], exist_ok=True)
    os.makedirs(app.config['VERIFICATION_DOCS_DIR'], exist_ok=True)

    # Template filters and global helpers
    @app.template_filter('time_ago')
    def filter_time_ago(dt):
        return humanize_time_ago(dt)

    @app.template_filter('format_currency')
    def filter_format_currency(val):
        try:
            return f"${float(val):.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.context_processor
    def inject_global_vars():
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = NotificationService.get_unread_count(current_user.id)
        return {
            'unread_notifications_count': unread_count,
            'app_name': 'MediFind'
        }

    # Register Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.customer import customer_bp
    from app.blueprints.pharmacy import pharmacy_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        if app.template_folder:
            return render_template('errors/400.html', error=e), 400
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', error=e), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', error=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', error=e), 500

    return app
