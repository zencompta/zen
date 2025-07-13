import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from decimal import Decimal
import json
from collections import defaultdict
import re

class AuditAnalyzer:
    """Service d'analyse comptable intelligent pour détecter les anomalies et générer des insights"""
    
    def __init__(self, accounting_standard: str = 'IFRS'):
        self.accounting_standard = accounting_standard
        self.analysis_results = []
        
        # Configuration des seuils par norme comptable
        self.thresholds = {
            'IFRS': {
                'materiality_percentage': 0.05,  # 5% du résultat net
                'significant_variance': 0.10,    # 10% de variance significative
                'high_risk_amount': 100000       # Montant considéré comme risqué
            },
            'SYSCOHADA': {
                'materiality_percentage': 0.05,
                'significant_variance': 0.15,
                'high_risk_amount': 50000
            },
            'US_GAAP': {
                'materiality_percentage': 0.05,
                'significant_variance': 0.10,
                'high_risk_amount': 100000
            },
            'PCG': {
                'materiality_percentage': 0.05,
                'significant_variance': 0.12,
                'high_risk_amount': 75000
            }
        }
    
    def analyze_balance_sheet(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyse la balance générale et détecte les anomalies"""
        df = pd.DataFrame(entries)
        
        if df.empty:
            return {'error': 'Aucune donnée à analyser'}
        
        results = {
            'analysis_type': 'balance_analysis',
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'anomalies': [],
            'recommendations': [],
            'risk_level': 'low'
        }
        
        # 1. Vérification de l'équilibre comptable
        balance_check = self._check_accounting_balance(df)
        results['summary']['balance_check'] = balance_check
        
        # 2. Analyse des comptes
        account_analysis = self._analyze_accounts(df)
        results['summary']['account_analysis'] = account_analysis
        
        # 3. Détection d'anomalies
        anomalies = self._detect_balance_anomalies(df)
        results['anomalies'] = anomalies
        
        # 4. Calcul du niveau de risque global
        results['risk_level'] = self._calculate_risk_level(anomalies)
        
        # 5. Génération de recommandations
        results['recommendations'] = self._generate_balance_recommendations(balance_check, anomalies)
        
        return results
    
    def analyze_journal_entries(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyse les écritures de journal pour détecter les anomalies"""
        df = pd.DataFrame(entries)
        
        if df.empty:
            return {'error': 'Aucune donnée à analyser'}
        
        results = {
            'analysis_type': 'journal_analysis',
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'anomalies': [],
            'recommendations': [],
            'risk_level': 'low'
        }
        
        # 1. Analyse des écritures déséquilibrées
        unbalanced_entries = self._find_unbalanced_entries(df)
        results['summary']['unbalanced_entries'] = len(unbalanced_entries)
        
        # 2. Détection des écritures suspectes
        suspicious_entries = self._detect_suspicious_entries(df)
        results['anomalies'].extend(suspicious_entries)
        
        # 3. Analyse des montants inhabituels
        unusual_amounts = self._detect_unusual_amounts(df)
        results['anomalies'].extend(unusual_amounts)
        
        # 4. Vérification des dates
        date_anomalies = self._check_date_consistency(df)
        results['anomalies'].extend(date_anomalies)
        
        # 5. Calcul du niveau de risque
        results['risk_level'] = self._calculate_risk_level(results['anomalies'])
        
        # 6. Recommandations
        results['recommendations'] = self._generate_journal_recommendations(results['anomalies'])
        
        return results
    
    def perform_ratio_analysis(self, entries: List[Dict]) -> Dict[str, Any]:
        """Effectue une analyse par ratios financiers"""
        df = pd.DataFrame(entries)
        
        if df.empty:
            return {'error': 'Aucune donnée à analyser'}
        
        # Calculer les soldes par classe de comptes
        account_balances = self._calculate_account_balances(df)
        
        results = {
            'analysis_type': 'ratio_analysis',
            'timestamp': datetime.now().isoformat(),
            'ratios': {},
            'interpretations': [],
            'risk_level': 'low'
        }
        
        # Ratios de liquidité
        liquidity_ratios = self._calculate_liquidity_ratios(account_balances)
        results['ratios']['liquidity'] = liquidity_ratios
        
        # Ratios de solvabilité
        solvency_ratios = self._calculate_solvency_ratios(account_balances)
        results['ratios']['solvency'] = solvency_ratios
        
        # Ratios d'activité
        activity_ratios = self._calculate_activity_ratios(account_balances)
        results['ratios']['activity'] = activity_ratios
        
        # Interprétations
        results['interpretations'] = self._interpret_ratios(results['ratios'])
        
        # Niveau de risque basé sur les ratios
        results['risk_level'] = self._assess_ratio_risk(results['ratios'])
        
        return results
    
    def detect_fraud_indicators(self, entries: List[Dict]) -> Dict[str, Any]:
        """Détecte les indicateurs potentiels de fraude"""
        df = pd.DataFrame(entries)
        
        if df.empty:
            return {'error': 'Aucune donnée à analyser'}
        
        results = {
            'analysis_type': 'fraud_detection',
            'timestamp': datetime.now().isoformat(),
            'indicators': [],
            'risk_level': 'low',
            'recommendations': []
        }
        
        # 1. Loi de Benford (distribution des premiers chiffres)
        benford_analysis = self._benford_law_analysis(df)
        if benford_analysis['suspicious']:
            results['indicators'].append(benford_analysis)
        
        # 2. Écritures en fin de période
        period_end_entries = self._detect_period_end_manipulation(df)
        results['indicators'].extend(period_end_entries)
        
        # 3. Écritures rondes suspectes
        round_amounts = self._detect_suspicious_round_amounts(df)
        results['indicators'].extend(round_amounts)
        
        # 4. Écritures hors heures ouvrables
        after_hours = self._detect_after_hours_entries(df)
        results['indicators'].extend(after_hours)
        
        # 5. Comptes inhabituels
        unusual_accounts = self._detect_unusual_account_usage(df)
        results['indicators'].extend(unusual_accounts)
        
        # Calcul du risque de fraude
        results['risk_level'] = self._calculate_fraud_risk(results['indicators'])
        
        # Recommandations spécifiques à la fraude
        results['recommendations'] = self._generate_fraud_recommendations(results['indicators'])
        
        return results
    
    def _check_accounting_balance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Vérifie l'équilibre comptable global"""
        total_debit = df['debit_amount'].sum()
        total_credit = df['credit_amount'].sum()
        difference = abs(total_debit - total_credit)
        
        threshold = self.thresholds[self.accounting_standard]['high_risk_amount'] * 0.01
        
        return {
            'total_debit': float(total_debit),
            'total_credit': float(total_credit),
            'difference': float(difference),
            'is_balanced': difference < threshold,
            'balance_percentage': float((difference / max(total_debit, total_credit)) * 100) if max(total_debit, total_credit) > 0 else 0
        }
    
    def _analyze_accounts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse la répartition et les caractéristiques des comptes"""
        account_summary = df.groupby('account_number').agg({
            'debit_amount': 'sum',
            'credit_amount': 'sum',
            'account_name': 'first'
        }).reset_index()
        
        account_summary['net_balance'] = account_summary['debit_amount'] - account_summary['credit_amount']
        account_summary['total_movement'] = account_summary['debit_amount'] + account_summary['credit_amount']
        
        return {
            'total_accounts': len(account_summary),
            'accounts_with_movement': len(account_summary[account_summary['total_movement'] > 0]),
            'largest_movements': account_summary.nlargest(5, 'total_movement')[['account_number', 'account_name', 'total_movement']].to_dict('records'),
            'accounts_summary': account_summary.to_dict('records')
        }
    
    def _detect_balance_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les anomalies dans la balance"""
        anomalies = []
        
        # Comptes avec des soldes inhabituels selon leur nature
        account_nature_rules = {
            '1': 'debit',    # Actif
            '2': 'credit',   # Passif
            '3': 'credit',   # Capitaux propres
            '4': 'credit',   # Fournisseurs
            '5': 'debit',    # Financier
            '6': 'debit',    # Charges
            '7': 'credit'    # Produits
        }
        
        account_balances = df.groupby('account_number').agg({
            'debit_amount': 'sum',
            'credit_amount': 'sum',
            'account_name': 'first'
        }).reset_index()
        
        account_balances['net_balance'] = account_balances['debit_amount'] - account_balances['credit_amount']
        
        for _, account in account_balances.iterrows():
            account_class = str(account['account_number'])[0]
            expected_nature = account_nature_rules.get(account_class)
            
            if expected_nature == 'debit' and account['net_balance'] < 0:
                anomalies.append({
                    'type': 'unusual_account_balance',
                    'severity': 'warning',
                    'account_number': account['account_number'],
                    'account_name': account['account_name'],
                    'description': f"Compte d'actif avec solde créditeur: {account['net_balance']:.2f}",
                    'amount': float(account['net_balance'])
                })
            elif expected_nature == 'credit' and account['net_balance'] > 0:
                anomalies.append({
                    'type': 'unusual_account_balance',
                    'severity': 'warning',
                    'account_number': account['account_number'],
                    'account_name': account['account_name'],
                    'description': f"Compte de passif avec solde débiteur: {account['net_balance']:.2f}",
                    'amount': float(account['net_balance'])
                })
        
        return anomalies
    
    def _find_unbalanced_entries(self, df: pd.DataFrame) -> List[Dict]:
        """Trouve les écritures déséquilibrées"""
        if 'piece_number' not in df.columns:
            return []
        
        piece_balances = df.groupby('piece_number').agg({
            'debit_amount': 'sum',
            'credit_amount': 'sum'
        }).reset_index()
        
        piece_balances['difference'] = abs(piece_balances['debit_amount'] - piece_balances['credit_amount'])
        
        # Seuil de tolérance pour les erreurs d'arrondi
        tolerance = 0.01
        unbalanced = piece_balances[piece_balances['difference'] > tolerance]
        
        return unbalanced.to_dict('records')
    
    def _detect_suspicious_entries(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les écritures suspectes"""
        anomalies = []
        
        # Écritures avec des montants très élevés
        high_amount_threshold = self.thresholds[self.accounting_standard]['high_risk_amount']
        
        high_amount_entries = df[
            (df['debit_amount'] > high_amount_threshold) | 
            (df['credit_amount'] > high_amount_threshold)
        ]
        
        for _, entry in high_amount_entries.iterrows():
            amount = max(entry['debit_amount'], entry['credit_amount'])
            anomalies.append({
                'type': 'high_amount_entry',
                'severity': 'medium',
                'description': f"Écriture avec montant élevé: {amount:.2f}",
                'amount': float(amount),
                'account_number': entry['account_number'],
                'entry_date': entry.get('entry_date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('entry_date')) else ''
            })
        
        return anomalies
    
    def _detect_unusual_amounts(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les montants inhabituels statistiquement"""
        anomalies = []
        
        # Analyse des montants pour détecter les outliers
        amounts = pd.concat([df['debit_amount'], df['credit_amount']]).dropna()
        amounts = amounts[amounts > 0]  # Exclure les zéros
        
        if len(amounts) > 10:  # Besoin d'un échantillon suffisant
            Q1 = amounts.quantile(0.25)
            Q3 = amounts.quantile(0.75)
            IQR = Q3 - Q1
            
            # Outliers selon la règle IQR
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_entries = df[
                ((df['debit_amount'] > upper_bound) | (df['debit_amount'] < lower_bound) & (df['debit_amount'] > 0)) |
                ((df['credit_amount'] > upper_bound) | (df['credit_amount'] < lower_bound) & (df['credit_amount'] > 0))
            ]
            
            for _, entry in outlier_entries.iterrows():
                amount = max(entry['debit_amount'], entry['credit_amount'])
                anomalies.append({
                    'type': 'statistical_outlier',
                    'severity': 'low',
                    'description': f"Montant statistiquement inhabituel: {amount:.2f}",
                    'amount': float(amount),
                    'account_number': entry['account_number']
                })
        
        return anomalies
    
    def _check_date_consistency(self, df: pd.DataFrame) -> List[Dict]:
        """Vérifie la cohérence des dates"""
        anomalies = []
        
        if 'entry_date' not in df.columns:
            return anomalies
        
        # Convertir les dates
        df['entry_date'] = pd.to_datetime(df['entry_date'], errors='coerce')
        
        # Écritures avec des dates futures
        future_dates = df[df['entry_date'] > datetime.now()]
        for _, entry in future_dates.iterrows():
            anomalies.append({
                'type': 'future_date',
                'severity': 'medium',
                'description': f"Écriture avec date future: {entry['entry_date'].strftime('%Y-%m-%d')}",
                'account_number': entry['account_number'],
                'entry_date': entry['entry_date'].strftime('%Y-%m-%d')
            })
        
        # Écritures avec des dates très anciennes (plus de 2 ans)
        old_threshold = datetime.now() - timedelta(days=730)
        old_dates = df[df['entry_date'] < old_threshold]
        
        if len(old_dates) > 0:
            anomalies.append({
                'type': 'old_entries',
                'severity': 'low',
                'description': f"{len(old_dates)} écritures avec des dates anciennes (> 2 ans)",
                'count': len(old_dates)
            })
        
        return anomalies
    
    def _calculate_risk_level(self, anomalies: List[Dict]) -> str:
        """Calcule le niveau de risque global basé sur les anomalies"""
        if not anomalies:
            return 'low'
        
        severity_scores = {'low': 1, 'medium': 3, 'high': 5, 'critical': 10}
        total_score = sum(severity_scores.get(anomaly.get('severity', 'low'), 1) for anomaly in anomalies)
        
        if total_score >= 20:
            return 'critical'
        elif total_score >= 10:
            return 'high'
        elif total_score >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_balance_recommendations(self, balance_check: Dict, anomalies: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur l'analyse de balance"""
        recommendations = []
        
        if not balance_check['is_balanced']:
            recommendations.append(
                f"Corriger le déséquilibre comptable de {balance_check['difference']:.2f} "
                f"({balance_check['balance_percentage']:.2f}%)"
            )
        
        unusual_balances = [a for a in anomalies if a['type'] == 'unusual_account_balance']
        if unusual_balances:
            recommendations.append(
                f"Vérifier {len(unusual_balances)} comptes avec des soldes inhabituels selon leur nature"
            )
        
        if not recommendations:
            recommendations.append("La balance semble cohérente. Poursuivre avec les analyses détaillées.")
        
        return recommendations
    
    def _generate_journal_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des journaux"""
        recommendations = []
        
        high_amounts = [a for a in anomalies if a['type'] == 'high_amount_entry']
        if high_amounts:
            recommendations.append(
                f"Examiner en détail {len(high_amounts)} écritures avec des montants élevés"
            )
        
        future_dates = [a for a in anomalies if a['type'] == 'future_date']
        if future_dates:
            recommendations.append(
                f"Corriger {len(future_dates)} écritures avec des dates futures"
            )
        
        if not recommendations:
            recommendations.append("Les écritures de journal semblent cohérentes.")
        
        return recommendations
    
    def _calculate_account_balances(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcule les soldes par classe de comptes"""
        balances = {}
        
        account_summary = df.groupby('account_number').agg({
            'debit_amount': 'sum',
            'credit_amount': 'sum'
        }).reset_index()
        
        account_summary['net_balance'] = account_summary['debit_amount'] - account_summary['credit_amount']
        
        # Regrouper par classe de comptes
        for _, account in account_summary.iterrows():
            account_class = str(account['account_number'])[0]
            class_name = {
                '1': 'actif_immobilise',
                '2': 'actif_circulant', 
                '3': 'stocks',
                '4': 'tiers',
                '5': 'financier',
                '6': 'charges',
                '7': 'produits'
            }.get(account_class, 'autres')
            
            if class_name not in balances:
                balances[class_name] = 0
            balances[class_name] += account['net_balance']
        
        return balances
    
    def _calculate_liquidity_ratios(self, balances: Dict[str, float]) -> Dict[str, float]:
        """Calcule les ratios de liquidité"""
        ratios = {}
        
        actif_circulant = balances.get('actif_circulant', 0) + balances.get('stocks', 0)
        passif_circulant = abs(balances.get('tiers', 0))  # Approximation
        
        if passif_circulant > 0:
            ratios['current_ratio'] = actif_circulant / passif_circulant
        
        return ratios
    
    def _calculate_solvency_ratios(self, balances: Dict[str, float]) -> Dict[str, float]:
        """Calcule les ratios de solvabilité"""
        ratios = {}
        
        total_actif = sum(v for k, v in balances.items() if k.startswith('actif'))
        total_passif = abs(sum(v for k, v in balances.items() if v < 0))
        
        if total_actif > 0:
            ratios['debt_to_assets'] = total_passif / total_actif
        
        return ratios
    
    def _calculate_activity_ratios(self, balances: Dict[str, float]) -> Dict[str, float]:
        """Calcule les ratios d'activité"""
        ratios = {}
        
        # Ratio de rotation des stocks (approximatif)
        charges = balances.get('charges', 0)
        stocks = balances.get('stocks', 0)
        
        if stocks > 0:
            ratios['inventory_turnover'] = charges / stocks
        
        return ratios
    
    def _interpret_ratios(self, ratios: Dict) -> List[str]:
        """Interprète les ratios calculés"""
        interpretations = []
        
        # Interprétation du ratio de liquidité
        current_ratio = ratios.get('liquidity', {}).get('current_ratio')
        if current_ratio:
            if current_ratio < 1:
                interpretations.append("Ratio de liquidité faible - risque de difficultés de trésorerie")
            elif current_ratio > 2:
                interpretations.append("Ratio de liquidité élevé - possible sur-liquidité")
            else:
                interpretations.append("Ratio de liquidité dans la norme")
        
        return interpretations
    
    def _assess_ratio_risk(self, ratios: Dict) -> str:
        """Évalue le risque basé sur les ratios"""
        risk_indicators = 0
        
        # Vérifier les ratios critiques
        current_ratio = ratios.get('liquidity', {}).get('current_ratio')
        if current_ratio and current_ratio < 1:
            risk_indicators += 2
        
        debt_ratio = ratios.get('solvency', {}).get('debt_to_assets')
        if debt_ratio and debt_ratio > 0.7:
            risk_indicators += 2
        
        if risk_indicators >= 3:
            return 'high'
        elif risk_indicators >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _benford_law_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse selon la loi de Benford pour détecter les manipulations"""
        # Extraire les premiers chiffres des montants
        amounts = pd.concat([df['debit_amount'], df['credit_amount']]).dropna()
        amounts = amounts[amounts > 0]
        
        if len(amounts) < 100:  # Échantillon trop petit
            return {'suspicious': False, 'reason': 'Échantillon insuffisant pour l\'analyse de Benford'}
        
        first_digits = [int(str(int(amount))[0]) for amount in amounts if str(int(amount))[0].isdigit()]
        
        # Distribution observée
        observed = pd.Series(first_digits).value_counts().sort_index()
        
        # Distribution théorique de Benford
        benford_expected = {i: np.log10(1 + 1/i) for i in range(1, 10)}
        
        # Test chi-carré simplifié
        chi_square = 0
        for digit in range(1, 10):
            expected_count = len(first_digits) * benford_expected[digit]
            observed_count = observed.get(digit, 0)
            if expected_count > 0:
                chi_square += ((observed_count - expected_count) ** 2) / expected_count
        
        # Seuil critique pour 8 degrés de liberté (approximatif)
        critical_value = 15.507
        
        return {
            'suspicious': chi_square > critical_value,
            'chi_square': chi_square,
            'critical_value': critical_value,
            'type': 'benford_law_violation',
            'severity': 'high' if chi_square > critical_value else 'low',
            'description': f"Test de la loi de Benford: chi² = {chi_square:.2f}"
        }
    
    def _detect_period_end_manipulation(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les manipulations en fin de période"""
        anomalies = []
        
        if 'entry_date' not in df.columns:
            return anomalies
        
        df['entry_date'] = pd.to_datetime(df['entry_date'], errors='coerce')
        df['day_of_month'] = df['entry_date'].dt.day
        
        # Concentration d'écritures en fin de mois
        end_of_month_entries = df[df['day_of_month'] >= 28]
        total_entries = len(df)
        
        if len(end_of_month_entries) / total_entries > 0.3:  # Plus de 30% en fin de mois
            anomalies.append({
                'type': 'period_end_concentration',
                'severity': 'medium',
                'description': f"Concentration élevée d'écritures en fin de mois: {len(end_of_month_entries)}/{total_entries}",
                'percentage': (len(end_of_month_entries) / total_entries) * 100
            })
        
        return anomalies
    
    def _detect_suspicious_round_amounts(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les montants ronds suspects"""
        anomalies = []
        
        amounts = pd.concat([df['debit_amount'], df['credit_amount']]).dropna()
        amounts = amounts[amounts > 0]
        
        # Montants ronds (multiples de 1000)
        round_amounts = amounts[amounts % 1000 == 0]
        
        if len(round_amounts) / len(amounts) > 0.2:  # Plus de 20% de montants ronds
            anomalies.append({
                'type': 'excessive_round_amounts',
                'severity': 'low',
                'description': f"Proportion élevée de montants ronds: {len(round_amounts)}/{len(amounts)}",
                'percentage': (len(round_amounts) / len(amounts)) * 100
            })
        
        return anomalies
    
    def _detect_after_hours_entries(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte les écritures saisies hors heures ouvrables"""
        # Cette fonction nécessiterait des timestamps précis avec heures
        # Pour l'instant, retourne une liste vide
        return []
    
    def _detect_unusual_account_usage(self, df: pd.DataFrame) -> List[Dict]:
        """Détecte l'utilisation inhabituelle de certains comptes"""
        anomalies = []
        
        # Comptes de régularisation utilisés fréquemment
        regularization_accounts = df[df['account_number'].str.startswith('47')]  # Comptes transitoires
        
        if len(regularization_accounts) > len(df) * 0.1:  # Plus de 10% des écritures
            anomalies.append({
                'type': 'excessive_regularization_accounts',
                'severity': 'medium',
                'description': f"Usage excessif des comptes de régularisation: {len(regularization_accounts)} écritures",
                'count': len(regularization_accounts)
            })
        
        return anomalies
    
    def _calculate_fraud_risk(self, indicators: List[Dict]) -> str:
        """Calcule le risque de fraude basé sur les indicateurs"""
        if not indicators:
            return 'low'
        
        high_risk_indicators = [i for i in indicators if i.get('severity') == 'high']
        medium_risk_indicators = [i for i in indicators if i.get('severity') == 'medium']
        
        if len(high_risk_indicators) >= 2:
            return 'critical'
        elif len(high_risk_indicators) >= 1 or len(medium_risk_indicators) >= 3:
            return 'high'
        elif len(medium_risk_indicators) >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_fraud_recommendations(self, indicators: List[Dict]) -> List[str]:
        """Génère des recommandations spécifiques à la détection de fraude"""
        recommendations = []
        
        if any(i['type'] == 'benford_law_violation' for i in indicators):
            recommendations.append("Effectuer un contrôle approfondi des montants - violation de la loi de Benford détectée")
        
        if any(i['type'] == 'period_end_concentration' for i in indicators):
            recommendations.append("Examiner les écritures de fin de période pour détecter d'éventuelles manipulations")
        
        if any(i['type'] == 'excessive_round_amounts' for i in indicators):
            recommendations.append("Vérifier la justification des montants ronds fréquents")
        
        if not recommendations:
            recommendations.append("Aucun indicateur de fraude majeur détecté")
        
        return recommendations

