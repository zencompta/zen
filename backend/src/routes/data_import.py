from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from src.models.data_import import db, DataImport, AccountingEntry, AnalysisResult
from src.models.audit_project import AuditProject
from src.services.data_processor import DataProcessor
from src.services.audit_analyzer import AuditAnalyzer

data_import_bp = Blueprint('data_import', __name__)

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'json', 'xml'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@data_import_bp.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload et traitement initial d'un fichier de données"""
    try:
        # Vérifier les paramètres requis
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        audit_project_id = request.form.get('audit_project_id')
        import_type = request.form.get('import_type')  # balance, journal, grand_livre
        
        if not audit_project_id or not import_type:
            return jsonify({'error': 'Paramètres manquants: audit_project_id et import_type requis'}), 400
        
        # Vérifier que le projet appartient à l'utilisateur
        project = AuditProject.query.filter_by(
            id=audit_project_id, 
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        if file and allowed_file(file.filename):
            # Vérifier la taille du fichier
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': f'Fichier trop volumineux (max {MAX_FILE_SIZE // (1024*1024)}MB)'}), 400
            
            filename = secure_filename(file.filename)
            file_content = file.read()
            
            # Créer l'enregistrement d'import
            data_import = DataImport(
                audit_project_id=audit_project_id,
                file_name=filename,
                file_type=filename.rsplit('.', 1)[1].lower(),
                file_size=file_size,
                import_type=import_type,
                import_status='processing'
            )
            
            db.session.add(data_import)
            db.session.commit()
            
            # Traiter le fichier
            processor = DataProcessor()
            result = processor.process_file(file_content, filename, import_type)
            
            if result['success']:
                # Sauvegarder les données extraites
                data_import.extracted_data = json.dumps(result['data'])
                data_import.rows_imported = result['rows_processed']
                data_import.rows_failed = result['rows_with_errors']
                data_import.validation_errors = json.dumps(result['validation_errors'])
                data_import.import_status = 'completed'
                data_import.completed_at = datetime.utcnow()
                
                # Sauvegarder les écritures comptables
                for row_data in result['data']:
                    entry = AccountingEntry(
                        audit_project_id=audit_project_id,
                        data_import_id=data_import.id,
                        journal_code=row_data.get('journal_code'),
                        piece_number=row_data.get('piece_number'),
                        entry_date=datetime.strptime(row_data['entry_date'], '%Y-%m-%d').date() if row_data.get('entry_date') else None,
                        account_number=row_data['account_number'],
                        account_name=row_data.get('account_name'),
                        description=row_data.get('description'),
                        debit_amount=row_data.get('debit_amount', 0),
                        credit_amount=row_data.get('credit_amount', 0),
                        validation_status='valid'
                    )
                    db.session.add(entry)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'import_id': data_import.id,
                    'message': 'Fichier traité avec succès',
                    'summary': {
                        'rows_processed': result['rows_processed'],
                        'rows_with_errors': result['rows_with_errors'],
                        'rows_with_warnings': result['rows_with_warnings']
                    },
                    'validation_errors': result['validation_errors']
                })
            else:
                # Échec du traitement
                data_import.import_status = 'failed'
                data_import.validation_errors = json.dumps(result['errors'])
                db.session.commit()
                
                return jsonify({
                    'success': False,
                    'import_id': data_import.id,
                    'errors': result['errors'],
                    'suggestions': result.get('suggestions', {})
                }), 400
        
        return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500

@data_import_bp.route('/preview', methods=['POST'])
@require_auth
def preview_file():
    """Prévisualise un fichier avant import définitif"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        import_type = request.form.get('import_type', 'balance')
        
        if file and allowed_file(file.filename):
            file_content = file.read()
            filename = secure_filename(file.filename)
            
            processor = DataProcessor()
            
            # Traitement pour prévisualisation (sans sauvegarde)
            result = processor.process_file(file_content, filename, import_type)
            
            if result['success']:
                # Limiter les données pour la prévisualisation
                preview_data = result['data'][:10]  # Premiers 10 enregistrements
                
                return jsonify({
                    'success': True,
                    'preview_data': preview_data,
                    'total_rows': len(result['data']),
                    'columns_detected': result['columns_detected'],
                    'file_format': result['file_format'],
                    'validation_summary': {
                        'rows_with_errors': result['rows_with_errors'],
                        'rows_with_warnings': result['rows_with_warnings']
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'errors': result['errors'],
                    'suggestions': result.get('suggestions', {})
                }), 400
        
        return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la prévisualisation: {str(e)}'}), 500

@data_import_bp.route('/mapping', methods=['POST'])
@require_auth
def apply_column_mapping():
    """Applique un mapping personnalisé des colonnes"""
    try:
        data = request.get_json()
        import_id = data.get('import_id')
        column_mapping = data.get('mapping', {})
        
        if not import_id:
            return jsonify({'error': 'import_id requis'}), 400
        
        # Récupérer l'import
        data_import = DataImport.query.filter_by(id=import_id).first()
        if not data_import:
            return jsonify({'error': 'Import non trouvé'}), 404
        
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=data_import.audit_project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Sauvegarder la configuration de mapping
        data_import.mapping_config = json.dumps(column_mapping)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mapping appliqué avec succès'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'application du mapping: {str(e)}'}), 500

@data_import_bp.route('/project/<int:project_id>/imports', methods=['GET'])
@require_auth
def get_project_imports(project_id):
    """Récupère la liste des imports pour un projet"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        imports = DataImport.query.filter_by(audit_project_id=project_id).order_by(DataImport.created_at.desc()).all()
        
        return jsonify({
            'imports': [import_record.to_dict() for import_record in imports]
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@data_import_bp.route('/analyze/<int:project_id>', methods=['POST'])
@require_auth
def analyze_project_data(project_id):
    """Lance l'analyse comptable des données d'un projet"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Récupérer les données comptables
        entries = AccountingEntry.query.filter_by(audit_project_id=project_id).all()
        
        if not entries:
            return jsonify({'error': 'Aucune donnée à analyser'}), 400
        
        # Convertir en format pour l'analyseur
        entries_data = [entry.to_dict() for entry in entries]
        
        # Initialiser l'analyseur
        analyzer = AuditAnalyzer(project.accounting_standard)
        
        # Effectuer les analyses
        analyses = []
        
        # 1. Analyse de balance
        balance_analysis = analyzer.analyze_balance_sheet(entries_data)
        if 'error' not in balance_analysis:
            analyses.append(balance_analysis)
            
            # Sauvegarder le résultat
            result = AnalysisResult(
                audit_project_id=project_id,
                analysis_type='balance_analysis',
                analysis_name='Analyse de la balance générale',
                status='completed',
                result_summary=balance_analysis.get('summary', ''),
                result_data=json.dumps(balance_analysis),
                risk_level=balance_analysis.get('risk_level', 'low')
            )
            db.session.add(result)
        
        # 2. Analyse des écritures de journal
        journal_analysis = analyzer.analyze_journal_entries(entries_data)
        if 'error' not in journal_analysis:
            analyses.append(journal_analysis)
            
            result = AnalysisResult(
                audit_project_id=project_id,
                analysis_type='journal_analysis',
                analysis_name='Analyse des écritures de journal',
                status='completed',
                result_summary=journal_analysis.get('summary', ''),
                result_data=json.dumps(journal_analysis),
                risk_level=journal_analysis.get('risk_level', 'low')
            )
            db.session.add(result)
        
        # 3. Analyse par ratios
        ratio_analysis = analyzer.perform_ratio_analysis(entries_data)
        if 'error' not in ratio_analysis:
            analyses.append(ratio_analysis)
            
            result = AnalysisResult(
                audit_project_id=project_id,
                analysis_type='ratio_analysis',
                analysis_name='Analyse par ratios financiers',
                status='completed',
                result_summary=json.dumps(ratio_analysis.get('interpretations', [])),
                result_data=json.dumps(ratio_analysis),
                risk_level=ratio_analysis.get('risk_level', 'low')
            )
            db.session.add(result)
        
        # 4. Détection de fraude
        fraud_analysis = analyzer.detect_fraud_indicators(entries_data)
        if 'error' not in fraud_analysis:
            analyses.append(fraud_analysis)
            
            result = AnalysisResult(
                audit_project_id=project_id,
                analysis_type='fraud_detection',
                analysis_name='Détection d\'indicateurs de fraude',
                status='completed',
                result_summary=f"{len(fraud_analysis.get('indicators', []))} indicateurs détectés",
                result_data=json.dumps(fraud_analysis),
                risk_level=fraud_analysis.get('risk_level', 'low')
            )
            db.session.add(result)
        
        # Mettre à jour le statut du projet
        project.status = 'in_progress'
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Analyse terminée avec succès',
            'analyses_count': len(analyses),
            'analyses': analyses
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500

@data_import_bp.route('/project/<int:project_id>/analysis-results', methods=['GET'])
@require_auth
def get_analysis_results(project_id):
    """Récupère les résultats d'analyse pour un projet"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        results = AnalysisResult.query.filter_by(audit_project_id=project_id).order_by(AnalysisResult.created_at.desc()).all()
        
        return jsonify({
            'results': [result.to_dict() for result in results]
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@data_import_bp.route('/project/<int:project_id>/data-summary', methods=['GET'])
@require_auth
def get_data_summary(project_id):
    """Récupère un résumé des données importées pour un projet"""
    try:
        # Vérifier l'autorisation
        project = AuditProject.query.filter_by(
            id=project_id,
            user_id=session['user_id']
        ).first()
        
        if not project:
            return jsonify({'error': 'Projet non trouvé ou accès non autorisé'}), 404
        
        # Statistiques des imports
        imports_count = DataImport.query.filter_by(audit_project_id=project_id).count()
        successful_imports = DataImport.query.filter_by(audit_project_id=project_id, import_status='completed').count()
        
        # Statistiques des écritures
        entries_count = AccountingEntry.query.filter_by(audit_project_id=project_id).count()
        total_debit = db.session.query(db.func.sum(AccountingEntry.debit_amount)).filter_by(audit_project_id=project_id).scalar() or 0
        total_credit = db.session.query(db.func.sum(AccountingEntry.credit_amount)).filter_by(audit_project_id=project_id).scalar() or 0
        
        # Comptes uniques
        unique_accounts = db.session.query(AccountingEntry.account_number).filter_by(audit_project_id=project_id).distinct().count()
        
        # Analyses effectuées
        analyses_count = AnalysisResult.query.filter_by(audit_project_id=project_id).count()
        
        return jsonify({
            'summary': {
                'imports': {
                    'total': imports_count,
                    'successful': successful_imports,
                    'failed': imports_count - successful_imports
                },
                'entries': {
                    'total_entries': entries_count,
                    'total_debit': float(total_debit),
                    'total_credit': float(total_credit),
                    'balance_difference': float(abs(total_debit - total_credit)),
                    'unique_accounts': unique_accounts
                },
                'analyses': {
                    'total_analyses': analyses_count
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du résumé: {str(e)}'}), 500

