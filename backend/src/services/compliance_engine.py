"""
Moteur de règles de conformité réglementaire
Gère la validation selon différentes normes comptables (IFRS, SYSCOHADA, etc.)
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from collections import defaultdict


class ComplianceStandard(Enum):
    """Normes comptables supportées"""
    IFRS = "ifrs"
    SYSCOHADA = "syscohada"
    FRENCH_GAAP = "french_gaap"
    US_GAAP = "us_gaap"
    OHADA = "ohada"


class ViolationSeverity(Enum):
    """Niveaux de sévérité des violations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleCategory(Enum):
    """Catégories de règles"""
    STRUCTURE = "structure"
    VALUATION = "valuation"
    PRESENTATION = "presentation"
    DISCLOSURE = "disclosure"
    RECOGNITION = "recognition"
    MEASUREMENT = "measurement"


@dataclass
class ComplianceRule:
    """Règle de conformité"""
    rule_id: str
    standard: ComplianceStandard
    category: RuleCategory
    title: str
    description: str
    severity: ViolationSeverity
    validation_function: str
    parameters: Dict[str, Any]
    references: List[str]
    applicable_accounts: List[str] = None
    effective_date: datetime = None
    expiry_date: datetime = None


@dataclass
class ComplianceViolation:
    """Violation de conformité détectée"""
    rule_id: str
    violation_id: str
    severity: ViolationSeverity
    title: str
    description: str
    affected_entries: List[str]
    expected_value: Any = None
    actual_value: Any = None
    remediation_steps: List[str] = None
    references: List[str] = None
    detected_at: datetime = None


