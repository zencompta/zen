from flask import Blueprint, request, jsonify, session, send_file
import os
import json
from datetime import datetime
from src.models.audit_project import AuditProject
from src.models.data_import import AnalysisResult, AccountingEntry
from src.services.report_generator import ReportGenerator
import tempfile

reports_bp = Blueprint('reports', __name__)

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@reports_bp.route('/generate/<int:project_id>', methods=['POST'])
@require_auth
def generate_comprehensive_report(project_id):
    """Génère un rapport d'audit complet"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Récupérer les résultats d'analyse
        analysis_results = AnalysisResult.query.filter_by(audit_project_id=project_id).all()
        
        if not analysis_results:
            return jsonify({'error': 'Aucune analyse disponible pour ce projet'}), 400
        
        # Préparer les données du projet
        project_data = {
            'company_name': project.company_name,
            'audit_year': project.audit_year,
            'accounting_standard': project.accounting_standard,
            'created_at': project.created_at.strftime('%d/%m/%Y'),
            'status': project.status,
            'total_entries': AccountingEntry.query.filter_by(audit_project_id=project_id).count()
        }
        
        # Convertir les résultats d'analyse
        analysis_data = []
        for result in analysis_results:
            analysis_dict = result.to_dict()
            # Parser le JSON des données détaillées
            if result.result_data:
                try:
                    analysis_dict['detailed_data'] = json.loads(result.result_data)
                except json.JSONDecodeError:
                    analysis_dict['detailed_data'] = {}
            analysis_data.append(analysis_dict)
        
        # Créer le générateur de rapport
        generator = ReportGenerator(project_data, analysis_data, project.accounting_standard)
        
        # Générer le fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            result = generator.generate_comprehensive_report(tmp_file.name)
            
            if result['success']:
                # Retourner le fichier
                return send_file(
                    tmp_file.name,
                    as_attachment=True,
                    download_name=f"rapport_audit_{project.company_name}_{project.audit_year}.pdf",
                    mimetype='application/pdf'
                )
            else:
                return jsonify({'error': f'Erreur lors de la génération: {result["error"]}'}), 500
                
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération du rapport: {str(e)}'}), 500

@reports_bp.route('/generate-summary/<int:project_id>', methods=['POST'])
@require_auth
def generate_summary_report(project_id):
    """Génère un résumé exécutif"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Récupérer les résultats d'analyse
        analysis_results = AnalysisResult.query.filter_by(audit_project_id=project_id).all()
        
        if not analysis_results:
            return jsonify({'error': 'Aucune analyse disponible pour ce projet'}), 400
        
        # Préparer les données
        project_data = {
            'company_name': project.company_name,
            'audit_year': project.audit_year,
            'accounting_standard': project.accounting_standard,
            'total_entries': AccountingEntry.query.filter_by(audit_project_id=project_id).count()
        }
        
        analysis_data = [result.to_dict() for result in analysis_results]
        
        # Créer le générateur de rapport
        generator = ReportGenerator(project_data, analysis_data, project.accounting_standard)
        
        # Générer le résumé
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            result = generator.generate_executive_summary_only(tmp_file.name)
            
            if result['success']:
                return send_file(
                    tmp_file.name,
                    as_attachment=True,
                    download_name=f"resume_audit_{project.company_name}_{project.audit_year}.pdf",
                    mimetype='application/pdf'
                )
            else:
                return jsonify({'error': f'Erreur lors de la génération: {result["error"]}'}), 500
                
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération du résumé: {str(e)}'}), 500

