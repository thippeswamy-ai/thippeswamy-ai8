import os
from flask import Flask, render_template
from models.db_helper import init_db, seed_sample_data
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college_lost_and_found_secret_key_2026')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit
    
    db_path = os.path.join(app.root_path, 'database.db')
    app.config['DATABASE'] = db_path

    # Ensure uploads directory exists
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    # Initialize DB if not present
    if not os.path.exists(db_path):
        with app.app_context():
            init_db(db_path)
            seed_sample_data(db_path)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting College Lost Things and Found System server...")
    print("Default Admin Credentials: Username -> 'admin', Password -> 'admin123'")
    app.run(host='0.0.0.0', port=5000, debug=True)
