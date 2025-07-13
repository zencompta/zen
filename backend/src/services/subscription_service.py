"""
Service de gestion des abonnements et du modèle freemium
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import os
from typing import Dict, Any, Tuple

from ..models.subscription import (
    freemium_manager, 
    SubscriptionType, 
    SubscriptionPlan,
    UserSubscription
)

subscription_bp = Blueprint('subscription', __name__)

class SubscriptionService:
    """Service pour gérer les abonnements et la logique freemium"""
    
    def __init__(self):
        self.freemium_manager = freemium_manager
        self.data_file = 'subscriptions.json'
        self.load_subscriptions()
    
    def load_subscriptions(self):
        """Charge les abonnements depuis le fichier JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, sub_data in data.items():
                        self.freemium_manager.subscriptions[user_id] = UserSubscription.from_dict(sub_data)
        except Exception as e:
            print(f"Erreur lors du chargement des abonnements: {e}")
    
    def save_subscriptions(self):
        """Sauvegarde les abonnements dans le fichier JSON"""
        try:
            data = {}
            for user_id, subscription in self.freemium_manager.subscriptions.items():
                data[user_id] = subscription.to_dict()
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des abonnements: {e}")
    
    def check_audit_permission(self, user_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Vérifie si un utilisateur peut effectuer un audit"""
        can_audit, message = self.freemium_manager.can_user_perform_audit(user_id)
        status = self.freemium_manager.get_subscription_status(user_id)
        
        return can_audit, message, status
    
    def perform_audit(self, user_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Effectue un audit pour un utilisateur"""
        success, message = self.freemium_manager.perform_audit(user_id)
        
        if success:
            self.save_subscriptions()
        
        status = self.freemium_manager.get_subscription_status(user_id)
        return success, message, status
    
    def upgrade_subscription(self, user_id: str, plan_type: str, payment_info: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Met à niveau l'abonnement d'un utilisateur"""
        try:
            subscription_type = SubscriptionType(plan_type)
            success, message = self.freemium_manager.upgrade_subscription(user_id, subscription_type)
            
            if success:
                self.save_subscriptions()
                # Ici, on pourrait intégrer un vrai système de paiement
                # Pour l'instant, on simule le paiement comme réussi
                
            return success, message
        except ValueError:
            return False, "Type d'abonnement invalide"
        except Exception as e:
            return False, f"Erreur lors de la mise à niveau: {str(e)}"
    
    def get_subscription_plans(self) -> Dict[str, Any]:
        """Retourne tous les plans d'abonnement disponibles"""
        return SubscriptionPlan.get_all_plans()
    
    def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Retourne le statut complet d'un utilisateur"""
        return self.freemium_manager.get_subscription_status(user_id)

# Instance du service
subscription_service = SubscriptionService()

@subscription_bp.route('/api/subscription/status', methods=['GET'])
def get_subscription_status():
    """Récupère le statut d'abonnement de l'utilisateur"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id requis'}), 400
        
        status = subscription_service.get_user_status(user_id)
        
        return jsonify({
            'success': True,
            'data': status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/api/subscription/plans', methods=['GET'])
def get_subscription_plans():
    """Récupère tous les plans d'abonnement disponibles"""
    try:
        plans = subscription_service.get_subscription_plans()
        
        return jsonify({
            'success': True,
            'data': plans
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/api/subscription/check-audit', methods=['POST'])
def check_audit_permission():
    """Vérifie si l'utilisateur peut effectuer un audit"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id requis'}), 400
        
        can_audit, message, status = subscription_service.check_audit_permission(user_id)
        
        return jsonify({
            'success': True,
            'can_audit': can_audit,
            'message': message,
            'subscription_status': status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/api/subscription/perform-audit', methods=['POST'])
def perform_audit():
    """Effectue un audit pour l'utilisateur"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id requis'}), 400
        
        success, message, status = subscription_service.perform_audit(user_id)
        
        return jsonify({
            'success': success,
            'message': message,
            'subscription_status': status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/api/subscription/upgrade', methods=['POST'])
def upgrade_subscription():
    """Met à niveau l'abonnement de l'utilisateur"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        plan_type = data.get('plan_type')
        payment_info = data.get('payment_info', {})
        
        if not user_id or not plan_type:
            return jsonify({'error': 'user_id et plan_type requis'}), 400
        
        success, message = subscription_service.upgrade_subscription(user_id, plan_type, payment_info)
        
        if success:
            status = subscription_service.get_user_status(user_id)
            return jsonify({
                'success': True,
                'message': message,
                'subscription_status': status
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/api/subscription/simulate-payment', methods=['POST'])
def simulate_payment():
    """Simule un paiement pour les tests"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        plan_type = data.get('plan_type')
        amount = data.get('amount')
        
        if not all([user_id, plan_type, amount]):
            return jsonify({'error': 'user_id, plan_type et amount requis'}), 400
        
        # Simulation d'un paiement réussi
        # En production, ici on intégrerait une vraie passerelle de paiement
        
        success, message = subscription_service.upgrade_subscription(user_id, plan_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Paiement simulé avec succès',
                'transaction_id': f'sim_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'subscription_message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erreur lors de l\'activation: {message}'
            }), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_subscription_blueprint():
    """Retourne le blueprint des abonnements"""
    return subscription_bp

