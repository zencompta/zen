from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class DataImport(db.Model):
    """Modèle pour stocker les informations d'importation de données"""
    __tablename__ = 'data_imports'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_project_id = db.Column(db.Integer, db.ForeignKey('audit_projects.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # excel, csv, pdf, json, xml, fec
    file_size = db.Column(db.Integer, nullable=False)  # en bytes
    import_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    import_type = db.Column(db.String(50), nullable=False)  # balance, journal, grand_livre, etats_financiers
    
    # Métadonnées d'importation
    rows_imported = db.Column(db.Integer, default=0)
    rows_failed = db.Column(db.Integer, default=0)
    validation_errors = db.Column(db.Text)  # JSON des erreurs de validation
    mapping_config = db.Column(db.Text)  # JSON de la configuration de mapping des colonnes
    
    # Données extraites (stockage temporaire)
    extracted_data = db.Column(db.Text)  # JSON des données extraites
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relations
    audit_project = db.relationship('AuditProject', backref='data_imports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'audit_project_id': self.audit_project_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'import_status': self.import_status,
            'import_type': self.import_type,
            'rows_imported': self.rows_imported,
            'rows_failed': self.rows_failed,
            'validation_errors': json.loads(self.validation_errors) if self.validation_errors else [],
            'mapping_config': json.loads(self.mapping_config) if self.mapping_config else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AccountingEntry(db.Model):
    """Modèle pour stocker les écritures comptables importées"""
    __tablename__ = 'accounting_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_project_id = db.Column(db.Integer, db.ForeignKey('audit_projects.id'), nullable=False)
    data_import_id = db.Column(db.Integer, db.ForeignKey('data_imports.id'), nullable=False)
    
    # Informations de l'écriture
    journal_code = db.Column(db.String(20))
    piece_number = db.Column(db.String(50))
    entry_date = db.Column(db.Date)
    account_number = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    # Montants
    debit_amount = db.Column(db.Numeric(15, 2), default=0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0)
    currency = db.Column(db.String(3), default='EUR')
    
    # Métadonnées
    line_number = db.Column(db.Integer)  # Numéro de ligne dans le fichier source
    validation_status = db.Column(db.String(20), default='valid')  # valid, warning, error
    validation_messages = db.Column(db.Text)  # JSON des messages de validation
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    audit_project = db.relationship('AuditProject', backref='accounting_entries')
    data_import = db.relationship('DataImport', backref='accounting_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'audit_project_id': self.audit_project_id,
            'data_import_id': self.data_import_id,
            'journal_code': self.journal_code,
            'piece_number': self.piece_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'description': self.description,
            'debit_amount': float(self.debit_amount) if self.debit_amount else 0,
            'credit_amount': float(self.credit_amount) if self.credit_amount else 0,
            'currency': self.currency,
            'line_number': self.line_number,
            'validation_status': self.validation_status,
            'validation_messages': json.loads(self.validation_messages) if self.validation_messages else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AnalysisResult(db.Model):
    """Modèle pour stocker les résultats d'analyse comptable"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_project_id = db.Column(db.Integer, db.ForeignKey('audit_projects.id'), nullable=False)
    
    # Type d'analyse
    analysis_type = db.Column(db.String(50), nullable=False)  # balance_check, anomaly_detection, ratio_analysis, etc.
    analysis_name = db.Column(db.String(255), nullable=False)
    
    # Résultats
    status = db.Column(db.String(20), default='completed')  # completed, failed, warning
    result_summary = db.Column(db.Text)  # Résumé textuel
    result_data = db.Column(db.Text)  # JSON des données détaillées
    
    # Métriques
    risk_level = db.Column(db.String(20))  # low, medium, high, critical
    confidence_score = db.Column(db.Float)  # Score de confiance 0-1
    
    # Recommandations
    recommendations = db.Column(db.Text)  # JSON des recommandations
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    audit_project = db.relationship('AuditProject', backref='analysis_results')
    
    def to_dict(self):
        return {
            'id': self.id,
            'audit_project_id': self.audit_project_id,
            'analysis_type': self.analysis_type,
            'analysis_name': self.analysis_name,
            'status': self.status,
            'result_summary': self.result_summary,
            'result_data': json.loads(self.result_data) if self.result_data else {},
            'risk_level': self.risk_level,
            'confidence_score': self.confidence_score,
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

