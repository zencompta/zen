from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Valider le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valider la force du mot de passe"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, "Mot de passe valide"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.json
        
        # Validation des données requises
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        company = data.get('company', '').strip()
        
        # Validation de l'email
        if not validate_email(email):
            return jsonify({'error': 'Format d\'email invalide'}), 400
        
        # Validation du mot de passe
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Un compte avec cet email existe déjà'}), 409
        
        # Créer le nouvel utilisateur
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Créer la session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        return jsonify({
            'message': 'Inscription réussie',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de l\'inscription'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Trouver l'utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Vérifier le statut du compte
        if user.status != 'active':
            return jsonify({'error': 'Compte suspendu ou désactivé'}), 403
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Créer la session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_role'] = user.role
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la connexion'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Déconnexion de l'utilisateur"""
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Obtenir les informations de l'utilisateur connecté"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Demande de réinitialisation de mot de passe"""
    try:
        data = request.json
        
        if not data.get('email'):
            return jsonify({'error': 'Email requis'}), 400
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Pour des raisons de sécurité, on renvoie toujours le même message
        # même si l'email n'existe pas
        return jsonify({
            'message': 'Si cet email existe dans notre système, vous recevrez un lien de réinitialisation'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la demande'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Changer le mot de passe de l'utilisateur connecté"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    try:
        data = request.json
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Mot de passe actuel et nouveau mot de passe requis'}), 400
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier le mot de passe actuel
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
        
        # Valider le nouveau mot de passe
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Mettre à jour le mot de passe
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la modification'}), 500

