"""
Modèle de données pour la gestion des abonnements et du modèle freemium
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any

class SubscriptionType(Enum):
    """Types d'abonnement disponibles"""
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionStatus(Enum):
    """Statuts d'abonnement"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class UserSubscription:
    """Modèle pour gérer les abonnements utilisateur"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.subscription_type = SubscriptionType.FREE
        self.status = SubscriptionStatus.ACTIVE
        self.start_date = datetime.now()
        self.end_date = None
        self.audits_used = 0
        self.max_audits = 3  # Limite pour les utilisateurs gratuits
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return {
            'user_id': self.user_id,
            'subscription_type': self.subscription_type.value,
            'status': self.status.value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'audits_used': self.audits_used,
            'max_audits': self.max_audits,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSubscription':
        """Crée un objet à partir d'un dictionnaire"""
        subscription = cls(data['user_id'])
        subscription.subscription_type = SubscriptionType(data['subscription_type'])
        subscription.status = SubscriptionStatus(data['status'])
        subscription.start_date = datetime.fromisoformat(data['start_date']) if data['start_date'] else None
        subscription.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        subscription.audits_used = data['audits_used']
        subscription.max_audits = data['max_audits']
        subscription.created_at = datetime.fromisoformat(data['created_at'])
        subscription.updated_at = datetime.fromisoformat(data['updated_at'])
        return subscription
    
    def can_perform_audit(self) -> bool:
        """Vérifie si l'utilisateur peut effectuer un audit"""
        if self.subscription_type == SubscriptionType.FREE:
            return self.audits_used < self.max_audits
        
        # Pour les abonnements payants, vérifier si l'abonnement est actif
        if self.subscription_type in [SubscriptionType.MONTHLY, SubscriptionType.YEARLY]:
            return self.is_subscription_active()
        
        return False
    
    def is_subscription_active(self) -> bool:
        """Vérifie si l'abonnement est actif"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        
        if self.end_date and datetime.now() > self.end_date:
            self.status = SubscriptionStatus.EXPIRED
            return False
        
        return True
    
    def increment_audit_usage(self) -> bool:
        """Incrémente le nombre d'audits utilisés"""
        if not self.can_perform_audit():
            return False
        
        self.audits_used += 1
        self.updated_at = datetime.now()
        return True
    
    def upgrade_to_monthly(self) -> None:
        """Met à niveau vers l'abonnement mensuel"""
        self.subscription_type = SubscriptionType.MONTHLY
        self.status = SubscriptionStatus.ACTIVE
        self.start_date = datetime.now()
        self.end_date = datetime.now() + timedelta(days=30)
        self.max_audits = -1  # Illimité
        self.updated_at = datetime.now()
    
    def upgrade_to_yearly(self) -> None:
        """Met à niveau vers l'abonnement annuel"""
        self.subscription_type = SubscriptionType.YEARLY
        self.status = SubscriptionStatus.ACTIVE
        self.start_date = datetime.now()
        self.end_date = datetime.now() + timedelta(days=365)
        self.max_audits = -1  # Illimité
        self.updated_at = datetime.now()
    
    def get_remaining_audits(self) -> int:
        """Retourne le nombre d'audits restants"""
        if self.subscription_type == SubscriptionType.FREE:
            return max(0, self.max_audits - self.audits_used)
        return -1  # Illimité pour les abonnements payants
    
    def get_days_until_expiry(self) -> Optional[int]:
        """Retourne le nombre de jours avant expiration"""
        if not self.end_date:
            return None
        
        delta = self.end_date - datetime.now()
        return max(0, delta.days)

class SubscriptionPlan:
    """Modèle pour les plans d'abonnement"""
    
    PLANS = {
        SubscriptionType.FREE: {
            'name': 'Gratuit',
            'price': 0,
            'currency': 'FCFA',
            'duration_days': None,
            'max_audits': 3,
            'features': [
                'Jusqu\'à 3 audits gratuits',
                'Fonctionnalités de base',
                'Support communautaire'
            ]
        },
        SubscriptionType.MONTHLY: {
            'name': 'Mensuel',
            'price': 30000,
            'currency': 'FCFA',
            'duration_days': 30,
            'max_audits': -1,  # Illimité
            'features': [
                'Audits illimités pendant 1 mois',
                'Toutes les fonctionnalités avancées',
                'Analyse IA complète',
                'Templates professionnels',
                'Visualisations 3D',
                'Support prioritaire',
                'Rapports personnalisés'
            ]
        },
        SubscriptionType.YEARLY: {
            'name': 'Annuel',
            'price': 200000,
            'currency': 'FCFA',
            'duration_days': 365,
            'max_audits': -1,  # Illimité
            'features': [
                'Audits illimités pendant 1 an',
                'Toutes les fonctionnalités avancées',
                'Analyse IA complète',
                'Templates professionnels',
                'Visualisations 3D',
                'Support prioritaire VIP',
                'Rapports personnalisés',
                'Formation personnalisée',
                'Économie de 133.000 FCFA par rapport au mensuel'
            ]
        }
    }
    
    @classmethod
    def get_plan_details(cls, subscription_type: SubscriptionType) -> Dict[str, Any]:
        """Retourne les détails d'un plan d'abonnement"""
        return cls.PLANS.get(subscription_type, {})
    
    @classmethod
    def get_all_plans(cls) -> Dict[str, Dict[str, Any]]:
        """Retourne tous les plans d'abonnement"""
        return {plan_type.value: plan_details for plan_type, plan_details in cls.PLANS.items()}

class FreemiumManager:
    """Gestionnaire pour la logique freemium"""
    
    def __init__(self):
        self.subscriptions = {}  # En production, utiliser une base de données
    
    def get_user_subscription(self, user_id: str) -> UserSubscription:
        """Récupère l'abonnement d'un utilisateur"""
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = UserSubscription(user_id)
        return self.subscriptions[user_id]
    
    def can_user_perform_audit(self, user_id: str) -> tuple[bool, str]:
        """Vérifie si un utilisateur peut effectuer un audit"""
        subscription = self.get_user_subscription(user_id)
        
        if subscription.can_perform_audit():
            return True, "Audit autorisé"
        
        if subscription.subscription_type == SubscriptionType.FREE:
            return False, f"Limite de {subscription.max_audits} audits gratuits atteinte. Veuillez souscrire à un abonnement."
        
        if not subscription.is_subscription_active():
            return False, "Votre abonnement a expiré. Veuillez renouveler votre abonnement."
        
        return False, "Audit non autorisé"
    
    def perform_audit(self, user_id: str) -> tuple[bool, str]:
        """Effectue un audit pour un utilisateur"""
        subscription = self.get_user_subscription(user_id)
        
        if subscription.increment_audit_usage():
            return True, "Audit effectué avec succès"
        
        return False, "Impossible d'effectuer l'audit"
    
    def upgrade_subscription(self, user_id: str, subscription_type: SubscriptionType) -> tuple[bool, str]:
        """Met à niveau l'abonnement d'un utilisateur"""
        subscription = self.get_user_subscription(user_id)
        
        try:
            if subscription_type == SubscriptionType.MONTHLY:
                subscription.upgrade_to_monthly()
                return True, "Abonnement mensuel activé avec succès"
            elif subscription_type == SubscriptionType.YEARLY:
                subscription.upgrade_to_yearly()
                return True, "Abonnement annuel activé avec succès"
            else:
                return False, "Type d'abonnement invalide"
        except Exception as e:
            return False, f"Erreur lors de la mise à niveau: {str(e)}"
    
    def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """Retourne le statut d'abonnement d'un utilisateur"""
        subscription = self.get_user_subscription(user_id)
        
        return {
            'subscription_type': subscription.subscription_type.value,
            'status': subscription.status.value,
            'audits_used': subscription.audits_used,
            'remaining_audits': subscription.get_remaining_audits(),
            'max_audits': subscription.max_audits,
            'days_until_expiry': subscription.get_days_until_expiry(),
            'can_perform_audit': subscription.can_perform_audit(),
            'plan_details': SubscriptionPlan.get_plan_details(subscription.subscription_type)
        }

# Instance globale du gestionnaire freemium
freemium_manager = FreemiumManager()

