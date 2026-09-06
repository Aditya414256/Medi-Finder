import os
from app import create_app
from app.extensions import db

env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"==================================================")
    print(f" MediFind Platform Server running on port {port}")
    print(f" Environment: {env} | Debug: {debug}")
    print(f" Visit: http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
