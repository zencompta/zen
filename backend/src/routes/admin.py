from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.audit_project import AuditProject
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Vérifie que l'utilisateur est connecté et est administrateur"""
    if 'user_id' not in session:
        return None
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        return None
    return user

@admin_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    """Récupère tous les utilisateurs (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    users = User.query.all()
    users_data = []
    
    for user in users:
        user_dict = user.to_dict()
        # Ajouter des informations supplémentaires
        user_dict['project_count'] = AuditProject.query.filter_by(user_id=user.id).count()
        users_data.append(user_dict)
    
    return jsonify(users_data)

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    """Met à jour le statut d'un utilisateur (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['active', 'suspended', 'deleted']:
        return jsonify({'error': 'Statut non valide'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Empêcher la modification de son propre compte
    if user.id == admin.id:
        return jsonify({'error': 'Impossible de modifier votre propre statut'}), 400
    
    user.status = new_status
    
    try:
        db.session.commit()
        return jsonify({'message': 'Statut utilisateur mis à jour', 'user': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la mise à jour'}), 500

@admin_bp.route('/admin/projects', methods=['GET'])
def get_all_projects():
    """Récupère tous les projets d'audit (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Jointure avec les utilisateurs pour récupérer les emails
    projects = db.session.query(
        AuditProject,
        User.email.label('user_email'),
        User.first_name.label('user_first_name'),
        User.last_name.label('user_last_name')
    ).join(User, AuditProject.user_id == User.id).all()
    
    projects_data = []
    for project, user_email, user_first_name, user_last_name in projects:
        project_dict = project.to_dict()
        project_dict['user_email'] = user_email
        project_dict['user_name'] = f"{user_first_name} {user_last_name}"
        projects_data.append(project_dict)
    
    return jsonify(projects_data)

@admin_bp.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    """Récupère les statistiques pour l'administration"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Statistiques des utilisateurs
    total_users = User.query.count()
    active_users = User.query.filter_by(status='active').count()
    suspended_users = User.query.filter_by(status='suspended').count()
    deleted_users = User.query.filter_by(status='deleted').count()
    
    # Statistiques des projets
    total_projects = AuditProject.query.count()
    draft_projects = AuditProject.query.filter_by(status='draft').count()
    in_progress_projects = AuditProject.query.filter_by(status='in_progress').count()
    completed_projects = AuditProject.query.filter_by(status='completed').count()
    
    # Projets ce mois-ci
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    projects_this_month = AuditProject.query.filter(
        AuditProject.created_at >= start_of_month
    ).count()
    
    # Nouveaux utilisateurs ce mois-ci
    new_users_this_month = User.query.filter(
        User.created_at >= start_of_month
    ).count()
    
    # Activité récente (derniers 30 jours)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_activity = {
        'new_users': User.query.filter(User.created_at >= thirty_days_ago).count(),
        'new_projects': AuditProject.query.filter(AuditProject.created_at >= thirty_days_ago).count(),
    }
    
    # Répartition par norme comptable
    accounting_standards = db.session.query(
        AuditProject.accounting_standard,
        func.count(AuditProject.id).label('count')
    ).group_by(AuditProject.accounting_standard).all()
    
    standards_stats = {standard: count for standard, count in accounting_standards}
    
    stats = {
        'users': {
            'total': total_users,
            'active': active_users,
            'suspended': suspended_users,
            'deleted': deleted_users,
            'new_this_month': new_users_this_month
        },
        'projects': {
            'total': total_projects,
            'draft': draft_projects,
            'in_progress': in_progress_projects,
            'completed': completed_projects,
            'this_month': projects_this_month
        },
        'recent_activity': recent_activity,
        'accounting_standards': standards_stats,
        # Statistiques simplifiées pour l'affichage principal
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'projects_this_month': projects_this_month
    }
    
    return jsonify(stats)

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """Récupère les détails d'un utilisateur (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Récupérer les projets de l'utilisateur
    projects = AuditProject.query.filter_by(user_id=user_id).all()
    
    user_data = user.to_dict()
    user_data['projects'] = [project.to_dict() for project in projects]
    
    return jsonify(user_data)

@admin_bp.route('/admin/projects/<int:project_id>', methods=['DELETE'])
def delete_project_admin(project_id):
    """Supprime un projet (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    project = AuditProject.query.get(project_id)
    if not project:
        return jsonify({'error': 'Projet non trouvé'}), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Projet supprimé avec succès'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la suppression'}), 500

@admin_bp.route('/admin/system/info', methods=['GET'])
def get_system_info():
    """Récupère les informations système (admin seulement)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Informations système basiques
    system_info = {
        'version': '1.0.0',
        'environment': 'development',
        'database': {
            'type': 'SQLite',
            'users_count': User.query.count(),
            'projects_count': AuditProject.query.count()
        },
        'features': {
            'authentication': True,
            'audit_projects': True,
            'admin_panel': True,
            'reports': False  # En développement
        }
    }
    
    return jsonify(system_info)

