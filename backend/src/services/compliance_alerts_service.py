"""
Service d'alertes de non-conformité
Gère les alertes en temps réel et les notifications de conformité réglementaire
"""

import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict, deque
import threading
import time


class AlertType(Enum):
    """Types d'alertes"""
    COMPLIANCE_VIOLATION = "compliance_violation"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    DEADLINE_APPROACHING = "deadline_approaching"
    PATTERN_ANOMALY = "pattern_anomaly"
    REGULATORY_UPDATE = "regulatory_update"
    SYSTEM_ERROR = "system_error"


class AlertPriority(Enum):
    """Priorités d'alertes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Statuts d'alertes"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class NotificationChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    DASHBOARD = "dashboard"
    WEBHOOK = "webhook"
    SLACK = "slack"


@dataclass
class ComplianceAlert:
    """Alerte de conformité"""
    alert_id: str
    alert_type: AlertType
    priority: AlertPriority
    status: AlertStatus
    title: str
    description: str
    source: str
    affected_entities: List[str]
    compliance_standard: str
    rule_id: str
    violation_details: Dict[str, Any]
    remediation_actions: List[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class AlertRule:
    """Règle d'alerte"""
    rule_id: str
    name: str
    description: str
    alert_type: AlertType
    priority: AlertPriority
    conditions: Dict[str, Any]
    notification_channels: List[NotificationChannel]
    cooldown_minutes: int = 60
    is_active: bool = True
    created_by: str = "system"
    created_at: datetime = None


@dataclass
class NotificationTemplate:
    """Template de notification"""
    template_id: str
    channel: NotificationChannel
    alert_type: AlertType
    subject_template: str
    body_template: str
    variables: List[str]


