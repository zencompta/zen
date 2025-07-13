"""
Service de validation croisée entre différents documents comptables
Vérifie la cohérence et la concordance entre les documents
"""

import os
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import re
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Niveaux de validation"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Résultat d'une validation"""
    level: ValidationLevel
    message: str
    field: str
    expected_value: Any = None
    actual_value: Any = None
    documents: List[str] = None
    confidence: float = 1.0


class CrossValidationService:
    """Service de validation croisée entre documents comptables"""
    
    def __init__(self):
        self.tolerance_amount = Decimal('0.01')  # Tolérance pour les montants (1 centime)
        self.tolerance_date = timedelta(days=1)  # Tolérance pour les dates (1 jour)
        
        self.validation_rules = {
            'FACTURE_PAIEMENT': {
                'description': 'Validation entre facture et paiement',
                'required_fields': ['montant', 'date', 'reference'],
                'tolerance_days': 30
            },
            'BALANCE_GRAND_LIVRE': {
                'description': 'Validation entre balance et grand livre',
                'required_fields': ['compte', 'solde'],
                'tolerance_amount': 0.01
            },
            'JOURNAL_BALANCE': {
                'description': 'Validation entre journal et balance',
                'required_fields': ['compte', 'debit', 'credit'],
                'tolerance_amount': 0.01
            },
            'FEC_BALANCE': {
                'description': 'Validation entre FEC et balance',
                'required_fields': ['CompteNum', 'Debit', 'Credit'],
                'tolerance_amount': 0.01
            }
        }
    
    def validate_documents(self, documents: List[Dict]) -> Dict:
        """
        Valide la cohérence entre plusieurs documents
        
        Args:
            documents: Liste de documents avec leurs données
            
        Returns:
            Dict contenant les résultats de validation
        """
        result = {
            'success': True,
            'validation_summary': {
                'total_checks': 0,
                'passed': 0,
                'warnings': 0,
                'errors': 0,
                'critical': 0
            },
            'validations': [],
            'recommendations': [],
            'processing_time': 0.0
        }
        
        try:
            start_time = datetime.now()
            
            # Identifier les types de documents
            doc_types = [doc.get('type', 'UNKNOWN') for doc in documents]
            
            # Effectuer les validations selon les combinaisons disponibles
            if 'FACTURE' in doc_types and 'PAIEMENT' in doc_types:
                validations = self._validate_facture_paiement(documents)
                result['validations'].extend(validations)
            
            if 'BALANCE' in doc_types and 'GRAND_LIVRE' in doc_types:
                validations = self._validate_balance_grand_livre(documents)
                result['validations'].extend(validations)
            
            if 'JOURNAL' in doc_types and 'BALANCE' in doc_types:
                validations = self._validate_journal_balance(documents)
                result['validations'].extend(validations)
            
            if 'FEC' in doc_types and 'BALANCE' in doc_types:
                validations = self._validate_fec_balance(documents)
                result['validations'].extend(validations)
            
            # Validations génériques
            generic_validations = self._perform_generic_validations(documents)
            result['validations'].extend(generic_validations)
            
            # Calculer le résumé
            result['validation_summary'] = self._calculate_summary(result['validations'])
            
            # Générer des recommandations
            result['recommendations'] = self._generate_recommendations(result['validations'])
            
            # Déterminer le succès global
            result['success'] = result['validation_summary']['critical'] == 0
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur validation croisée: {str(e)}"
        
        return result
    
    def _validate_facture_paiement(self, documents: List[Dict]) -> List[ValidationResult]:
        """Valide la cohérence entre factures et paiements"""
        validations = []
        
        factures = [doc for doc in documents if doc.get('type') == 'FACTURE']
        paiements = [doc for doc in documents if doc.get('type') == 'PAIEMENT']
        
        for facture in factures:
            facture_data = facture.get('data', {})
            numero_facture = facture_data.get('numero_facture')
            montant_facture = self._parse_amount(facture_data.get('montant_ttc', '0'))
            date_facture = self._parse_date(facture_data.get('date'))
            
            if not numero_facture:
                validations.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="Numéro de facture manquant",
                    field="numero_facture",
                    documents=[facture.get('file_name', 'facture')]
                ))
                continue
            
            # Chercher les paiements correspondants
            matching_payments = []
            for paiement in paiements:
                paiement_data = paiement.get('data', {})
                ref_paiement = paiement_data.get('reference', '')
                
                if numero_facture in ref_paiement or ref_paiement in numero_facture:
                    matching_payments.append(paiement)
            
            if not matching_payments:
                validations.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Aucun paiement trouvé pour la facture {numero_facture}",
                    field="paiement_correspondant",
                    expected_value=numero_facture,
                    documents=[facture.get('file_name', 'facture')]
                ))
            else:
                # Vérifier la concordance des montants
                total_paiements = sum(
                    self._parse_amount(p.get('data', {}).get('montant', '0'))
                    for p in matching_payments
                )
                
                if abs(montant_facture - total_paiements) > self.tolerance_amount:
                    validations.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"Montant facture ({montant_facture}) != montant paiements ({total_paiements})",
                        field="montant",
                        expected_value=float(montant_facture),
                        actual_value=float(total_paiements),
                        documents=[facture.get('file_name', 'facture')] + 
                                 [p.get('file_name', 'paiement') for p in matching_payments]
                    ))
                else:
                    validations.append(ValidationResult(
                        level=ValidationLevel.INFO,
                        message=f"Montants concordants pour facture {numero_facture}",
                        field="montant",
                        expected_value=float(montant_facture),
                        actual_value=float(total_paiements),
                        documents=[facture.get('file_name', 'facture')] + 
                                 [p.get('file_name', 'paiement') for p in matching_payments]
                    ))
        
        return validations
    
    def _validate_balance_grand_livre(self, documents: List[Dict]) -> List[ValidationResult]:
        """Valide la cohérence entre balance et grand livre"""
        validations = []
        
        balances = [doc for doc in documents if doc.get('type') == 'BALANCE']
        grands_livres = [doc for doc in documents if doc.get('type') == 'GRAND_LIVRE']
        
        for balance in balances:
            balance_data = balance.get('data', {})
            if not isinstance(balance_data, list):
                continue
            
            for grand_livre in grands_livres:
                gl_data = grand_livre.get('data', {})
                if not isinstance(gl_data, list):
                    continue
                
                # Comparer les soldes par compte
                for balance_line in balance_data:
                    compte = balance_line.get('compte')
                    solde_balance = self._parse_amount(balance_line.get('solde', '0'))
                    
                    # Calculer le solde depuis le grand livre
                    solde_gl = self._calculate_account_balance(gl_data, compte)
                    
                    if abs(solde_balance - solde_gl) > self.tolerance_amount:
                        validations.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"Solde compte {compte}: Balance ({solde_balance}) != Grand Livre ({solde_gl})",
                            field="solde",
                            expected_value=float(solde_balance),
                            actual_value=float(solde_gl),
                            documents=[balance.get('file_name', 'balance'), 
                                     grand_livre.get('file_name', 'grand_livre')]
                        ))
                    else:
                        validations.append(ValidationResult(
                            level=ValidationLevel.INFO,
                            message=f"Solde concordant pour compte {compte}",
                            field="solde",
                            expected_value=float(solde_balance),
                            actual_value=float(solde_gl),
                            documents=[balance.get('file_name', 'balance'), 
                                     grand_livre.get('file_name', 'grand_livre')]
                        ))
        
        return validations
    
    def _validate_journal_balance(self, documents: List[Dict]) -> List[ValidationResult]:
        """Valide la cohérence entre journaux et balance"""
        validations = []
        
        journaux = [doc for doc in documents if doc.get('type') == 'JOURNAL']
        balances = [doc for doc in documents if doc.get('type') == 'BALANCE']
        
        for balance in balances:
            balance_data = balance.get('data', {})
            if not isinstance(balance_data, list):
                continue
            
            # Calculer les totaux depuis les journaux
            total_debit_journaux = Decimal('0')
            total_credit_journaux = Decimal('0')
            
            for journal in journaux:
                journal_data = journal.get('data', {})
                if isinstance(journal_data, list):
                    for line in journal_data:
                        total_debit_journaux += self._parse_amount(line.get('debit', '0'))
                        total_credit_journaux += self._parse_amount(line.get('credit', '0'))
            
            # Calculer les totaux depuis la balance
            total_debit_balance = Decimal('0')
            total_credit_balance = Decimal('0')
            
            for line in balance_data:
                debit = self._parse_amount(line.get('debit', '0'))
                credit = self._parse_amount(line.get('credit', '0'))
                total_debit_balance += debit
                total_credit_balance += credit
            
            # Vérifier l'équilibre débit/crédit
            if abs(total_debit_journaux - total_credit_journaux) > self.tolerance_amount:
                validations.append(ValidationResult(
                    level=ValidationLevel.CRITICAL,
                    message=f"Déséquilibre dans les journaux: Débit ({total_debit_journaux}) != Crédit ({total_credit_journaux})",
                    field="equilibre_journaux",
                    expected_value=float(total_debit_journaux),
                    actual_value=float(total_credit_journaux),
                    documents=[j.get('file_name', 'journal') for j in journaux]
                ))
            
            # Vérifier la concordance avec la balance
            if abs(total_debit_journaux - total_debit_balance) > self.tolerance_amount:
                validations.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Total débit: Journaux ({total_debit_journaux}) != Balance ({total_debit_balance})",
                    field="total_debit",
                    expected_value=float(total_debit_journaux),
                    actual_value=float(total_debit_balance),
                    documents=[j.get('file_name', 'journal') for j in journaux] + 
                             [b.get('file_name', 'balance') for b in balances]
                ))
        
        return validations
    
    def _validate_fec_balance(self, documents: List[Dict]) -> List[ValidationResult]:
        """Valide la cohérence entre FEC et balance"""
        validations = []
        
        fecs = [doc for doc in documents if doc.get('type') == 'FEC']
        balances = [doc for doc in documents if doc.get('type') == 'BALANCE']
        
        for fec in fecs:
            fec_data = fec.get('data', {})
            if not isinstance(fec_data, list):
                continue
            
            for balance in balances:
                balance_data = balance.get('data', {})
                if not isinstance(balance_data, list):
                    continue
                
                # Calculer les soldes par compte depuis le FEC
                fec_balances = self._calculate_fec_balances(fec_data)
                
                # Comparer avec la balance
                for balance_line in balance_data:
                    compte = balance_line.get('compte')
                    solde_balance = self._parse_amount(balance_line.get('solde', '0'))
                    solde_fec = fec_balances.get(compte, Decimal('0'))
                    
                    if abs(solde_balance - solde_fec) > self.tolerance_amount:
                        validations.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"Solde compte {compte}: Balance ({solde_balance}) != FEC ({solde_fec})",
                            field="solde_fec",
                            expected_value=float(solde_balance),
                            actual_value=float(solde_fec),
                            documents=[balance.get('file_name', 'balance'), 
                                     fec.get('file_name', 'fec')]
                        ))
        
        return validations
    
    def _perform_generic_validations(self, documents: List[Dict]) -> List[ValidationResult]:
        """Effectue des validations génériques sur tous les documents"""
        validations = []
        
        # Vérifier la cohérence des dates
        dates = []
        for doc in documents:
            doc_data = doc.get('data', {})
            if isinstance(doc_data, dict):
                date_fields = ['date', 'date_facture', 'date_paiement', 'EcritureDate']
                for field in date_fields:
                    if field in doc_data:
                        date_val = self._parse_date(doc_data[field])
                        if date_val:
                            dates.append((date_val, doc.get('file_name', 'document'), field))
        
        # Vérifier les écarts de dates
        if len(dates) > 1:
            dates.sort(key=lambda x: x[0])
            min_date, max_date = dates[0][0], dates[-1][0]
            
            if (max_date - min_date).days > 365:  # Plus d'un an d'écart
                validations.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Écart important entre les dates: {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}",
                    field="coherence_dates",
                    expected_value=min_date.strftime('%d/%m/%Y'),
                    actual_value=max_date.strftime('%d/%m/%Y'),
                    documents=[d[1] for d in dates]
                ))
        
        # Vérifier la cohérence des montants
        montants = []
        for doc in documents:
            doc_data = doc.get('data', {})
            if isinstance(doc_data, dict):
                amount_fields = ['montant', 'montant_ttc', 'total', 'solde']
                for field in amount_fields:
                    if field in doc_data:
                        amount = self._parse_amount(doc_data[field])
                        if amount > 0:
                            montants.append((amount, doc.get('file_name', 'document'), field))
        
        # Détecter les montants aberrants
        if len(montants) > 2:
            amounts = [m[0] for m in montants]
            avg_amount = sum(amounts) / len(amounts)
            
            for amount, doc_name, field in montants:
                if amount > avg_amount * 10:  # 10 fois la moyenne
                    validations.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        message=f"Montant potentiellement aberrant: {amount} dans {doc_name}",
                        field=field,
                        actual_value=float(amount),
                        documents=[doc_name]
                    ))
        
        return validations
    
    def _calculate_account_balance(self, grand_livre_data: List[Dict], compte: str) -> Decimal:
        """Calcule le solde d'un compte depuis le grand livre"""
        solde = Decimal('0')
        
        for line in grand_livre_data:
            if line.get('compte') == compte:
                debit = self._parse_amount(line.get('debit', '0'))
                credit = self._parse_amount(line.get('credit', '0'))
                solde += debit - credit
        
        return solde
    
    def _calculate_fec_balances(self, fec_data: List[Dict]) -> Dict[str, Decimal]:
        """Calcule les soldes par compte depuis le FEC"""
        balances = {}
        
        for line in fec_data:
            compte = line.get('CompteNum')
            if compte:
                if compte not in balances:
                    balances[compte] = Decimal('0')
                
                debit = self._parse_amount(line.get('Debit', '0'))
                credit = self._parse_amount(line.get('Credit', '0'))
                balances[compte] += debit - credit
        
        return balances
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse un montant en Decimal"""
        if not amount_str:
            return Decimal('0')
        
        # Nettoyer la chaîne
        amount_str = str(amount_str).strip()
        amount_str = re.sub(r'[^\d,\.\-]', '', amount_str)
        amount_str = amount_str.replace(',', '.')
        
        try:
            return Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except:
            return Decimal('0')
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date"""
        if not date_str:
            return None
        
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%d/%m/%y', '%d-%m-%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except:
                continue
        
        return None
    
    def _calculate_summary(self, validations: List[ValidationResult]) -> Dict:
        """Calcule le résumé des validations"""
        summary = {
            'total_checks': len(validations),
            'passed': 0,
            'warnings': 0,
            'errors': 0,
            'critical': 0
        }
        
        for validation in validations:
            if validation.level == ValidationLevel.INFO:
                summary['passed'] += 1
            elif validation.level == ValidationLevel.WARNING:
                summary['warnings'] += 1
            elif validation.level == ValidationLevel.ERROR:
                summary['errors'] += 1
            elif validation.level == ValidationLevel.CRITICAL:
                summary['critical'] += 1
        
        return summary
    
    def _generate_recommendations(self, validations: List[ValidationResult]) -> List[str]:
        """Génère des recommandations basées sur les validations"""
        recommendations = []
        
        # Compter les types d'erreurs
        error_types = {}
        for validation in validations:
            if validation.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
                field = validation.field
                if field not in error_types:
                    error_types[field] = 0
                error_types[field] += 1
        
        # Générer des recommandations
        if 'montant' in error_types:
            recommendations.append(
                "Vérifier la saisie des montants et s'assurer de l'utilisation du même format décimal"
            )
        
        if 'solde' in error_types:
            recommendations.append(
                "Contrôler les calculs de soldes et vérifier la cohérence entre les documents"
            )
        
        if 'equilibre_journaux' in error_types:
            recommendations.append(
                "Corriger le déséquilibre débit/crédit dans les journaux comptables"
            )
        
        if 'coherence_dates' in error_types:
            recommendations.append(
                "Vérifier la cohérence des dates entre les documents"
            )
        
        if not recommendations:
            recommendations.append("Aucune recommandation spécifique - validation globalement satisfaisante")
        
        return recommendations
    
    def validate_document_pair(self, doc1: Dict, doc2: Dict, validation_type: str) -> Dict:
        """
        Valide une paire de documents selon un type de validation spécifique
        
        Args:
            doc1: Premier document
            doc2: Deuxième document
            validation_type: Type de validation à effectuer
            
        Returns:
            Dict contenant les résultats de validation
        """
        if validation_type not in self.validation_rules:
            return {
                'success': False,
                'error': f"Type de validation non supporté: {validation_type}"
            }
        
        return self.validate_documents([doc1, doc2])
    
    def get_validation_rules(self) -> Dict:
        """Retourne les règles de validation disponibles"""
        return self.validation_rules

