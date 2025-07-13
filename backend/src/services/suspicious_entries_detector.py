"""
Service de détection d'écritures suspectes en comptabilité
Utilise des algorithmes pour identifier des patterns anormaux et potentiellement frauduleux
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
import re
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import Counter, defaultdict


class SuspicionLevel(Enum):
    """Niveaux de suspicion"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuspicionType(Enum):
    """Types de suspicions"""
    ROUND_AMOUNT = "round_amount"
    DUPLICATE_ENTRY = "duplicate_entry"
    UNUSUAL_TIMING = "unusual_timing"
    BENFORD_LAW_VIOLATION = "benford_law_violation"
    UNUSUAL_ACCOUNT_ACTIVITY = "unusual_account_activity"
    SEQUENTIAL_MANIPULATION = "sequential_manipulation"
    AMOUNT_JUST_BELOW_THRESHOLD = "amount_just_below_threshold"
    UNUSUAL_JOURNAL_PATTERN = "unusual_journal_pattern"
    WEEKEND_ENTRY = "weekend_entry"
    LATE_NIGHT_ENTRY = "late_night_entry"
    REVERSAL_PATTERN = "reversal_pattern"
    GHOST_EMPLOYEE = "ghost_employee"
    VENDOR_DUPLICATION = "vendor_duplication"


@dataclass
class SuspiciousEntry:
    """Écriture suspecte détectée"""
    entry_id: str
    suspicion_type: SuspicionType
    suspicion_level: SuspicionLevel
    description: str
    risk_score: float
    evidence: Dict[str, Any]
    recommendations: List[str]
    related_entries: List[str] = None
    account_affected: str = None
    amount: float = None
    date: str = None