class ComplianceAlertsService:
    """Service d'alertes de conformité"""
    
    def __init__(self):
        self.alerts = {}  # alert_id -> ComplianceAlert
        self.alert_rules = {}  # rule_id -> AlertRule
        self.notification_templates = {}  # template_id -> NotificationTemplate
        self.alert_history = deque(maxlen=10000)  # Historique des alertes
        self.subscribers = defaultdict(list)  # channel -> [callback]
        self.alert_counters = defaultdict(int)
        self.last_alert_times = {}  # rule_id -> datetime (pour cooldown)
        
        # Configuration
        self.config = {
            'max_alerts_per_hour': 100,
            'default_cooldown_minutes': 60,
            'auto_resolve_after_days': 30,
            'notification_retry_attempts': 3,
            'batch_notification_size': 50
        }
        
        # Initialiser les règles et templates par défaut
        self._initialize_default_alert_rules()
        self._initialize_notification_templates()
        
        # Démarrer le thread de maintenance
        self._start_maintenance_thread()
    
    def _initialize_default_alert_rules(self):
        """Initialise les règles d'alerte par défaut"""
        
        default_rules = [
            AlertRule(
                rule_id="CRITICAL_COMPLIANCE_VIOLATION",
                name="Violation critique de conformité",
                description="Alerte pour les violations critiques de conformité réglementaire",
                alert_type=AlertType.COMPLIANCE_VIOLATION,
                priority=AlertPriority.CRITICAL,
                conditions={
                    "severity": "critical",
                    "standards": ["ifrs", "syscohada", "french_gaap"]
                },
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown_minutes=0,  # Pas de cooldown pour les violations critiques
                created_at=datetime.now()
            ),
            AlertRule(
                rule_id="HIGH_COMPLIANCE_VIOLATION",
                name="Violation importante de conformité",
                description="Alerte pour les violations importantes de conformité",
                alert_type=AlertType.COMPLIANCE_VIOLATION,
                priority=AlertPriority.HIGH,
                conditions={
                    "severity": "error",
                    "standards": ["ifrs", "syscohada", "french_gaap"]
                },
                notification_channels=[NotificationChannel.DASHBOARD],
                cooldown_minutes=30,
                created_at=datetime.now()
            ),
            AlertRule(
                rule_id="DEADLINE_APPROACHING",
                name="Échéance approchant",
                description="Alerte pour les échéances de conformité approchant",
                alert_type=AlertType.DEADLINE_APPROACHING,
                priority=AlertPriority.MEDIUM,
                conditions={
                    "days_before": 7,
                    "deadline_types": ["audit", "declaration", "reporting"]
                },
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown_minutes=1440,  # 24 heures
                created_at=datetime.now()
            ),
            AlertRule(
                rule_id="PATTERN_ANOMALY",
                name="Anomalie de pattern",
                description="Alerte pour les anomalies détectées dans les patterns comptables",
                alert_type=AlertType.PATTERN_ANOMALY,
                priority=AlertPriority.MEDIUM,
                conditions={
                    "anomaly_score_threshold": 0.8,
                    "pattern_types": ["temporal", "amount", "frequency"]
                },
                notification_channels=[NotificationChannel.DASHBOARD],
                cooldown_minutes=120,
                created_at=datetime.now()
            ),
            AlertRule(
                rule_id="THRESHOLD_EXCEEDED",
                name="Seuil dépassé",
                description="Alerte pour les seuils de conformité dépassés",
                alert_type=AlertType.THRESHOLD_EXCEEDED,
                priority=AlertPriority.HIGH,
                conditions={
                    "threshold_types": ["amount", "frequency", "ratio"],
                    "deviation_percentage": 20
                },
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown_minutes=60,
                created_at=datetime.now()
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_notification_templates(self):
        """Initialise les templates de notification"""
        
        templates = [
            NotificationTemplate(
                template_id="EMAIL_CRITICAL_VIOLATION",
                channel=NotificationChannel.EMAIL,
                alert_type=AlertType.COMPLIANCE_VIOLATION,
                subject_template="🚨 URGENT: Violation critique de conformité - {standard}",
                body_template="""
Bonjour,

Une violation critique de conformité a été détectée:

📋 **Détails de l'alerte:**
- Type: {alert_type}
- Norme: {standard}
- Règle: {rule_id}
- Priorité: {priority}

📝 **Description:**
{description}

🎯 **Entités affectées:**
{affected_entities}

⚠️ **Détails de la violation:**
{violation_details}

🔧 **Actions correctives recommandées:**
{remediation_actions}

📅 **Créée le:** {created_at}
📅 **Échéance:** {due_date}

Veuillez traiter cette alerte en priorité.

Cordialement,
Système ZenCompta
                """,
                variables=["standard", "alert_type", "rule_id", "priority", "description", 
                          "affected_entities", "violation_details", "remediation_actions", 
                          "created_at", "due_date"]
            ),
            NotificationTemplate(
                template_id="DASHBOARD_COMPLIANCE_VIOLATION",
                channel=NotificationChannel.DASHBOARD,
                alert_type=AlertType.COMPLIANCE_VIOLATION,
                subject_template="Violation de conformité {standard}",
                body_template="{description} - Entités: {affected_entities}",
                variables=["standard", "description", "affected_entities"]
            ),
            NotificationTemplate(
                template_id="EMAIL_DEADLINE_APPROACHING",
                channel=NotificationChannel.EMAIL,
                alert_type=AlertType.DEADLINE_APPROACHING,
                subject_template="⏰ Échéance approchant: {title}",
                body_template="""
Bonjour,

Une échéance de conformité approche:

📅 **Échéance:** {due_date}
📋 **Type:** {alert_type}
📝 **Description:** {description}

🎯 **Entités concernées:**
{affected_entities}

🔧 **Actions à effectuer:**
{remediation_actions}

Merci de prendre les dispositions nécessaires.

Cordialement,
Système ZenCompta
                """,
                variables=["title", "due_date", "alert_type", "description", 
                          "affected_entities", "remediation_actions"]
            )
        ]
        
        for template in templates:
            self.notification_templates[template.template_id] = template
    
    def create_alert(self, alert_data: Dict[str, Any]) -> str:
        """
        Crée une nouvelle alerte
        
        Args:
            alert_data: Données de l'alerte
            
        Returns:
            ID de l'alerte créée
        """
        try:
            alert_id = str(uuid.uuid4())
            
            # Créer l'alerte
            alert = ComplianceAlert(
                alert_id=alert_id,
                alert_type=AlertType(alert_data.get('alert_type', 'compliance_violation')),
                priority=AlertPriority(alert_data.get('priority', 'medium')),
                status=AlertStatus.ACTIVE,
                title=alert_data.get('title', ''),
                description=alert_data.get('description', ''),
                source=alert_data.get('source', 'system'),
                affected_entities=alert_data.get('affected_entities', []),
                compliance_standard=alert_data.get('compliance_standard', ''),
                rule_id=alert_data.get('rule_id', ''),
                violation_details=alert_data.get('violation_details', {}),
                remediation_actions=alert_data.get('remediation_actions', []),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=alert_data.get('due_date'),
                assigned_to=alert_data.get('assigned_to'),
                tags=alert_data.get('tags', []),
                metadata=alert_data.get('metadata', {})
            )
            
            # Stocker l'alerte
            self.alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Incrémenter les compteurs
            self.alert_counters[alert.alert_type.value] += 1
            self.alert_counters[f"{alert.priority.value}_priority"] += 1
            
            # Déclencher les notifications
            self._trigger_notifications(alert)
            
            return alert_id
            
        except Exception as e:
            raise Exception(f"Erreur création alerte: {str(e)}")
    
    def process_compliance_violations(self, violations: List[Dict]) -> List[str]:
        """
        Traite une liste de violations de conformité et crée les alertes appropriées
        
        Args:
            violations: Liste des violations détectées
            
        Returns:
            Liste des IDs d'alertes créées
        """
        alert_ids = []
        
        try:
            for violation in violations:
                # Déterminer la priorité basée sur la sévérité
                severity = violation.get('severity', 'warning')
                priority_mapping = {
                    'critical': AlertPriority.CRITICAL,
                    'error': AlertPriority.HIGH,
                    'warning': AlertPriority.MEDIUM,
                    'info': AlertPriority.LOW
                }
                priority = priority_mapping.get(severity, AlertPriority.MEDIUM)
                
                # Vérifier les règles d'alerte applicables
                applicable_rules = self._find_applicable_alert_rules(
                    AlertType.COMPLIANCE_VIOLATION, 
                    {'severity': severity}
                )
                
                for rule in applicable_rules:
                    # Vérifier le cooldown
                    if self._is_in_cooldown(rule.rule_id):
                        continue
                    
                    # Créer l'alerte
                    alert_data = {
                        'alert_type': AlertType.COMPLIANCE_VIOLATION.value,
                        'priority': priority.value,
                        'title': f"Violation {severity}: {violation.get('title', '')}",
                        'description': violation.get('description', ''),
                        'source': 'compliance_engine',
                        'affected_entities': violation.get('affected_entries', []),
                        'compliance_standard': violation.get('standard', ''),
                        'rule_id': violation.get('rule_id', ''),
                        'violation_details': {
                            'severity': severity,
                            'expected_value': violation.get('expected_value'),
                            'actual_value': violation.get('actual_value'),
                            'references': violation.get('references', [])
                        },
                        'remediation_actions': violation.get('remediation_steps', []),
                        'tags': ['compliance', severity, violation.get('standard', '')]
                    }
                    
                    alert_id = self.create_alert(alert_data)
                    alert_ids.append(alert_id)
                    
                    # Mettre à jour le temps de dernière alerte
                    self.last_alert_times[rule.rule_id] = datetime.now()
        
        except Exception as e:
            print(f"Erreur traitement violations: {e}")
        
        return alert_ids
    
    def create_deadline_alert(self, deadline_info: Dict) -> str:
        """
        Crée une alerte pour une échéance approchant
        
        Args:
            deadline_info: Informations sur l'échéance
            
        Returns:
            ID de l'alerte créée
        """
        try:
            due_date = deadline_info.get('due_date')
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date)
            
            days_until_deadline = (due_date - datetime.now()).days
            
            # Déterminer la priorité basée sur l'urgence
            if days_until_deadline <= 1:
                priority = AlertPriority.CRITICAL
            elif days_until_deadline <= 3:
                priority = AlertPriority.HIGH
            elif days_until_deadline <= 7:
                priority = AlertPriority.MEDIUM
            else:
                priority = AlertPriority.LOW
            
            alert_data = {
                'alert_type': AlertType.DEADLINE_APPROACHING.value,
                'priority': priority.value,
                'title': f"Échéance dans {days_until_deadline} jour(s): {deadline_info.get('title', '')}",
                'description': deadline_info.get('description', ''),
                'source': 'deadline_monitor',
                'affected_entities': deadline_info.get('affected_entities', []),
                'compliance_standard': deadline_info.get('standard', ''),
                'rule_id': deadline_info.get('rule_id', ''),
                'violation_details': {
                    'deadline_type': deadline_info.get('type', ''),
                    'days_remaining': days_until_deadline,
                    'due_date': due_date.isoformat()
                },
                'remediation_actions': deadline_info.get('required_actions', []),
                'due_date': due_date,
                'tags': ['deadline', deadline_info.get('type', ''), f"{days_until_deadline}_days"]
            }
            
            return self.create_alert(alert_data)
            
        except Exception as e:
            raise Exception(f"Erreur création alerte échéance: {str(e)}")
    
    def create_anomaly_alert(self, anomaly_data: Dict) -> str:
        """
        Crée une alerte pour une anomalie détectée
        
        Args:
            anomaly_data: Données de l'anomalie
            
        Returns:
            ID de l'alerte créée
        """
        try:
            anomaly_score = anomaly_data.get('anomaly_score', 0.0)
            
            # Déterminer la priorité basée sur le score d'anomalie
            if anomaly_score >= 0.9:
                priority = AlertPriority.CRITICAL
            elif anomaly_score >= 0.7:
                priority = AlertPriority.HIGH
            elif anomaly_score >= 0.5:
                priority = AlertPriority.MEDIUM
            else:
                priority = AlertPriority.LOW
            
            alert_data = {
                'alert_type': AlertType.PATTERN_ANOMALY.value,
                'priority': priority.value,
                'title': f"Anomalie détectée: {anomaly_data.get('description', '')}",
                'description': anomaly_data.get('detailed_description', ''),
                'source': 'anomaly_detector',
                'affected_entities': anomaly_data.get('affected_entries', []),
                'compliance_standard': '',
                'rule_id': anomaly_data.get('detection_rule', ''),
                'violation_details': {
                    'anomaly_type': anomaly_data.get('type', ''),
                    'anomaly_score': anomaly_score,
                    'contributing_factors': anomaly_data.get('contributing_factors', []),
                    'similar_cases': anomaly_data.get('similar_cases', [])
                },
                'remediation_actions': anomaly_data.get('recommendations', []),
                'tags': ['anomaly', anomaly_data.get('type', ''), f"score_{int(anomaly_score*100)}"]
            }
            
            return self.create_alert(alert_data)
            
        except Exception as e:
            raise Exception(f"Erreur création alerte anomalie: {str(e)}")
    
    def get_alerts(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """
        Récupère les alertes selon les filtres
        
        Args:
            filters: Filtres à appliquer
            limit: Nombre maximum d'alertes à retourner
            
        Returns:
            Liste des alertes filtrées
        """
        try:
            alerts = list(self.alerts.values())
            
            # Appliquer les filtres
            if filters:
                if 'status' in filters:
                    status_filter = AlertStatus(filters['status'])
                    alerts = [a for a in alerts if a.status == status_filter]
                
                if 'priority' in filters:
                    priority_filter = AlertPriority(filters['priority'])
                    alerts = [a for a in alerts if a.priority == priority_filter]
                
                if 'alert_type' in filters:
                    type_filter = AlertType(filters['alert_type'])
                    alerts = [a for a in alerts if a.alert_type == type_filter]
                
                if 'standard' in filters:
                    standard = filters['standard']
                    alerts = [a for a in alerts if a.compliance_standard == standard]
                
                if 'assigned_to' in filters:
                    assigned_to = filters['assigned_to']
                    alerts = [a for a in alerts if a.assigned_to == assigned_to]
                
                if 'created_after' in filters:
                    created_after = datetime.fromisoformat(filters['created_after'])
                    alerts = [a for a in alerts if a.created_at >= created_after]
                
                if 'tags' in filters:
                    required_tags = filters['tags']
                    if isinstance(required_tags, str):
                        required_tags = [required_tags]
                    alerts = [a for a in alerts if any(tag in (a.tags or []) for tag in required_tags)]
            
            # Trier par priorité et date de création
            priority_order = {
                AlertPriority.CRITICAL: 4,
                AlertPriority.HIGH: 3,
                AlertPriority.MEDIUM: 2,
                AlertPriority.LOW: 1
            }
            
            alerts.sort(key=lambda x: (priority_order[x.priority], x.created_at), reverse=True)
            
            # Limiter le nombre de résultats
            alerts = alerts[:limit]
            
            # Convertir en dictionnaires
            return [asdict(alert) for alert in alerts]
            
        except Exception as e:
            raise Exception(f"Erreur récupération alertes: {str(e)}")
    
    def update_alert_status(self, alert_id: str, new_status: str, 
                           updated_by: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """
        Met à jour le statut d'une alerte
        
        Args:
            alert_id: ID de l'alerte
            new_status: Nouveau statut
            updated_by: Utilisateur qui effectue la mise à jour
            notes: Notes optionnelles
            
        Returns:
            True si la mise à jour a réussi
        """
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            old_status = alert.status
            alert.status = AlertStatus(new_status)
            alert.updated_at = datetime.now()
            
            # Ajouter les métadonnées de mise à jour
            if not alert.metadata:
                alert.metadata = {}
            
            alert.metadata['status_history'] = alert.metadata.get('status_history', [])
            alert.metadata['status_history'].append({
                'from_status': old_status.value,
                'to_status': new_status,
                'updated_by': updated_by,
                'updated_at': alert.updated_at.isoformat(),
                'notes': notes
            })
            
            # Déclencher les notifications si nécessaire
            if new_status in ['resolved', 'dismissed']:
                self._notify_alert_resolution(alert, updated_by)
            
            return True
            
        except Exception as e:
            print(f"Erreur mise à jour statut alerte: {e}")
            return False
    
    def assign_alert(self, alert_id: str, assigned_to: str, assigned_by: Optional[str] = None) -> bool:
        """
        Assigne une alerte à un utilisateur
        
        Args:
            alert_id: ID de l'alerte
            assigned_to: Utilisateur assigné
            assigned_by: Utilisateur qui effectue l'assignation
            
        Returns:
            True si l'assignation a réussi
        """
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            old_assigned = alert.assigned_to
            alert.assigned_to = assigned_to
            alert.updated_at = datetime.now()
            
            # Ajouter les métadonnées d'assignation
            if not alert.metadata:
                alert.metadata = {}
            
            alert.metadata['assignment_history'] = alert.metadata.get('assignment_history', [])
            alert.metadata['assignment_history'].append({
                'from_user': old_assigned,
                'to_user': assigned_to,
                'assigned_by': assigned_by,
                'assigned_at': alert.updated_at.isoformat()
            })
            
            # Notifier l'utilisateur assigné
            self._notify_alert_assignment(alert, assigned_to, assigned_by)
            
            return True
            
        except Exception as e:
            print(f"Erreur assignation alerte: {e}")
            return False
    
    def get_alert_statistics(self, period_days: int = 30) -> Dict:
        """
        Calcule les statistiques des alertes
        
        Args:
            period_days: Période en jours pour les statistiques
            
        Returns:
            Dict contenant les statistiques
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_alerts = [a for a in self.alerts.values() if a.created_at >= cutoff_date]
            
            stats = {
                'total_alerts': len(recent_alerts),
                'by_status': defaultdict(int),
                'by_priority': defaultdict(int),
                'by_type': defaultdict(int),
                'by_standard': defaultdict(int),
                'resolution_time': {
                    'average_hours': 0.0,
                    'median_hours': 0.0
                },
                'trends': {
                    'daily_counts': defaultdict(int),
                    'weekly_counts': defaultdict(int)
                }
            }
            
            resolution_times = []
            
            for alert in recent_alerts:
                # Compter par statut
                stats['by_status'][alert.status.value] += 1
                
                # Compter par priorité
                stats['by_priority'][alert.priority.value] += 1
                
                # Compter par type
                stats['by_type'][alert.alert_type.value] += 1
                
                # Compter par norme
                if alert.compliance_standard:
                    stats['by_standard'][alert.compliance_standard] += 1
                
                # Calculer le temps de résolution
                if alert.status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED]:
                    resolution_time = (alert.updated_at - alert.created_at).total_seconds() / 3600
                    resolution_times.append(resolution_time)
                
                # Tendances quotidiennes
                day_key = alert.created_at.strftime('%Y-%m-%d')
                stats['trends']['daily_counts'][day_key] += 1
                
                # Tendances hebdomadaires
                week_key = alert.created_at.strftime('%Y-W%U')
                stats['trends']['weekly_counts'][week_key] += 1
            
            # Calculer les temps de résolution moyens
            if resolution_times:
                stats['resolution_time']['average_hours'] = sum(resolution_times) / len(resolution_times)
                stats['resolution_time']['median_hours'] = sorted(resolution_times)[len(resolution_times) // 2]
            
            # Convertir les defaultdict en dict normaux
            stats['by_status'] = dict(stats['by_status'])
            stats['by_priority'] = dict(stats['by_priority'])
            stats['by_type'] = dict(stats['by_type'])
            stats['by_standard'] = dict(stats['by_standard'])
            stats['trends']['daily_counts'] = dict(stats['trends']['daily_counts'])
            stats['trends']['weekly_counts'] = dict(stats['trends']['weekly_counts'])
            
            return stats
            
        except Exception as e:
            raise Exception(f"Erreur calcul statistiques: {str(e)}")
    
    def _find_applicable_alert_rules(self, alert_type: AlertType, context: Dict) -> List[AlertRule]:
        """Trouve les règles d'alerte applicables"""
        applicable_rules = []
        
        for rule in self.alert_rules.values():
            if not rule.is_active:
                continue
            
            if rule.alert_type != alert_type:
                continue
            
            # Vérifier les conditions
            conditions_met = True
            for condition_key, condition_value in rule.conditions.items():
                if condition_key in context:
                    if isinstance(condition_value, list):
                        if context[condition_key] not in condition_value:
                            conditions_met = False
                            break
                    else:
                        if context[condition_key] != condition_value:
                            conditions_met = False
                            break
            
            if conditions_met:
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Vérifie si une règle est en période de cooldown"""
        if rule_id not in self.last_alert_times:
            return False
        
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        last_alert_time = self.last_alert_times[rule_id]
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() - last_alert_time < cooldown_period
    
    def _trigger_notifications(self, alert: ComplianceAlert):
        """Déclenche les notifications pour une alerte"""
        try:
            # Trouver les règles d'alerte applicables
            applicable_rules = self._find_applicable_alert_rules(
                alert.alert_type, 
                {'severity': alert.violation_details.get('severity', '')}
            )
            
            # Envoyer les notifications selon les canaux configurés
            for rule in applicable_rules:
                for channel in rule.notification_channels:
                    self._send_notification(alert, channel)
        
        except Exception as e:
            print(f"Erreur déclenchement notifications: {e}")
    
    def _send_notification(self, alert: ComplianceAlert, channel: NotificationChannel):
        """Envoie une notification sur un canal spécifique"""
        try:
            # Trouver le template approprié
            template = self._find_notification_template(alert.alert_type, channel)
            
            if not template:
                print(f"Aucun template trouvé pour {alert.alert_type.value} sur {channel.value}")
                return
            
            # Préparer les variables pour le template
            variables = {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type.value,
                'priority': alert.priority.value,
                'title': alert.title,
                'description': alert.description,
                'standard': alert.compliance_standard,
                'rule_id': alert.rule_id,
                'affected_entities': ', '.join(alert.affected_entities),
                'violation_details': json.dumps(alert.violation_details, indent=2),
                'remediation_actions': '\n'.join(f"- {action}" for action in alert.remediation_actions),
                'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'due_date': alert.due_date.strftime('%Y-%m-%d %H:%M:%S') if alert.due_date else 'Non définie'
            }
            
            # Formater le message
            subject = template.subject_template.format(**variables)
            body = template.body_template.format(**variables)
            
            # Envoyer selon le canal
            if channel == NotificationChannel.EMAIL:
                self._send_email_notification(alert, subject, body)
            elif channel == NotificationChannel.DASHBOARD:
                self._send_dashboard_notification(alert, subject, body)
            elif channel == NotificationChannel.WEBHOOK:
                self._send_webhook_notification(alert, subject, body)
            # Ajouter d'autres canaux selon les besoins
            
        except Exception as e:
            print(f"Erreur envoi notification {channel.value}: {e}")
    
    def _find_notification_template(self, alert_type: AlertType, channel: NotificationChannel) -> Optional[NotificationTemplate]:
        """Trouve le template de notification approprié"""
        for template in self.notification_templates.values():
            if template.alert_type == alert_type and template.channel == channel:
                return template
        return None
    
    def _send_email_notification(self, alert: ComplianceAlert, subject: str, body: str):
        """Envoie une notification par email (simulation)"""
        # En production, intégrer avec un service d'email
        print(f"📧 EMAIL NOTIFICATION:")
        print(f"To: compliance-team@company.com")
        print(f"Subject: {subject}")
        print(f"Body: {body[:200]}...")
    
    def _send_dashboard_notification(self, alert: ComplianceAlert, subject: str, body: str):
        """Envoie une notification au dashboard"""
        # Notifier les abonnés du dashboard
        if NotificationChannel.DASHBOARD in self.subscribers:
            for callback in self.subscribers[NotificationChannel.DASHBOARD]:
                try:
                    callback({
                        'alert_id': alert.alert_id,
                        'subject': subject,
                        'body': body,
                        'priority': alert.priority.value,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Erreur callback dashboard: {e}")
    
    def _send_webhook_notification(self, alert: ComplianceAlert, subject: str, body: str):
        """Envoie une notification via webhook (simulation)"""
        # En production, faire un appel HTTP POST
        webhook_payload = {
            'alert_id': alert.alert_id,
            'alert_type': alert.alert_type.value,
            'priority': alert.priority.value,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now().isoformat()
        }
        print(f"🔗 WEBHOOK NOTIFICATION: {json.dumps(webhook_payload, indent=2)}")
    
    def _notify_alert_resolution(self, alert: ComplianceAlert, resolved_by: Optional[str]):
        """Notifie la résolution d'une alerte"""
        print(f"✅ Alerte {alert.alert_id} résolue par {resolved_by or 'système'}")
    
    def _notify_alert_assignment(self, alert: ComplianceAlert, assigned_to: str, assigned_by: Optional[str]):
        """Notifie l'assignation d'une alerte"""
        print(f"👤 Alerte {alert.alert_id} assignée à {assigned_to} par {assigned_by or 'système'}")
    
    def _start_maintenance_thread(self):
        """Démarre le thread de maintenance des alertes"""
        def maintenance_loop():
            while True:
                try:
                    self._cleanup_old_alerts()
                    self._auto_resolve_stale_alerts()
                    time.sleep(3600)  # Maintenance toutes les heures
                except Exception as e:
                    print(f"Erreur maintenance alertes: {e}")
                    time.sleep(300)  # Retry après 5 minutes en cas d'erreur
        
        maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        maintenance_thread.start()
    
    def _cleanup_old_alerts(self):
        """Nettoie les anciennes alertes résolues"""
        cutoff_date = datetime.now() - timedelta(days=self.config['auto_resolve_after_days'])
        
        alerts_to_remove = []
        for alert_id, alert in self.alerts.items():
            if (alert.status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED] and 
                alert.updated_at < cutoff_date):
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
    
    def _auto_resolve_stale_alerts(self):
        """Résout automatiquement les alertes obsolètes"""
        cutoff_date = datetime.now() - timedelta(days=self.config['auto_resolve_after_days'])
        
        for alert in self.alerts.values():
            if (alert.status == AlertStatus.ACTIVE and 
                alert.created_at < cutoff_date and
                alert.priority == AlertPriority.LOW):
                alert.status = AlertStatus.RESOLVED
                alert.updated_at = datetime.now()
                if not alert.metadata:
                    alert.metadata = {}
                alert.metadata['auto_resolved'] = True
                alert.metadata['auto_resolved_reason'] = 'Alerte obsolète (résolution automatique)'
    
    def subscribe_to_notifications(self, channel: NotificationChannel, callback: Callable):
        """S'abonne aux notifications d'un canal"""
        self.subscribers[channel].append(callback)
    
    def unsubscribe_from_notifications(self, channel: NotificationChannel, callback: Callable):
        """Se désabonne des notifications d'un canal"""
        if callback in self.subscribers[channel]:
            self.subscribers[channel].remove(callback)
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Ajoute une nouvelle règle d'alerte"""
        try:
            self.alert_rules[rule.rule_id] = rule
            return True
        except Exception:
            return False
    
    def update_alert_rule(self, rule_id: str, updates: Dict) -> bool:
        """Met à jour une règle d'alerte"""
        try:
            if rule_id not in self.alert_rules:
                return False
            
            rule = self.alert_rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            return True
        except Exception:
            return False
    
    def get_alert_rules(self) -> List[Dict]:
        """Retourne la liste des règles d'alerte"""
        return [asdict(rule) for rule in self.alert_rules.values()]
    
    def test_alert_system(self) -> Dict:
        """Teste le système d'alertes"""
        try:
            # Créer une alerte de test
            test_alert_data = {
                'alert_type': AlertType.COMPLIANCE_VIOLATION.value,
                'priority': AlertPriority.MEDIUM.value,
                'title': 'Test d\'alerte système',
                'description': 'Alerte de test pour vérifier le fonctionnement du système',
                'source': 'test_system',
                'affected_entities': ['TEST_001'],
                'compliance_standard': 'test_standard',
                'rule_id': 'TEST_RULE',
                'violation_details': {'test': True},
                'remediation_actions': ['Action de test'],
                'tags': ['test']
            }
            
            alert_id = self.create_alert(test_alert_data)
            
            # Tester la mise à jour de statut
            status_updated = self.update_alert_status(alert_id, AlertStatus.RESOLVED.value, 'test_user')
            
            return {
                'success': True,
                'test_alert_id': alert_id,
                'status_update_success': status_updated,
                'total_alerts': len(self.alerts),
                'total_rules': len(self.alert_rules),
                'message': 'Système d\'alertes fonctionnel'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Erreur test système alertes: {str(e)}"
            }