@reports_bp.route('/preview/<int:project_id>', methods=['GET'])
@require_auth
def preview_report_data(project_id):
    """Prévisualise les données qui seront incluses dans le rapport"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Récupérer les statistiques
        analysis_results = AnalysisResult.query.filter_by(audit_project_id=project_id).all()
        total_entries = AccountingEntry.query.filter_by(audit_project_id=project_id).count()
        
        # Calculer les statistiques de risque
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        total_anomalies = 0
        
        for result in analysis_results:
            risk_level = result.risk_level or 'low'
            risk_distribution[risk_level] += 1
            
            # Compter les anomalies
            if result.result_data:
                try:
                    data = json.loads(result.result_data)
                    anomalies = data.get('anomalies', [])
                    total_anomalies += len(anomalies)
                except json.JSONDecodeError:
                    pass
        
        # Préparer la prévisualisation
        preview_data = {
            'project_info': {
                'company_name': project.company_name,
                'audit_year': project.audit_year,
                'accounting_standard': project.accounting_standard,
                'status': project.status,
                'created_at': project.created_at.strftime('%d/%m/%Y')
            },
            'statistics': {
                'total_analyses': len(analysis_results),
                'total_entries': total_entries,
                'total_anomalies': total_anomalies,
                'risk_distribution': risk_distribution
            },
            'analyses_summary': [
                {
                    'type': result.analysis_type,
                    'name': result.analysis_name,
                    'risk_level': result.risk_level,
                    'created_at': result.created_at.strftime('%d/%m/%Y %H:%M')
                }
                for result in analysis_results
            ]
        }
        
        return jsonify({
            'success': True,
            'preview': preview_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la prévisualisation: {str(e)}'}), 500

@reports_bp.route('/templates', methods=['GET'])
@require_auth
def get_report_templates():
    """Récupère la liste des modèles de rapport disponibles"""
    try:
        templates = [
            {
                'id': 'comprehensive',
                'name': 'Rapport Complet',
                'description': 'Rapport d\'audit détaillé avec toutes les analyses, graphiques et recommandations',
                'pages_estimate': '15-25 pages',
                'includes': [
                    'Page de couverture professionnelle',
                    'Résumé exécutif',
                    'Table des matières',
                    'Analyse détaillée de la balance',
                    'Analyse des écritures de journal',
                    'Analyse par ratios financiers',
                    'Détection d\'indicateurs de fraude',
                    'Graphiques et visualisations',
                    'Recommandations détaillées',
                    'Annexes méthodologiques'
                ]
            },
            {
                'id': 'executive_summary',
                'name': 'Résumé Exécutif',
                'description': 'Version condensée pour la direction avec les points clés',
                'pages_estimate': '3-5 pages',
                'includes': [
                    'Synthèse des résultats',
                    'Tableau de synthèse des risques',
                    'Recommandations prioritaires',
                    'Conclusion générale'
                ]
            },
            {
                'id': 'technical',
                'name': 'Rapport Technique',
                'description': 'Rapport détaillé pour les équipes comptables et d\'audit',
                'pages_estimate': '10-15 pages',
                'includes': [
                    'Analyses techniques détaillées',
                    'Méthodologie appliquée',
                    'Données brutes et calculs',
                    'Recommandations techniques'
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des modèles: {str(e)}'}), 500

@reports_bp.route('/custom-generate/<int:project_id>', methods=['POST'])
@require_auth
def generate_custom_report(project_id):
    """Génère un rapport personnalisé selon les options choisies"""
    try:
        data = request.get_json()
        template_id = data.get('template_id', 'comprehensive')
        custom_options = data.get('options', {})
        
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Récupérer les données nécessaires
        analysis_results = AnalysisResult.query.filter_by(audit_project_id=project_id).all()
        
        if not analysis_results:
            return jsonify({'error': 'Aucune analyse disponible pour ce projet'}), 400
        
        project_data = {
            'company_name': project.company_name,
            'audit_year': project.audit_year,
            'accounting_standard': project.accounting_standard,
            'created_at': project.created_at.strftime('%d/%m/%Y'),
            'status': project.status,
            'total_entries': AccountingEntry.query.filter_by(audit_project_id=project_id).count()
        }
        
        analysis_data = [result.to_dict() for result in analysis_results]
        
        # Créer le générateur avec options personnalisées
        generator = ReportGenerator(project_data, analysis_data, project.accounting_standard)
        
        # Générer selon le template choisi
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            if template_id == 'executive_summary':
                result = generator.generate_executive_summary_only(tmp_file.name)
            else:
                result = generator.generate_comprehensive_report(tmp_file.name)
            
            if result['success']:
                filename = f"rapport_{template_id}_{project.company_name}_{project.audit_year}.pdf"
                return send_file(
                    tmp_file.name,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            else:
                return jsonify({'error': f'Erreur lors de la génération: {result["error"]}'}), 500
                
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération personnalisée: {str(e)}'}), 500

