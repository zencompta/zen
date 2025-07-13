from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AuditProject(db.Model):
    __tablename__ = 'audit_project'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    audit_year = db.Column(db.Integer, nullable=False)
    accounting_standard = db.Column(db.String(50), nullable=False)  # IFRS, SYSCOHADA, US_GAAP, PCG, OTHER
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, completed
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Données d'audit (JSON pour flexibilité)
    audit_data = db.Column(db.Text)  # Stockage JSON des données d'audit
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'audit_year': self.audit_year,
            'accounting_standard': self.accounting_standard,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'audit_data': self.audit_data
        }
    
    @staticmethod
    def validate_accounting_standard(standard):
        """Valide que la norme comptable est supportée"""
        valid_standards = ['IFRS', 'SYSCOHADA', 'US_GAAP', 'PCG', 'OTHER']
        return standard in valid_standards
    
    @staticmethod
    def validate_status(status):
        """Valide que le statut est valide"""
        valid_statuses = ['draft', 'in_progress', 'completed']
        return status in valid_statuses

