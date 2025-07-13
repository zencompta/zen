import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.audit_projects import audit_projects_bp
from src.routes.admin import admin_bp
from src.routes.data_import import data_import_bp
from src.routes.reports import reports_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'zencompta-secret-key-2024-ultra-secure'

# Configuration CORS pour permettre les requêtes depuis le frontend
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://127.0.0.1:5173']# Enregistrement des blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(audit_projects_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(data_import_bp, url_prefix='/api/data')
app.register_blueprint(reports_bp, url_prefix='/api/reports') Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Créer les tables
with app.app_context():
    db.create_all()
    
    # Créer un utilisateur admin par défaut s'il n'existe pas
    from src.models.user import User
    admin_user = User.query.filter_by(email='admin@zencompta.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@zencompta.com',
            first_name='Admin',
            last_name='ZenCompta',
            company='ZenCompta',
            role='admin',
            email_verified=True
        )
        admin_user.set_password('Admin123!')
        db.session.add(admin_user)
        db.session.commit()
        print("Utilisateur admin créé: admin@zencompta.com / Admin123!")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