class ComplianceEngine:
    """Moteur de conformité réglementaire"""
    
    def __init__(self):
        self.rules = {}
        self.standards_config = {}
        self.validation_functions = {}
        
        # Initialiser les règles par défaut
        self._initialize_default_rules()
        self._register_validation_functions()
    
    def _initialize_default_rules(self):
        """Initialise les règles de conformité par défaut"""
        
        # Règles IFRS
        ifrs_rules = [
            ComplianceRule(
                rule_id="IFRS_001",
                standard=ComplianceStandard.IFRS,
                category=RuleCategory.STRUCTURE,
                title="Plan comptable conforme IFRS",
                description="Les comptes doivent respecter la structure IFRS",
                severity=ViolationSeverity.ERROR,
                validation_function="validate_ifrs_chart_of_accounts",
                parameters={"required_classes": ["1", "2", "3", "4", "5"]},
                references=["IAS 1 - Présentation des états financiers"]
            ),
            ComplianceRule(
                rule_id="IFRS_002",
                standard=ComplianceStandard.IFRS,
                category=RuleCategory.VALUATION,
                title="Évaluation à la juste valeur",
                description="Certains actifs doivent être évalués à la juste valeur",
                severity=ViolationSeverity.WARNING,
                validation_function="validate_fair_value_measurement",
                parameters={"fair_value_accounts": ["26", "27", "50"]},
                references=["IFRS 13 - Évaluation de la juste valeur"]
            ),
            ComplianceRule(
                rule_id="IFRS_003",
                standard=ComplianceStandard.IFRS,
                category=RuleCategory.RECOGNITION,
                title="Reconnaissance des revenus",
                description="Les revenus doivent être reconnus selon IFRS 15",
                severity=ViolationSeverity.ERROR,
                validation_function="validate_revenue_recognition",
                parameters={"revenue_accounts": ["70", "71", "72", "73", "74", "75"]},
                references=["IFRS 15 - Produits des activités ordinaires tirés de contrats avec des clients"]
            )
        ]
        
        # Règles SYSCOHADA
        syscohada_rules = [
            ComplianceRule(
                rule_id="SYSCOHADA_001",
                standard=ComplianceStandard.SYSCOHADA,
                category=RuleCategory.STRUCTURE,
                title="Plan comptable SYSCOHADA",
                description="Respect du plan comptable SYSCOHADA révisé",
                severity=ViolationSeverity.ERROR,
                validation_function="validate_syscohada_chart",
                parameters={"syscohada_classes": ["1", "2", "3", "4", "5", "6", "7", "8"]},
                references=["Acte uniforme OHADA - Plan comptable général"]
            ),
            ComplianceRule(
                rule_id="SYSCOHADA_002",
                standard=ComplianceStandard.SYSCOHADA,
                category=RuleCategory.PRESENTATION,
                title="États financiers SYSCOHADA",
                description="Présentation conforme aux modèles SYSCOHADA",
                severity=ViolationSeverity.ERROR,
                validation_function="validate_syscohada_financial_statements",
                parameters={"required_statements": ["bilan", "compte_resultat", "tafire"]},
                references=["Acte uniforme OHADA - États financiers"]
            ),
            ComplianceRule(
                rule_id="SYSCOHADA_003",
                standard=ComplianceStandard.SYSCOHADA,
                category=RuleCategory.VALUATION,
                title="Amortissements SYSCOHADA",
                description="Calcul des amortissements selon SYSCOHADA",
                severity=ViolationSeverity.WARNING,
                validation_function="validate_syscohada_depreciation",
                parameters={"depreciation_accounts": ["28", "29", "39", "48", "49", "59", "68"]},
                references=["Acte uniforme OHADA - Amortissements"]
            )
        ]
        
        # Règles comptabilité française
        french_gaap_rules = [
            ComplianceRule(
                rule_id="FR_GAAP_001",
                standard=ComplianceStandard.FRENCH_GAAP,
                category=RuleCategory.STRUCTURE,
                title="Plan comptable général français",
                description="Respect du PCG français",
                severity=ViolationSeverity.ERROR,
                validation_function="validate_french_chart_of_accounts",
                parameters={"pcg_classes": ["1", "2", "3", "4", "5", "6", "7"]},
                references=["Code de commerce - Plan comptable général"]
            ),
            ComplianceRule(
                rule_id="FR_GAAP_002",
                standard=ComplianceStandard.FRENCH_GAAP,
                category=RuleCategory.DISCLOSURE,
                title="Annexe comptable",
                description="Informations obligatoires en annexe",
                severity=ViolationSeverity.WARNING,
                validation_function="validate_french_notes_disclosure",
                parameters={"required_notes": ["methodes", "evenements", "engagements"]},
                references=["Code de commerce - Annexe comptable"]
            )
        ]
        
        # Enregistrer toutes les règles
        all_rules = ifrs_rules + syscohada_rules + french_gaap_rules
        
        for rule in all_rules:
            if rule.standard not in self.rules:
                self.rules[rule.standard] = {}
            self.rules[rule.standard][rule.rule_id] = rule
    
    def _register_validation_functions(self):
        """Enregistre les fonctions de validation"""
        self.validation_functions = {
            "validate_ifrs_chart_of_accounts": self._validate_ifrs_chart_of_accounts,
            "validate_fair_value_measurement": self._validate_fair_value_measurement,
            "validate_revenue_recognition": self._validate_revenue_recognition,
            "validate_syscohada_chart": self._validate_syscohada_chart,
            "validate_syscohada_financial_statements": self._validate_syscohada_financial_statements,
            "validate_syscohada_depreciation": self._validate_syscohada_depreciation,
            "validate_french_chart_of_accounts": self._validate_french_chart_of_accounts,
            "validate_french_notes_disclosure": self._validate_french_notes_disclosure,
            "validate_balance_equation": self._validate_balance_equation,
            "validate_account_ranges": self._validate_account_ranges,
            "validate_mandatory_accounts": self._validate_mandatory_accounts,
            "validate_depreciation_consistency": self._validate_depreciation_consistency,
            "validate_revenue_cut_off": self._validate_revenue_cut_off,
            "validate_inventory_valuation": self._validate_inventory_valuation
        }
    
    def validate_compliance(self, data: Dict, standard: ComplianceStandard, 
                          validation_config: Optional[Dict] = None) -> Dict:
        """
        Valide la conformité des données selon une norme
        
        Args:
            data: Données comptables à valider
            standard: Norme comptable à appliquer
            validation_config: Configuration de validation (optionnelle)
            
        Returns:
            Dict contenant les résultats de validation
        """
        result = {
            'success': True,
            'standard': standard.value,
            'validation_summary': {
                'total_rules_checked': 0,
                'violations_found': 0,
                'severity_distribution': {
                    'info': 0,
                    'warning': 0,
                    'error': 0,
                    'critical': 0
                }
            },
            'violations': [],
            'compliance_score': 0.0,
            'recommendations': [],
            'processing_time': 0.0
        }
        
        try:
            start_time = datetime.now()
            
            if standard not in self.rules:
                result['success'] = False
                result['error'] = f"Norme non supportée: {standard.value}"
                return result
            
            # Configuration de validation
            config = validation_config or {}
            enabled_categories = config.get('categories', list(RuleCategory))
            max_severity = config.get('max_severity', ViolationSeverity.INFO)
            
            violations = []
            rules_checked = 0
            
            # Appliquer les règles de la norme
            for rule_id, rule in self.rules[standard].items():
                # Vérifier si la règle doit être appliquée
                if not self._should_apply_rule(rule, config):
                    continue
                
                # Vérifier la catégorie
                if rule.category not in enabled_categories:
                    continue
                
                # Vérifier la sévérité
                if self._severity_level(rule.severity) > self._severity_level(max_severity):
                    continue
                
                rules_checked += 1
                
                # Exécuter la validation
                try:
                    rule_violations = self._execute_rule_validation(rule, data, config)
                    violations.extend(rule_violations)
                except Exception as e:
                    result['warnings'] = result.get('warnings', [])
                    result['warnings'].append(f"Erreur validation règle {rule_id}: {str(e)}")
            
            # Calculer les statistiques
            result['validation_summary']['total_rules_checked'] = rules_checked
            result['validation_summary']['violations_found'] = len(violations)
            
            for violation in violations:
                result['validation_summary']['severity_distribution'][violation.severity.value] += 1
            
            # Calculer le score de conformité
            if rules_checked > 0:
                compliance_score = max(0.0, 1.0 - (len(violations) / rules_checked))
                result['compliance_score'] = compliance_score
            
            # Convertir les violations en dictionnaires
            result['violations'] = [self._violation_to_dict(v) for v in violations]
            
            # Générer des recommandations
            result['recommendations'] = self._generate_compliance_recommendations(violations, standard)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur validation conformité: {str(e)}"
        
        return result
    
    def get_checklist(self, standard: ComplianceStandard, category: Optional[RuleCategory] = None) -> Dict:
        """
        Génère une check-list de conformité pour une norme
        
        Args:
            standard: Norme comptable
            category: Catégorie de règles (optionnelle)
            
        Returns:
            Dict contenant la check-list
        """
        checklist = {
            'standard': standard.value,
            'category': category.value if category else 'all',
            'checklist_items': [],
            'total_items': 0,
            'categories': {}
        }
        
        try:
            if standard not in self.rules:
                checklist['error'] = f"Norme non supportée: {standard.value}"
                return checklist
            
            # Filtrer les règles par catégorie si spécifiée
            rules_to_include = {}
            for rule_id, rule in self.rules[standard].items():
                if category is None or rule.category == category:
                    rules_to_include[rule_id] = rule
            
            # Grouper par catégorie
            categories = defaultdict(list)
            for rule_id, rule in rules_to_include.items():
                categories[rule.category.value].append({
                    'rule_id': rule_id,
                    'title': rule.title,
                    'description': rule.description,
                    'severity': rule.severity.value,
                    'references': rule.references,
                    'status': 'pending'  # À remplir lors de la validation
                })
            
            checklist['categories'] = dict(categories)
            checklist['total_items'] = len(rules_to_include)
            
            # Créer la liste plate pour faciliter l'utilisation
            for category_name, items in categories.items():
                checklist['checklist_items'].extend(items)
            
        except Exception as e:
            checklist['error'] = f"Erreur génération check-list: {str(e)}"
        
        return checklist
    
    def validate_real_time(self, entry_data: Dict, standard: ComplianceStandard) -> Dict:
        """
        Validation en temps réel d'une écriture comptable
        
        Args:
            entry_data: Données de l'écriture
            standard: Norme à appliquer
            
        Returns:
            Dict avec les alertes de conformité
        """
        result = {
            'is_compliant': True,
            'alerts': [],
            'warnings': [],
            'blocking_errors': [],
            'suggestions': []
        }
        
        try:
            if standard not in self.rules:
                result['is_compliant'] = False
                result['blocking_errors'].append(f"Norme non supportée: {standard.value}")
                return result
            
            # Valider les règles critiques en temps réel
            critical_rules = [
                rule for rule in self.rules[standard].values()
                if rule.severity in [ViolationSeverity.ERROR, ViolationSeverity.CRITICAL]
            ]
            
            for rule in critical_rules:
                try:
                    violations = self._execute_rule_validation(rule, {'entries': [entry_data]}, {})
                    
                    for violation in violations:
                        if violation.severity == ViolationSeverity.CRITICAL:
                            result['blocking_errors'].append(violation.description)
                            result['is_compliant'] = False
                        elif violation.severity == ViolationSeverity.ERROR:
                            result['alerts'].append(violation.description)
                        elif violation.severity == ViolationSeverity.WARNING:
                            result['warnings'].append(violation.description)
                
                except Exception as e:
                    result['warnings'].append(f"Erreur validation règle {rule.rule_id}: {str(e)}")
            
            # Générer des suggestions d'amélioration
            result['suggestions'] = self._generate_entry_suggestions(entry_data, standard)
            
        except Exception as e:
            result['is_compliant'] = False
            result['blocking_errors'].append(f"Erreur validation temps réel: {str(e)}")
        
        return result
    
    def _should_apply_rule(self, rule: ComplianceRule, config: Dict) -> bool:
        """Détermine si une règle doit être appliquée"""
        # Vérifier les dates d'effectivité
        current_date = datetime.now()
        
        if rule.effective_date and current_date < rule.effective_date:
            return False
        
        if rule.expiry_date and current_date > rule.expiry_date:
            return False
        
        # Vérifier les comptes applicables
        applicable_accounts = config.get('applicable_accounts', [])
        if rule.applicable_accounts and applicable_accounts:
            if not any(acc in rule.applicable_accounts for acc in applicable_accounts):
                return False
        
        return True
    
    def _severity_level(self, severity: ViolationSeverity) -> int:
        """Convertit la sévérité en niveau numérique"""
        levels = {
            ViolationSeverity.INFO: 1,
            ViolationSeverity.WARNING: 2,
            ViolationSeverity.ERROR: 3,
            ViolationSeverity.CRITICAL: 4
        }
        return levels.get(severity, 1)
    
    def _execute_rule_validation(self, rule: ComplianceRule, data: Dict, config: Dict) -> List[ComplianceViolation]:
        """Exécute la validation d'une règle"""
        violations = []
        
        try:
            validation_function = self.validation_functions.get(rule.validation_function)
            
            if not validation_function:
                return violations
            
            # Exécuter la fonction de validation
            rule_result = validation_function(data, rule.parameters, config)
            
            # Traiter les résultats
            if isinstance(rule_result, list):
                for violation_data in rule_result:
                    violation = ComplianceViolation(
                        rule_id=rule.rule_id,
                        violation_id=f"{rule.rule_id}_{len(violations)}",
                        severity=rule.severity,
                        title=rule.title,
                        description=violation_data.get('description', rule.description),
                        affected_entries=violation_data.get('affected_entries', []),
                        expected_value=violation_data.get('expected_value'),
                        actual_value=violation_data.get('actual_value'),
                        remediation_steps=violation_data.get('remediation_steps', []),
                        references=rule.references,
                        detected_at=datetime.now()
                    )
                    violations.append(violation)
            
        except Exception as e:
            # Créer une violation pour l'erreur de validation
            violation = ComplianceViolation(
                rule_id=rule.rule_id,
                violation_id=f"{rule.rule_id}_error",
                severity=ViolationSeverity.WARNING,
                title=f"Erreur validation {rule.title}",
                description=f"Impossible de valider la règle: {str(e)}",
                affected_entries=[],
                detected_at=datetime.now()
            )
            violations.append(violation)
        
        return violations
    
    # Fonctions de validation spécifiques
    
    def _validate_ifrs_chart_of_accounts(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la conformité du plan comptable IFRS"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            required_classes = parameters.get('required_classes', [])
            
            # Extraire les comptes utilisés
            accounts_used = set()
            for entry in entries:
                account = str(entry.get('account', ''))
                if account:
                    accounts_used.add(account[0])  # Premier chiffre = classe
            
            # Vérifier les classes manquantes
            missing_classes = set(required_classes) - accounts_used
            
            if missing_classes:
                violations.append({
                    'description': f"Classes de comptes IFRS manquantes: {', '.join(missing_classes)}",
                    'expected_value': required_classes,
                    'actual_value': list(accounts_used),
                    'remediation_steps': [
                        "Ajouter les comptes des classes manquantes",
                        "Vérifier la complétude du plan comptable IFRS"
                    ]
                })
            
            # Vérifier la structure des comptes
            for entry in entries:
                account = str(entry.get('account', ''))
                if account and not self._is_valid_ifrs_account(account):
                    violations.append({
                        'description': f"Compte non conforme IFRS: {account}",
                        'affected_entries': [str(entry.get('id', ''))],
                        'remediation_steps': [
                            "Corriger la numérotation du compte",
                            "Respecter la structure IFRS"
                        ]
                    })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation plan comptable IFRS: {str(e)}"
            })
        
        return violations
    
    def _validate_fair_value_measurement(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide l'évaluation à la juste valeur selon IFRS 13"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            fair_value_accounts = parameters.get('fair_value_accounts', [])
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                # Vérifier si le compte nécessite une évaluation à la juste valeur
                if any(account.startswith(fv_acc) for fv_acc in fair_value_accounts):
                    # Vérifier la présence d'informations sur la juste valeur
                    description = str(entry.get('description', '')).lower()
                    
                    if 'juste valeur' not in description and 'fair value' not in description:
                        violations.append({
                            'description': f"Compte {account} nécessite une évaluation à la juste valeur",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Documenter l'évaluation à la juste valeur",
                                "Appliquer IFRS 13",
                                "Indiquer le niveau de hiérarchie de juste valeur"
                            ]
                        })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation juste valeur: {str(e)}"
            })
        
        return violations
    
    def _validate_revenue_recognition(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la reconnaissance des revenus selon IFRS 15"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            revenue_accounts = parameters.get('revenue_accounts', [])
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                # Vérifier les comptes de revenus
                if any(account.startswith(rev_acc) for rev_acc in revenue_accounts):
                    description = str(entry.get('description', '')).lower()
                    
                    # Vérifier la documentation de la performance obligation
                    if 'contrat' not in description and 'client' not in description:
                        violations.append({
                            'description': f"Revenu {account} sans référence au contrat client",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Documenter l'obligation de performance",
                                "Référencer le contrat client",
                                "Appliquer le modèle IFRS 15 en 5 étapes"
                            ]
                        })
                    
                    # Vérifier les montants négatifs (annulations)
                    amount = float(entry.get('montant', 0))
                    if amount < 0:
                        violations.append({
                            'description': f"Revenu négatif détecté: {amount}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Vérifier la justification de l'annulation",
                                "Documenter les modifications de contrat"
                            ]
                        })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation reconnaissance revenus: {str(e)}"
            })
        
        return violations
    
    def _validate_syscohada_chart(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la conformité au plan comptable SYSCOHADA"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            syscohada_classes = parameters.get('syscohada_classes', [])
            
            # Vérifier la structure des comptes SYSCOHADA
            for entry in entries:
                account = str(entry.get('account', ''))
                
                if account:
                    # Vérifier la longueur (minimum 2 chiffres)
                    if len(account) < 2:
                        violations.append({
                            'description': f"Compte SYSCOHADA trop court: {account}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Utiliser au minimum 2 chiffres",
                                "Respecter la codification SYSCOHADA"
                            ]
                        })
                    
                    # Vérifier la classe
                    first_digit = account[0]
                    if first_digit not in syscohada_classes:
                        violations.append({
                            'description': f"Classe de compte non SYSCOHADA: {first_digit}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Utiliser les classes SYSCOHADA (1-8)",
                                "Vérifier le plan comptable OHADA"
                            ]
                        })
                    
                    # Vérifications spécifiques par classe
                    if first_digit == '1':  # Comptes de ressources durables
                        if len(account) >= 2 and account[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            violations.append({
                                'description': f"Sous-classe invalide pour classe 1: {account}",
                                'affected_entries': [str(entry.get('id', ''))],
                                'remediation_steps': ["Vérifier la sous-classification SYSCOHADA"]
                            })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation SYSCOHADA: {str(e)}"
            })
        
        return violations
    
    def _validate_syscohada_financial_statements(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la présentation des états financiers SYSCOHADA"""
        violations = []
        
        try:
            required_statements = parameters.get('required_statements', [])
            available_statements = data.get('financial_statements', [])
            
            # Vérifier la présence des états obligatoires
            missing_statements = []
            for required in required_statements:
                if required not in available_statements:
                    missing_statements.append(required)
            
            if missing_statements:
                violations.append({
                    'description': f"États financiers SYSCOHADA manquants: {', '.join(missing_statements)}",
                    'expected_value': required_statements,
                    'actual_value': available_statements,
                    'remediation_steps': [
                        "Produire tous les états financiers obligatoires",
                        "Respecter les modèles SYSCOHADA",
                        "Bilan, Compte de résultat, TAFIRE obligatoires"
                    ]
                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation états financiers SYSCOHADA: {str(e)}"
            })
        
        return violations
    
    def _validate_syscohada_depreciation(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide les amortissements selon SYSCOHADA"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            depreciation_accounts = parameters.get('depreciation_accounts', [])
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                # Vérifier les comptes d'amortissement
                if any(account.startswith(dep_acc) for dep_acc in depreciation_accounts):
                    amount = float(entry.get('montant', 0))
                    description = str(entry.get('description', '')).lower()
                    
                    # Les amortissements doivent être positifs (en crédit)
                    if amount <= 0:
                        violations.append({
                            'description': f"Amortissement négatif ou nul: {amount}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Vérifier le calcul de l'amortissement",
                                "Les amortissements doivent être positifs"
                            ]
                        })
                    
                    # Vérifier la documentation
                    if 'amortissement' not in description and 'dotation' not in description:
                        violations.append({
                            'description': f"Amortissement mal documenté: {account}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Préciser la nature de l'amortissement",
                                "Indiquer l'actif concerné"
                            ]
                        })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation amortissements SYSCOHADA: {str(e)}"
            })
        
        return violations
    
    def _validate_french_chart_of_accounts(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la conformité au plan comptable général français"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            pcg_classes = parameters.get('pcg_classes', [])
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                if account:
                    # Vérifier la classe PCG
                    first_digit = account[0]
                    if first_digit not in pcg_classes:
                        violations.append({
                            'description': f"Classe de compte non PCG: {first_digit}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Utiliser les classes PCG (1-7)",
                                "Vérifier le plan comptable général français"
                            ]
                        })
                    
                    # Vérifier la longueur minimale
                    if len(account) < 3:
                        violations.append({
                            'description': f"Compte PCG trop court: {account}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Utiliser au minimum 3 chiffres",
                                "Respecter la codification PCG"
                            ]
                        })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation PCG français: {str(e)}"
            })
        
        return violations
    
    def _validate_french_notes_disclosure(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide les informations en annexe selon la réglementation française"""
        violations = []
        
        try:
            required_notes = parameters.get('required_notes', [])
            available_notes = data.get('notes', [])
            
            # Vérifier la présence des notes obligatoires
            missing_notes = []
            for required in required_notes:
                if required not in available_notes:
                    missing_notes.append(required)
            
            if missing_notes:
                violations.append({
                    'description': f"Informations annexe manquantes: {', '.join(missing_notes)}",
                    'expected_value': required_notes,
                    'actual_value': available_notes,
                    'remediation_steps': [
                        "Compléter l'annexe comptable",
                        "Respecter les obligations du Code de commerce",
                        "Documenter les méthodes comptables"
                    ]
                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation annexe française: {str(e)}"
            })
        
        return violations
    
    def _validate_balance_equation(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide l'équation comptable fondamentale"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            
            total_debit = Decimal('0')
            total_credit = Decimal('0')
            
            for entry in entries:
                debit = Decimal(str(entry.get('debit', 0)))
                credit = Decimal(str(entry.get('credit', 0)))
                
                total_debit += debit
                total_credit += credit
            
            # Vérifier l'équilibre
            difference = abs(total_debit - total_credit)
            tolerance = Decimal('0.01')  # Tolérance de 1 centime
            
            if difference > tolerance:
                violations.append({
                    'description': f"Déséquilibre comptable: Débit {total_debit} ≠ Crédit {total_credit}",
                    'expected_value': float(total_debit),
                    'actual_value': float(total_credit),
                    'remediation_steps': [
                        "Corriger les écritures déséquilibrées",
                        "Vérifier la saisie des montants",
                        "Respecter le principe de la partie double"
                    ]
                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation équilibre: {str(e)}"
            })
        
        return violations
    
    def _validate_account_ranges(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide les plages de comptes autorisées"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            allowed_ranges = parameters.get('allowed_ranges', {})
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                if account:
                    account_class = account[0]
                    
                    if account_class in allowed_ranges:
                        min_val, max_val = allowed_ranges[account_class]
                        account_num = int(account) if account.isdigit() else 0
                        
                        if not (min_val <= account_num <= max_val):
                            violations.append({
                                'description': f"Compte {account} hors plage autorisée [{min_val}-{max_val}]",
                                'affected_entries': [str(entry.get('id', ''))],
                                'remediation_steps': [
                                    "Utiliser un compte dans la plage autorisée",
                                    "Vérifier le plan comptable"
                                ]
                            })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation plages comptes: {str(e)}"
            })
        
        return violations
    
    def _validate_mandatory_accounts(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la présence des comptes obligatoires"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            mandatory_accounts = parameters.get('mandatory_accounts', [])
            
            # Extraire les comptes utilisés
            accounts_used = set(str(entry.get('account', '')) for entry in entries)
            
            # Vérifier les comptes manquants
            missing_accounts = set(mandatory_accounts) - accounts_used
            
            if missing_accounts:
                violations.append({
                    'description': f"Comptes obligatoires manquants: {', '.join(missing_accounts)}",
                    'expected_value': mandatory_accounts,
                    'actual_value': list(accounts_used),
                    'remediation_steps': [
                        "Ajouter les comptes obligatoires",
                        "Vérifier la complétude du plan comptable"
                    ]
                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation comptes obligatoires: {str(e)}"
            })
        
        return violations
    
    def _validate_depreciation_consistency(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la cohérence des amortissements"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            
            # Grouper par actif
            assets = defaultdict(list)
            
            for entry in entries:
                account = str(entry.get('account', ''))
                description = str(entry.get('description', '')).lower()
                
                # Identifier les écritures d'amortissement
                if 'amortissement' in description or 'dotation' in description:
                    # Extraire l'identifiant de l'actif (simplifié)
                    asset_id = account[:3]  # Utiliser les 3 premiers chiffres
                    assets[asset_id].append(entry)
            
            # Vérifier la cohérence pour chaque actif
            for asset_id, asset_entries in assets.items():
                if len(asset_entries) > 1:
                    # Vérifier la régularité des amortissements
                    amounts = [float(entry.get('montant', 0)) for entry in asset_entries]
                    
                    # Détecter les variations importantes
                    if len(amounts) > 2:
                        avg_amount = sum(amounts) / len(amounts)
                        for i, amount in enumerate(amounts):
                            if abs(amount - avg_amount) > avg_amount * 0.5:  # Variation > 50%
                                violations.append({
                                    'description': f"Amortissement irrégulier pour actif {asset_id}: {amount}",
                                    'affected_entries': [str(asset_entries[i].get('id', ''))],
                                    'remediation_steps': [
                                        "Vérifier le calcul de l'amortissement",
                                        "Justifier les variations importantes"
                                    ]
                                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation cohérence amortissements: {str(e)}"
            })
        
        return violations
    
    def _validate_revenue_cut_off(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide la séparation des exercices pour les revenus"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            cutoff_date = parameters.get('cutoff_date', datetime.now().replace(month=12, day=31))
            
            if isinstance(cutoff_date, str):
                cutoff_date = datetime.strptime(cutoff_date, '%Y-%m-%d')
            
            for entry in entries:
                account = str(entry.get('account', ''))
                entry_date = entry.get('date')
                
                if entry_date:
                    if isinstance(entry_date, str):
                        entry_date = datetime.strptime(entry_date, '%Y-%m-%d')
                    
                    # Vérifier les revenus près de la clôture
                    if account.startswith('7'):  # Comptes de produits
                        days_from_cutoff = abs((entry_date - cutoff_date).days)
                        
                        if days_from_cutoff <= 5:  # Dans les 5 jours de la clôture
                            description = str(entry.get('description', '')).lower()
                            
                            if 'facture' not in description and 'livraison' not in description:
                                violations.append({
                                    'description': f"Revenu proche clôture sans justification: {account}",
                                    'affected_entries': [str(entry.get('id', ''))],
                                    'remediation_steps': [
                                        "Documenter la date de livraison/prestation",
                                        "Vérifier la séparation des exercices",
                                        "Justifier la reconnaissance du revenu"
                                    ]
                                })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation séparation exercices: {str(e)}"
            })
        
        return violations
    
    def _validate_inventory_valuation(self, data: Dict, parameters: Dict, config: Dict) -> List[Dict]:
        """Valide l'évaluation des stocks"""
        violations = []
        
        try:
            entries = data.get('entries', [])
            inventory_accounts = parameters.get('inventory_accounts', ['31', '32', '33', '34', '35', '37'])
            
            for entry in entries:
                account = str(entry.get('account', ''))
                
                # Vérifier les comptes de stocks
                if any(account.startswith(inv_acc) for inv_acc in inventory_accounts):
                    amount = float(entry.get('montant', 0))
                    description = str(entry.get('description', '')).lower()
                    
                    # Les stocks ne peuvent pas être négatifs
                    if amount < 0:
                        violations.append({
                            'description': f"Stock négatif détecté: {account} = {amount}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Vérifier l'inventaire physique",
                                "Corriger les mouvements de stock",
                                "Les stocks ne peuvent être négatifs"
                            ]
                        })
                    
                    # Vérifier la méthode d'évaluation
                    if 'fifo' not in description and 'lifo' not in description and 'cump' not in description:
                        violations.append({
                            'description': f"Méthode d'évaluation stock non précisée: {account}",
                            'affected_entries': [str(entry.get('id', ''))],
                            'remediation_steps': [
                                "Préciser la méthode d'évaluation (FIFO, LIFO, CUMP)",
                                "Documenter la politique de valorisation des stocks"
                            ]
                        })
        
        except Exception as e:
            violations.append({
                'description': f"Erreur validation évaluation stocks: {str(e)}"
            })
        
        return violations
    
    def _is_valid_ifrs_account(self, account: str) -> bool:
        """Vérifie si un compte respecte la structure IFRS"""
        if not account or len(account) < 2:
            return False
        
        # Structure IFRS simplifiée
        first_digit = account[0]
        return first_digit in ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    def _violation_to_dict(self, violation: ComplianceViolation) -> Dict:
        """Convertit une violation en dictionnaire"""
        return {
            'rule_id': violation.rule_id,
            'violation_id': violation.violation_id,
            'severity': violation.severity.value,
            'title': violation.title,
            'description': violation.description,
            'affected_entries': violation.affected_entries,
            'expected_value': violation.expected_value,
            'actual_value': violation.actual_value,
            'remediation_steps': violation.remediation_steps or [],
            'references': violation.references or [],
            'detected_at': violation.detected_at.isoformat() if violation.detected_at else None
        }
    
    def _generate_compliance_recommendations(self, violations: List[ComplianceViolation], 
                                           standard: ComplianceStandard) -> List[str]:
        """Génère des recommandations basées sur les violations"""
        recommendations = []
        
        if not violations:
            recommendations.append(f"Conformité {standard.value.upper()} satisfaisante")
            return recommendations
        
        # Compter les violations par sévérité
        severity_counts = defaultdict(int)
        for violation in violations:
            severity_counts[violation.severity.value] += 1
        
        # Recommandations par sévérité
        if severity_counts['critical'] > 0:
            recommendations.append(f"URGENT: Corriger {severity_counts['critical']} violation(s) critique(s)")
        
        if severity_counts['error'] > 0:
            recommendations.append(f"Corriger {severity_counts['error']} erreur(s) de conformité")
        
        if severity_counts['warning'] > 0:
            recommendations.append(f"Examiner {severity_counts['warning']} avertissement(s)")
        
        # Recommandations spécifiques par norme
        if standard == ComplianceStandard.IFRS:
            recommendations.extend([
                "Vérifier la conformité aux normes IFRS en vigueur",
                "Documenter les méthodes comptables appliquées",
                "Assurer la cohérence avec les principes IFRS"
            ])
        elif standard == ComplianceStandard.SYSCOHADA:
            recommendations.extend([
                "Respecter le plan comptable SYSCOHADA révisé",
                "Produire tous les états financiers obligatoires",
                "Appliquer les règles d'évaluation OHADA"
            ])
        elif standard == ComplianceStandard.FRENCH_GAAP:
            recommendations.extend([
                "Respecter le Plan Comptable Général français",
                "Compléter l'annexe comptable obligatoire",
                "Appliquer les règles du Code de commerce"
            ])
        
        return recommendations
    
    def _generate_entry_suggestions(self, entry_data: Dict, standard: ComplianceStandard) -> List[str]:
        """Génère des suggestions pour une écriture"""
        suggestions = []
        
        account = str(entry_data.get('account', ''))
        description = str(entry_data.get('description', ''))
        amount = entry_data.get('montant', 0)
        
        # Suggestions générales
        if not account:
            suggestions.append("Spécifier un numéro de compte")
        
        if not description or len(description) < 10:
            suggestions.append("Améliorer la description de l'écriture")
        
        if amount == 0:
            suggestions.append("Vérifier le montant de l'écriture")
        
        # Suggestions spécifiques par norme
        if standard == ComplianceStandard.SYSCOHADA:
            if account and len(account) < 2:
                suggestions.append("Utiliser au minimum 2 chiffres pour le compte SYSCOHADA")
        
        elif standard == ComplianceStandard.FRENCH_GAAP:
            if account and len(account) < 3:
                suggestions.append("Utiliser au minimum 3 chiffres pour le compte PCG")
        
        return suggestions
    
    def add_custom_rule(self, rule: ComplianceRule) -> bool:
        """Ajoute une règle personnalisée"""
        try:
            if rule.standard not in self.rules:
                self.rules[rule.standard] = {}
            
            self.rules[rule.standard][rule.rule_id] = rule
            return True
        except Exception:
            return False
    
    def get_supported_standards(self) -> List[str]:
        """Retourne la liste des normes supportées"""
        return [standard.value for standard in ComplianceStandard]
    
    def get_rules_for_standard(self, standard: ComplianceStandard) -> Dict:
        """Retourne les règles pour une norme donnée"""
        if standard not in self.rules:
            return {}
        
        return {
            rule_id: {
                'title': rule.title,
                'description': rule.description,
                'category': rule.category.value,
                'severity': rule.severity.value,
                'references': rule.references
            }
            for rule_id, rule in self.rules[standard].items()
        }

