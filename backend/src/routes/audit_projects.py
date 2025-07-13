from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.audit_project import AuditProject
import json

audit_projects_bp = Blueprint('audit_projects', __name__)

def require_auth():
    """Vérifie que l'utilisateur est connecté"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@audit_projects_bp.route('/audit-projects', methods=['GET'])
def get_audit_projects():
    """Récupère tous les projets d'audit de l'utilisateur connecté"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    projects = AuditProject.query.filter_by(user_id=user.id).order_by(AuditProject.updated_at.desc()).all()
    return jsonify([project.to_dict() for project in projects])

@audit_projects_bp.route('/audit-projects', methods=['POST'])
def create_audit_project():
    """Crée un nouveau projet d'audit"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    data = request.get_json()
    
    # Validation des données
    if not data.get('company_name'):
        return jsonify({'error': 'Le nom de l\'entreprise est requis'}), 400
    
    if not data.get('audit_year'):
        return jsonify({'error': 'L\'exercice d\'audit est requis'}), 400
    
    if not data.get('accounting_standard'):
        return jsonify({'error': 'La norme comptable est requise'}), 400
    
    # Validation de la norme comptable
    if not AuditProject.validate_accounting_standard(data['accounting_standard']):
        return jsonify({'error': 'Norme comptable non supportée'}), 400
    
    # Validation de l'année
    try:
        audit_year = int(data['audit_year'])
        if audit_year < 2020 or audit_year > 2030:
            return jsonify({'error': 'L\'exercice doit être entre 2020 et 2030'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'L\'exercice doit être un nombre valide'}), 400
    
    # Vérifier qu'un projet similaire n'existe pas déjà
    existing_project = AuditProject.query.filter_by(
        user_id=user.id,
        company_name=data['company_name'],
        audit_year=audit_year
    ).first()
    
    if existing_project:
        return jsonify({'error': 'Un projet existe déjà pour cette entreprise et cet exercice'}), 400
    
    # Créer le nouveau projet
    project = AuditProject(
        company_name=data['company_name'].strip(),
        audit_year=audit_year,
        accounting_standard=data['accounting_standard'],
        user_id=user.id,
        status='draft'
    )
    
    try:
        db.session.add(project)
        db.session.commit()
        return jsonify(project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la création du projet'}), 500

@audit_projects_bp.route('/audit-projects/<int:project_id>', methods=['GET'])
def get_audit_project(project_id):
    """Récupère un projet d'audit spécifique"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    project = AuditProject.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    return jsonify(project.to_dict())

@audit_projects_bp.route('/audit-projects/<int:project_id>', methods=['PUT'])
def update_audit_project(project_id):
    """Met à jour un projet d'audit"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    project = AuditProject.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    data = request.get_json()
    
    # Mise à jour des champs autorisés
    if 'company_name' in data:
        if not data['company_name'].strip():
            return jsonify({'error': 'Le nom de l\'entreprise ne peut pas être vide'}), 400
        project.company_name = data['company_name'].strip()
    
    if 'audit_year' in data:
        try:
            audit_year = int(data['audit_year'])
            if audit_year < 2020 or audit_year > 2030:
                return jsonify({'error': 'L\'exercice doit être entre 2020 et 2030'}), 400
            project.audit_year = audit_year
        except (ValueError, TypeError):
            return jsonify({'error': 'L\'exercice doit être un nombre valide'}), 400
    
    if 'accounting_standard' in data:
        if not AuditProject.validate_accounting_standard(data['accounting_standard']):
            return jsonify({'error': 'Norme comptable non supportée'}), 400
        project.accounting_standard = data['accounting_standard']
    
    if 'status' in data:
        if not AuditProject.validate_status(data['status']):
            return jsonify({'error': 'Statut non valide'}), 400
        project.status = data['status']
    
    if 'audit_data' in data:
        # Valider que c'est du JSON valide
        try:
            json.dumps(data['audit_data'])
            project.audit_data = json.dumps(data['audit_data'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Données d\'audit non valides'}), 400
    
    try:
        db.session.commit()
        return jsonify(project.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la mise à jour du projet'}), 500

@audit_projects_bp.route('/audit-projects/<int:project_id>', methods=['DELETE'])
def delete_audit_project(project_id):
    """Supprime un projet d'audit"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    project = AuditProject.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projet supprimé avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la suppression du projet'}), 500

@audit_projects_bp.route('/audit-projects/<int:project_id>/generate-report', methods=['POST'])
def generate_audit_report(project_id):
    """Génère un rapport d'audit pour un projet"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non autorisé'}), 401
    
    project = AuditProject.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    # TODO: Implémenter la génération de rapport
    return jsonify({
        'message': 'Génération de rapport en développement',
        'project_id': project_id
    }), 501