class SuspiciousEntriesDetector:
    """Détecteur d'écritures suspectes"""
    
    def __init__(self):
        self.detection_rules = {
            'round_amounts': self._detect_round_amounts,
            'duplicates': self._detect_duplicates,
            'timing_anomalies': self._detect_timing_anomalies,
            'benford_law': self._check_benford_law,
            'account_activity': self._analyze_account_activity,
            'sequential_patterns': self._detect_sequential_patterns,
            'threshold_manipulation': self._detect_threshold_manipulation,
            'journal_patterns': self._analyze_journal_patterns,
            'reversal_patterns': self._detect_reversal_patterns,
            'entity_duplications': self._detect_entity_duplications
        }
        
        self.risk_thresholds = {
            'round_amount_percentage': 0.15,  # 15% de montants ronds = suspect
            'duplicate_tolerance_hours': 24,
            'benford_deviation_threshold': 0.05,
            'unusual_timing_hours': [22, 23, 0, 1, 2, 3, 4, 5],  # 22h-5h
            'threshold_proximity_percentage': 0.05,  # 5% en dessous du seuil
            'reversal_days_window': 7
        }
        
        # Loi de Benford - distribution attendue du premier chiffre
        self.benford_distribution = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
            6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
    
    def detect_suspicious_entries(self, data: List[Dict], detection_config: Optional[Dict] = None) -> Dict:
        """
        Détecte les écritures suspectes dans les données comptables
        
        Args:
            data: Données comptables
            detection_config: Configuration de détection (optionnelle)
            
        Returns:
            Dict contenant les résultats de détection
        """
        result = {
            'success': True,
            'detection_summary': {
                'total_entries': len(data),
                'suspicious_entries': 0,
                'risk_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                'detection_methods_used': []
            },
            'suspicious_entries': [],
            'risk_analysis': {},
            'recommendations': [],
            'processing_time': 0.0
        }
        
        try:
            start_time = datetime.now()
            
            if not data:
                result['success'] = False
                result['error'] = "Aucune donnée fournie pour la détection"
                return result
            
            # Préparer les données
            df = self._prepare_dataframe(data)
            if df.empty:
                result['success'] = False
                result['error'] = "Impossible de préparer les données pour la détection"
                return result
            
            # Configuration de détection
            config = detection_config or {}
            enabled_rules = config.get('enabled_rules', list(self.detection_rules.keys()))
            
            all_suspicious_entries = []
            
            # Appliquer les règles de détection
            for rule_name in enabled_rules:
                if rule_name in self.detection_rules:
                    try:
                        suspicious_entries = self.detection_rules[rule_name](df, config)
                        all_suspicious_entries.extend(suspicious_entries)
                        result['detection_summary']['detection_methods_used'].append(rule_name)
                    except Exception as e:
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append(f"Erreur dans {rule_name}: {str(e)}")
            
            # Trier par score de risque
            all_suspicious_entries.sort(key=lambda x: x.risk_score, reverse=True)
            
            # Convertir en dictionnaires
            result['suspicious_entries'] = [self._entry_to_dict(entry) for entry in all_suspicious_entries]
            
            # Calculer les statistiques
            result['detection_summary']['suspicious_entries'] = len(all_suspicious_entries)
            for entry in all_suspicious_entries:
                result['detection_summary']['risk_distribution'][entry.suspicion_level.value] += 1
            
            # Analyse des risques
            result['risk_analysis'] = self._calculate_risk_analysis(all_suspicious_entries, df)
            
            # Générer des recommandations
            result['recommendations'] = self._generate_recommendations(all_suspicious_entries)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur détection écritures suspectes: {str(e)}"
        
        return result
    
    def _prepare_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Prépare un DataFrame pandas à partir des données"""
        try:
            df = pd.DataFrame(data)
            
            # Standardiser les noms de colonnes
            column_mapping = {
                'EcritureDate': 'date',
                'EcritureNum': 'entry_id',
                'CompteNum': 'account',
                'CompteLib': 'account_name',
                'EcritureLib': 'description',
                'PieceRef': 'reference',
                'JournalCode': 'journal',
                'Debit': 'debit',
                'Credit': 'credit'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df[new_col] = df[old_col]
            
            # Convertir les dates
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Convertir les montants
            for col in ['debit', 'credit', 'montant']:
                if col in df.columns:
                    df[col] = df[col].apply(self._parse_amount)
            
            # Créer une colonne montant si elle n'existe pas
            if 'montant' not in df.columns:
                if 'debit' in df.columns and 'credit' in df.columns:
                    df['montant'] = df['debit'] + df['credit']
                elif 'debit' in df.columns:
                    df['montant'] = df['debit']
                elif 'credit' in df.columns:
                    df['montant'] = df['credit']
            
            # Créer un ID d'entrée si il n'existe pas
            if 'entry_id' not in df.columns:
                df['entry_id'] = df.index.astype(str)
            
            return df
            
        except Exception as e:
            print(f"Erreur préparation DataFrame: {e}")
            return pd.DataFrame()
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse un montant en float"""
        if pd.isna(amount_str):
            return 0.0
        
        amount_str = str(amount_str).strip()
        amount_str = re.sub(r'[^\d,\.\-]', '', amount_str)
        amount_str = amount_str.replace(',', '.')
        
        try:
            return float(amount_str)
        except:
            return 0.0
    
    def _detect_round_amounts(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les montants ronds suspects"""
        suspicious_entries = []
        
        if 'montant' not in df.columns:
            return suspicious_entries
        
        try:
            # Identifier les montants ronds
            round_amounts = df[df['montant'] % 100 == 0]  # Multiples de 100
            very_round_amounts = df[df['montant'] % 1000 == 0]  # Multiples de 1000
            
            total_entries = len(df)
            round_percentage = len(round_amounts) / total_entries if total_entries > 0 else 0
            
            # Si trop de montants ronds, c'est suspect
            if round_percentage > self.risk_thresholds['round_amount_percentage']:
                for _, entry in round_amounts.iterrows():
                    risk_score = 0.3 if entry['montant'] % 1000 == 0 else 0.2
                    
                    suspicious_entries.append(SuspiciousEntry(
                        entry_id=str(entry['entry_id']),
                        suspicion_type=SuspicionType.ROUND_AMOUNT,
                        suspicion_level=SuspicionLevel.MEDIUM if risk_score > 0.25 else SuspicionLevel.LOW,
                        description=f"Montant rond suspect: {entry['montant']:.2f}",
                        risk_score=risk_score,
                        evidence={
                            'amount': entry['montant'],
                            'round_percentage': round_percentage,
                            'is_very_round': entry['montant'] % 1000 == 0
                        },
                        recommendations=[
                            "Vérifier les pièces justificatives",
                            "Confirmer que le montant exact est correct"
                        ],
                        account_affected=entry.get('account', ''),
                        amount=entry['montant'],
                        date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                    ))
        
        except Exception as e:
            print(f"Erreur détection montants ronds: {e}")
        
        return suspicious_entries
    
    def _detect_duplicates(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les écritures en double"""
        suspicious_entries = []
        
        try:
            # Grouper par montant, compte et description
            duplicate_columns = ['montant', 'account', 'description']
            available_columns = [col for col in duplicate_columns if col in df.columns]
            
            if len(available_columns) < 2:
                return suspicious_entries
            
            # Identifier les doublons potentiels
            duplicates = df.groupby(available_columns).size()
            duplicates = duplicates[duplicates > 1]
            
            for group_key, count in duplicates.items():
                # Récupérer les entrées en double
                if len(available_columns) == 3:
                    duplicate_entries = df[
                        (df['montant'] == group_key[0]) &
                        (df['account'] == group_key[1]) &
                        (df['description'] == group_key[2])
                    ]
                elif len(available_columns) == 2:
                    duplicate_entries = df[
                        (df[available_columns[0]] == group_key[0]) &
                        (df[available_columns[1]] == group_key[1])
                    ]
                
                # Vérifier la proximité temporelle
                if 'date' in df.columns:
                    duplicate_entries = duplicate_entries.sort_values('date')
                    dates = duplicate_entries['date'].dropna()
                    
                    if len(dates) > 1:
                        time_diff = (dates.iloc[-1] - dates.iloc[0]).total_seconds() / 3600
                        
                        if time_diff <= self.risk_thresholds['duplicate_tolerance_hours']:
                            risk_score = 0.8 if time_diff <= 1 else 0.6
                            
                            for _, entry in duplicate_entries.iterrows():
                                suspicious_entries.append(SuspiciousEntry(
                                    entry_id=str(entry['entry_id']),
                                    suspicion_type=SuspicionType.DUPLICATE_ENTRY,
                                    suspicion_level=SuspicionLevel.HIGH if risk_score > 0.7 else SuspicionLevel.MEDIUM,
                                    description=f"Écriture potentiellement en double (montant: {entry['montant']:.2f})",
                                    risk_score=risk_score,
                                    evidence={
                                        'duplicate_count': count,
                                        'time_difference_hours': time_diff,
                                        'matching_fields': available_columns
                                    },
                                    recommendations=[
                                        "Vérifier s'il s'agit d'un doublon",
                                        "Contrôler les pièces justificatives",
                                        "Supprimer l'écriture en double si confirmé"
                                    ],
                                    related_entries=[str(e) for e in duplicate_entries['entry_id'].tolist()],
                                    account_affected=entry.get('account', ''),
                                    amount=entry['montant'],
                                    date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                                ))
        
        except Exception as e:
            print(f"Erreur détection doublons: {e}")
        
        return suspicious_entries
    
    def _detect_timing_anomalies(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les anomalies de timing"""
        suspicious_entries = []
        
        if 'date' not in df.columns:
            return suspicious_entries
        
        try:
            df_with_time = df.dropna(subset=['date'])
            
            # Détecter les écritures en dehors des heures ouvrables
            if 'date' in df.columns:
                df_with_time['hour'] = df_with_time['date'].dt.hour
                df_with_time['weekday'] = df_with_time['date'].dt.weekday
                
                # Écritures nocturnes (22h-5h)
                night_entries = df_with_time[df_with_time['hour'].isin(self.risk_thresholds['unusual_timing_hours'])]
                
                for _, entry in night_entries.iterrows():
                    suspicious_entries.append(SuspiciousEntry(
                        entry_id=str(entry['entry_id']),
                        suspicion_type=SuspicionType.LATE_NIGHT_ENTRY,
                        suspicion_level=SuspicionLevel.MEDIUM,
                        description=f"Écriture saisie à {entry['hour']}h",
                        risk_score=0.4,
                        evidence={
                            'hour': entry['hour'],
                            'is_weekend': entry['weekday'] >= 5
                        },
                        recommendations=[
                            "Vérifier la justification de cette saisie nocturne",
                            "Contrôler l'autorisation de l'utilisateur"
                        ],
                        account_affected=entry.get('account', ''),
                        amount=entry.get('montant', 0),
                        date=entry['date'].strftime('%Y-%m-%d %H:%M')
                    ))
                
                # Écritures le weekend
                weekend_entries = df_with_time[df_with_time['weekday'] >= 5]
                
                for _, entry in weekend_entries.iterrows():
                    suspicious_entries.append(SuspiciousEntry(
                        entry_id=str(entry['entry_id']),
                        suspicion_type=SuspicionType.WEEKEND_ENTRY,
                        suspicion_level=SuspicionLevel.LOW,
                        description="Écriture saisie le weekend",
                        risk_score=0.2,
                        evidence={
                            'weekday': entry['weekday'],
                            'day_name': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][entry['weekday']]
                        },
                        recommendations=[
                            "Vérifier si cette saisie weekend est justifiée"
                        ],
                        account_affected=entry.get('account', ''),
                        amount=entry.get('montant', 0),
                        date=entry['date'].strftime('%Y-%m-%d')
                    ))
        
        except Exception as e:
            print(f"Erreur détection anomalies timing: {e}")
        
        return suspicious_entries
    
    def _check_benford_law(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Vérifie la conformité à la loi de Benford"""
        suspicious_entries = []
        
        if 'montant' not in df.columns:
            return suspicious_entries
        
        try:
            # Extraire le premier chiffre des montants
            amounts = df[df['montant'] > 0]['montant']
            if len(amounts) < 50:  # Pas assez de données pour Benford
                return suspicious_entries
            
            first_digits = amounts.apply(lambda x: int(str(int(x))[0]))
            digit_counts = first_digits.value_counts().sort_index()
            
            # Calculer la distribution observée
            total_count = len(first_digits)
            observed_distribution = {}
            
            for digit in range(1, 10):
                observed_freq = digit_counts.get(digit, 0) / total_count
                expected_freq = self.benford_distribution[digit]
                deviation = abs(observed_freq - expected_freq)
                
                if deviation > self.risk_thresholds['benford_deviation_threshold']:
                    # Identifier les entrées avec ce premier chiffre
                    entries_with_digit = df[df['montant'].apply(lambda x: int(str(int(x))[0]) == digit if x > 0 else False)]
                    
                    for _, entry in entries_with_digit.iterrows():
                        suspicious_entries.append(SuspiciousEntry(
                            entry_id=str(entry['entry_id']),
                            suspicion_type=SuspicionType.BENFORD_LAW_VIOLATION,
                            suspicion_level=SuspicionLevel.MEDIUM if deviation > 0.1 else SuspicionLevel.LOW,
                            description=f"Violation loi de Benford - premier chiffre {digit}",
                            risk_score=min(deviation * 2, 1.0),
                            evidence={
                                'first_digit': digit,
                                'observed_frequency': observed_freq,
                                'expected_frequency': expected_freq,
                                'deviation': deviation
                            },
                            recommendations=[
                                "Analyser la distribution des montants",
                                "Vérifier s'il y a manipulation des chiffres"
                            ],
                            account_affected=entry.get('account', ''),
                            amount=entry['montant'],
                            date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                        ))
        
        except Exception as e:
            print(f"Erreur vérification loi Benford: {e}")
        
        return suspicious_entries
    
    def _analyze_account_activity(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Analyse l'activité inhabituelle des comptes"""
        suspicious_entries = []
        
        if 'account' not in df.columns or 'montant' not in df.columns:
            return suspicious_entries
        
        try:
            # Analyser l'activité par compte
            account_stats = df.groupby('account')['montant'].agg(['count', 'sum', 'mean', 'std']).reset_index()
            
            # Détecter les comptes avec activité anormale
            mean_activity = account_stats['count'].mean()
            std_activity = account_stats['count'].std()
            
            if std_activity > 0:
                for _, account_stat in account_stats.iterrows():
                    z_score = abs(account_stat['count'] - mean_activity) / std_activity
                    
                    if z_score > 2.0:  # Activité anormalement élevée
                        account_entries = df[df['account'] == account_stat['account']]
                        
                        for _, entry in account_entries.iterrows():
                            suspicious_entries.append(SuspiciousEntry(
                                entry_id=str(entry['entry_id']),
                                suspicion_type=SuspicionType.UNUSUAL_ACCOUNT_ACTIVITY,
                                suspicion_level=SuspicionLevel.MEDIUM if z_score > 3.0 else SuspicionLevel.LOW,
                                description=f"Activité anormale sur compte {account_stat['account']}",
                                risk_score=min(z_score / 5.0, 1.0),
                                evidence={
                                    'account': account_stat['account'],
                                    'transaction_count': account_stat['count'],
                                    'z_score': z_score,
                                    'total_amount': account_stat['sum']
                                },
                                recommendations=[
                                    "Analyser la justification de cette activité élevée",
                                    "Vérifier les autorisations sur ce compte"
                                ],
                                account_affected=account_stat['account'],
                                amount=entry['montant'],
                                date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                            ))
        
        except Exception as e:
            print(f"Erreur analyse activité comptes: {e}")
        
        return suspicious_entries
    
    def _detect_sequential_patterns(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les patterns séquentiels suspects"""
        suspicious_entries = []
        
        if 'montant' not in df.columns:
            return suspicious_entries
        
        try:
            # Détecter les séquences de montants identiques ou très proches
            df_sorted = df.sort_values('montant')
            
            consecutive_similar = []
            current_group = [df_sorted.iloc[0]]
            
            for i in range(1, len(df_sorted)):
                current_amount = df_sorted.iloc[i]['montant']
                prev_amount = df_sorted.iloc[i-1]['montant']
                
                if abs(current_amount - prev_amount) <= 0.01:  # Montants identiques ou très proches
                    current_group.append(df_sorted.iloc[i])
                else:
                    if len(current_group) >= 5:  # 5 montants identiques ou plus
                        consecutive_similar.append(current_group)
                    current_group = [df_sorted.iloc[i]]
            
            # Vérifier le dernier groupe
            if len(current_group) >= 5:
                consecutive_similar.append(current_group)
            
            # Marquer comme suspects
            for group in consecutive_similar:
                for entry in group:
                    suspicious_entries.append(SuspiciousEntry(
                        entry_id=str(entry['entry_id']),
                        suspicion_type=SuspicionType.SEQUENTIAL_MANIPULATION,
                        suspicion_level=SuspicionLevel.HIGH if len(group) > 10 else SuspicionLevel.MEDIUM,
                        description=f"Séquence de {len(group)} montants identiques: {entry['montant']:.2f}",
                        risk_score=min(len(group) / 20.0, 1.0),
                        evidence={
                            'sequence_length': len(group),
                            'amount': entry['montant']
                        },
                        recommendations=[
                            "Vérifier la légitimité de ces montants identiques",
                            "Analyser les pièces justificatives correspondantes"
                        ],
                        related_entries=[str(e['entry_id']) for e in group],
                        account_affected=entry.get('account', ''),
                        amount=entry['montant'],
                        date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                    ))
        
        except Exception as e:
            print(f"Erreur détection patterns séquentiels: {e}")
        
        return suspicious_entries
    
    def _detect_threshold_manipulation(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les manipulations de seuils"""
        suspicious_entries = []
        
        if 'montant' not in df.columns:
            return suspicious_entries
        
        try:
            # Seuils communs en comptabilité
            common_thresholds = [1000, 5000, 10000, 50000, 100000]
            
            for threshold in common_thresholds:
                # Chercher les montants juste en dessous du seuil
                proximity_amount = threshold * self.risk_thresholds['threshold_proximity_percentage']
                near_threshold = df[
                    (df['montant'] >= threshold - proximity_amount) & 
                    (df['montant'] < threshold)
                ]
                
                if len(near_threshold) > 0:
                    # Calculer la concentration près du seuil
                    total_near = len(near_threshold)
                    total_in_range = len(df[
                        (df['montant'] >= threshold - proximity_amount * 10) & 
                        (df['montant'] <= threshold + proximity_amount * 10)
                    ])
                    
                    if total_in_range > 0:
                        concentration = total_near / total_in_range
                        
                        if concentration > 0.5:  # Plus de 50% des montants près du seuil sont en dessous
                            for _, entry in near_threshold.iterrows():
                                suspicious_entries.append(SuspiciousEntry(
                                    entry_id=str(entry['entry_id']),
                                    suspicion_type=SuspicionType.AMOUNT_JUST_BELOW_THRESHOLD,
                                    suspicion_level=SuspicionLevel.MEDIUM,
                                    description=f"Montant juste sous le seuil de {threshold}: {entry['montant']:.2f}",
                                    risk_score=concentration,
                                    evidence={
                                        'threshold': threshold,
                                        'amount': entry['montant'],
                                        'distance_to_threshold': threshold - entry['montant'],
                                        'concentration': concentration
                                    },
                                    recommendations=[
                                        "Vérifier si ce montant a été volontairement maintenu sous le seuil",
                                        "Analyser la justification métier"
                                    ],
                                    account_affected=entry.get('account', ''),
                                    amount=entry['montant'],
                                    date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                                ))
        
        except Exception as e:
            print(f"Erreur détection manipulation seuils: {e}")
        
        return suspicious_entries
    
    def _analyze_journal_patterns(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Analyse les patterns de journaux suspects"""
        suspicious_entries = []
        
        if 'journal' not in df.columns:
            return suspicious_entries
        
        try:
            # Analyser la distribution par journal
            journal_stats = df.groupby('journal').agg({
                'montant': ['count', 'sum', 'mean'],
                'entry_id': 'count'
            }).reset_index()
            
            # Aplatir les colonnes multi-niveaux
            journal_stats.columns = ['journal', 'count', 'total_amount', 'avg_amount', 'entry_count']
            
            # Détecter les journaux avec patterns anormaux
            mean_entries = journal_stats['count'].mean()
            std_entries = journal_stats['count'].std()
            
            if std_entries > 0:
                for _, journal_stat in journal_stats.iterrows():
                    z_score = abs(journal_stat['count'] - mean_entries) / std_entries
                    
                    if z_score > 2.5:  # Journal avec activité anormale
                        journal_entries = df[df['journal'] == journal_stat['journal']]
                        
                        # Marquer quelques entrées représentatives
                        sample_entries = journal_entries.head(5)
                        
                        for _, entry in sample_entries.iterrows():
                            suspicious_entries.append(SuspiciousEntry(
                                entry_id=str(entry['entry_id']),
                                suspicion_type=SuspicionType.UNUSUAL_JOURNAL_PATTERN,
                                suspicion_level=SuspicionLevel.MEDIUM if z_score > 3.0 else SuspicionLevel.LOW,
                                description=f"Pattern anormal dans journal {journal_stat['journal']}",
                                risk_score=min(z_score / 5.0, 1.0),
                                evidence={
                                    'journal': journal_stat['journal'],
                                    'entry_count': journal_stat['count'],
                                    'z_score': z_score,
                                    'avg_amount': journal_stat['avg_amount']
                                },
                                recommendations=[
                                    "Analyser l'utilisation de ce journal",
                                    "Vérifier les autorisations d'accès"
                                ],
                                account_affected=entry.get('account', ''),
                                amount=entry['montant'],
                                date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                            ))
        
        except Exception as e:
            print(f"Erreur analyse patterns journaux: {e}")
        
        return suspicious_entries
    
    def _detect_reversal_patterns(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les patterns d'annulation suspects"""
        suspicious_entries = []
        
        if 'montant' not in df.columns or 'date' not in df.columns:
            return suspicious_entries
        
        try:
            # Chercher les montants opposés dans une fenêtre de temps
            df_sorted = df.sort_values('date')
            
            for i, entry in df_sorted.iterrows():
                amount = entry['montant']
                date = entry['date']
                
                # Chercher les montants opposés dans les jours suivants
                window_end = date + timedelta(days=self.risk_thresholds['reversal_days_window'])
                window_entries = df_sorted[
                    (df_sorted['date'] > date) & 
                    (df_sorted['date'] <= window_end) &
                    (abs(df_sorted['montant'] + amount) < 0.01)  # Montant opposé
                ]
                
                if len(window_entries) > 0:
                    for _, reversal_entry in window_entries.iterrows():
                        days_diff = (reversal_entry['date'] - date).days
                        
                        suspicious_entries.append(SuspiciousEntry(
                            entry_id=str(entry['entry_id']),
                            suspicion_type=SuspicionType.REVERSAL_PATTERN,
                            suspicion_level=SuspicionLevel.HIGH if days_diff <= 1 else SuspicionLevel.MEDIUM,
                            description=f"Pattern d'annulation détecté après {days_diff} jour(s)",
                            risk_score=max(0.3, 1.0 - (days_diff / 7.0)),
                            evidence={
                                'original_amount': amount,
                                'reversal_amount': reversal_entry['montant'],
                                'days_between': days_diff,
                                'reversal_entry_id': reversal_entry['entry_id']
                            },
                            recommendations=[
                                "Vérifier la justification de cette annulation",
                                "Analyser si c'est une tentative de dissimulation"
                            ],
                            related_entries=[str(reversal_entry['entry_id'])],
                            account_affected=entry.get('account', ''),
                            amount=amount,
                            date=date.strftime('%Y-%m-%d')
                        ))
        
        except Exception as e:
            print(f"Erreur détection patterns annulation: {e}")
        
        return suspicious_entries
    
    def _detect_entity_duplications(self, df: pd.DataFrame, config: Dict) -> List[SuspiciousEntry]:
        """Détecte les duplications d'entités (fournisseurs fantômes, etc.)"""
        suspicious_entries = []
        
        # Cette fonction nécessiterait des données sur les fournisseurs/clients
        # Pour l'instant, on simule avec les descriptions
        
        if 'description' not in df.columns:
            return suspicious_entries
        
        try:
            # Analyser les similitudes dans les descriptions
            descriptions = df['description'].dropna().str.lower()
            
            # Détecter les descriptions très similaires
            similar_groups = defaultdict(list)
            
            for i, desc1 in enumerate(descriptions):
                for j, desc2 in enumerate(descriptions):
                    if i < j:
                        # Calculer la similarité simple (mots communs)
                        words1 = set(desc1.split())
                        words2 = set(desc2.split())
                        
                        if len(words1) > 0 and len(words2) > 0:
                            similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                            
                            if similarity > 0.8 and len(words1) > 2:  # Très similaire
                                key = tuple(sorted([desc1, desc2]))
                                similar_groups[key].extend([i, j])
            
            # Marquer les entrées avec descriptions suspectes
            for group_key, indices in similar_groups.items():
                if len(set(indices)) > 2:  # Plus de 2 entrées similaires
                    for idx in set(indices):
                        entry = df.iloc[idx]
                        
                        suspicious_entries.append(SuspiciousEntry(
                            entry_id=str(entry['entry_id']),
                            suspicion_type=SuspicionType.VENDOR_DUPLICATION,
                            suspicion_level=SuspicionLevel.MEDIUM,
                            description=f"Description suspecte similaire à d'autres: {entry['description'][:50]}...",
                            risk_score=0.5,
                            evidence={
                                'similar_descriptions': list(group_key),
                                'similar_count': len(set(indices))
                            },
                            recommendations=[
                                "Vérifier s'il s'agit d'entités distinctes",
                                "Contrôler les informations fournisseur/client"
                            ],
                            account_affected=entry.get('account', ''),
                            amount=entry.get('montant', 0),
                            date=entry.get('date', '').strftime('%Y-%m-%d') if pd.notna(entry.get('date')) else ''
                        ))
        
        except Exception as e:
            print(f"Erreur détection duplications entités: {e}")
        
        return suspicious_entries
    
    def _calculate_risk_analysis(self, suspicious_entries: List[SuspiciousEntry], df: pd.DataFrame) -> Dict:
        """Calcule l'analyse des risques globale"""
        analysis = {
            'overall_risk_score': 0.0,
            'risk_factors': {},
            'most_common_suspicions': {},
            'high_risk_accounts': [],
            'temporal_risk_distribution': {}
        }
        
        try:
            if not suspicious_entries:
                return analysis
            
            # Score de risque global
            total_risk = sum(entry.risk_score for entry in suspicious_entries)
            analysis['overall_risk_score'] = min(total_risk / len(df), 1.0)
            
            # Facteurs de risque
            suspicion_counts = Counter(entry.suspicion_type.value for entry in suspicious_entries)
            analysis['most_common_suspicions'] = dict(suspicion_counts.most_common(5))
            
            # Comptes à haut risque
            account_risks = defaultdict(list)
            for entry in suspicious_entries:
                if entry.account_affected:
                    account_risks[entry.account_affected].append(entry.risk_score)
            
            high_risk_accounts = []
            for account, risks in account_risks.items():
                avg_risk = sum(risks) / len(risks)
                if avg_risk > 0.5:
                    high_risk_accounts.append({
                        'account': account,
                        'avg_risk_score': avg_risk,
                        'suspicious_entries_count': len(risks)
                    })
            
            analysis['high_risk_accounts'] = sorted(high_risk_accounts, key=lambda x: x['avg_risk_score'], reverse=True)[:10]
            
        except Exception as e:
            print(f"Erreur calcul analyse risques: {e}")
        
        return analysis
    
    def _generate_recommendations(self, suspicious_entries: List[SuspiciousEntry]) -> List[str]:
        """Génère des recommandations basées sur les détections"""
        recommendations = []
        
        if not suspicious_entries:
            recommendations.append("Aucune écriture suspecte détectée - situation normale")
            return recommendations
        
        # Compter les types de suspicions
        suspicion_counts = Counter(entry.suspicion_type.value for entry in suspicious_entries)
        
        # Recommandations spécifiques
        if suspicion_counts.get('duplicate_entry', 0) > 0:
            recommendations.append(f"Contrôler {suspicion_counts['duplicate_entry']} doublon(s) potentiel(s)")
        
        if suspicion_counts.get('round_amount', 0) > 5:
            recommendations.append("Analyser la fréquence élevée de montants ronds")
        
        if suspicion_counts.get('benford_law_violation', 0) > 0:
            recommendations.append("Investiguer les violations de la loi de Benford")
        
        if suspicion_counts.get('reversal_pattern', 0) > 0:
            recommendations.append("Examiner les patterns d'annulation suspects")
        
        # Recommandations générales
        critical_count = sum(1 for entry in suspicious_entries if entry.suspicion_level == SuspicionLevel.CRITICAL)
        high_count = sum(1 for entry in suspicious_entries if entry.suspicion_level == SuspicionLevel.HIGH)
        
        if critical_count > 0:
            recommendations.append(f"Traiter en urgence {critical_count} suspicion(s) critique(s)")
        
        if high_count > 0:
            recommendations.append(f"Investiguer {high_count} suspicion(s) à haut risque")
        
        recommendations.append("Renforcer les contrôles internes sur les écritures comptables")
        
        return recommendations
    
    def _entry_to_dict(self, entry: SuspiciousEntry) -> Dict:
        """Convertit une entrée suspecte en dictionnaire"""
        return {
            'entry_id': entry.entry_id,
            'suspicion_type': entry.suspicion_type.value,
            'suspicion_level': entry.suspicion_level.value,
            'description': entry.description,
            'risk_score': entry.risk_score,
            'evidence': entry.evidence,
            'recommendations': entry.recommendations,
            'related_entries': entry.related_entries or [],
            'account_affected': entry.account_affected,
            'amount': entry.amount,
            'date': entry.date
        }
    
    def get_detection_rules(self) -> List[str]:
        """Retourne la liste des règles de détection disponibles"""
        return list(self.detection_rules.keys())
    
    def configure_thresholds(self, new_thresholds: Dict) -> None:
        """Configure les seuils de détection"""
        self.risk_thresholds.update(new_thresholds)

