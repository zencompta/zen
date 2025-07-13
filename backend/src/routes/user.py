from flask import Blueprint, jsonify, request, session
from src.models.user import User, AuditProject, db
from datetime import datetime

user_bp = Blueprint('user', __name__)

def require_auth():
    """Vérifier que l'utilisateur est authentifié"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentification requise'}), 401
    return None

def require_admin():
    """Vérifier que l'utilisateur est admin"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Accès administrateur requis'}), 403
    return None

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Obtenir la liste des utilisateurs (admin seulement)"""
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtenir un utilisateur spécifique"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    # Un utilisateur peut voir ses propres infos, un admin peut voir tous les utilisateurs
    if session['user_id'] != user_id and session.get('user_role') != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Mettre à jour un utilisateur"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    # Un utilisateur peut modifier ses propres infos, un admin peut modifier tous les utilisateurs
    if session['user_id'] != user_id and session.get('user_role') != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Champs modifiables par l'utilisateur
    if 'first_name' in data:
        user.first_name = data['first_name'].strip()
    if 'last_name' in data:
        user.last_name = data['last_name'].strip()
    if 'company' in data:
        user.company = data['company'].strip()
    
    # Champs modifiables par l'admin seulement
    if session.get('user_role') == 'admin':
        if 'role' in data:
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
        if 'email_verified' in data:
            user.email_verified = data['email_verified']
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Supprimer un utilisateur (admin seulement)"""
    admin_error = require_admin()
    if admin_error:
        return admin_error
    
    user = User.query.get_or_404(user_id)
    
    # Marquer comme supprimé plutôt que de supprimer réellement
    user.status = 'deleted'
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur supprimé'}), 200

@user_bp.route('/audit-projects', methods=['GET'])
def get_audit_projects():
    """Obtenir les projets d'audit de l'utilisateur connecté"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    projects = AuditProject.query.filter_by(user_id=session['user_id']).all()
    return jsonify([project.to_dict() for project in projects])

@user_bp.route('/audit-projects', methods=['POST'])
def create_audit_project():
    """Créer un nouveau projet d'audit"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.json
    
    # Validation des données requises
    required_fields = ['company_name', 'audit_year', 'accounting_standard']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    project = AuditProject(
        user_id=session['user_id'],
        company_name=data['company_name'].strip(),
        audit_year=int(data['audit_year']),
        accounting_standard=data['accounting_standard']
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@user_bp.route('/audit-projects/<int:project_id>', methods=['GET'])
def get_audit_project(project_id):
    """Obtenir un projet d'audit spécifique"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    project = AuditProject.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est propriétaire du projet ou admin
    if project.user_id != session['user_id'] and session.get('user_role') != 'admin':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    return jsonify(project.to_dict())

@user_bp.route('/audit-projects/<int:project_id>', methods=['PUT'])
def update_audit_project(project_id):
    """Mettre à jour un projet d'audit"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    project = AuditProject.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est propriétaire du projet
    if project.user_id != session['user_id']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.json
    
    if 'company_name' in data:
        project.company_name = data['company_name'].strip()
    if 'audit_year' in data:
        project.audit_year = int(data['audit_year'])
    if 'accounting_standard' in data:
        project.accounting_standard = data['accounting_standard']
    if 'status' in data:
        project.status = data['status']
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(project.to_dict())

@user_bp.route('/audit-projects/<int:project_id>', methods=['DELETE'])
def delete_audit_project(project_id):
    """Supprimer un projet d'audit"""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    project = AuditProject.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est propriétaire du projet
    if project.user_id != session['user_id']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Projet supprimé'}), 200
