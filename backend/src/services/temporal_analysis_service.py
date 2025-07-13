"""
Service d'analyse de cohérence temporelle en comptabilité
Analyse les données comptables dans le temps pour détecter des anomalies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
from dataclasses import dataclass
from enum import Enum
import statistics
import re


class TemporalAnomalyType(Enum):
    """Types d'anomalies temporelles"""
    SEASONAL_DEVIATION = "seasonal_deviation"
    TREND_BREAK = "trend_break"
    OUTLIER = "outlier"
    MISSING_PERIOD = "missing_period"
    DUPLICATE_ENTRY = "duplicate_entry"
    RETROACTIVE_ENTRY = "retroactive_entry"
    FUTURE_ENTRY = "future_entry"
    INCONSISTENT_FREQUENCY = "inconsistent_frequency"


@dataclass
class TemporalAnomaly:
    """Anomalie temporelle détectée"""
    type: TemporalAnomalyType
    severity: str  # low, medium, high, critical
    description: str
    period: str
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    confidence: float = 1.0
    recommendations: List[str] = None
    affected_accounts: List[str] = None


class TemporalAnalysisService:
    """Service d'analyse de cohérence temporelle"""
    
    def __init__(self):
        self.analysis_methods = {
            'trend_analysis': self._analyze_trends,
            'seasonal_analysis': self._analyze_seasonality,
            'outlier_detection': self._detect_outliers,
            'frequency_analysis': self._analyze_frequency,
            'gap_detection': self._detect_gaps,
            'retroactive_analysis': self._analyze_retroactive_entries
        }
        
        self.severity_thresholds = {
            'outlier_zscore': 2.0,  # Z-score pour détecter les outliers
            'trend_deviation': 0.3,  # Déviation de tendance (30%)
            'seasonal_deviation': 0.5,  # Déviation saisonnière (50%)
            'missing_period_days': 7,  # Jours pour considérer une période manquante
            'retroactive_days': 30  # Jours pour considérer une écriture rétroactive
        }
    
    def analyze_temporal_coherence(self, data: List[Dict], analysis_config: Optional[Dict] = None) -> Dict:
        """
        Analyse la cohérence temporelle des données comptables
        
        Args:
            data: Données comptables avec dates et montants
            analysis_config: Configuration d'analyse (optionnelle)
            
        Returns:
            Dict contenant les résultats d'analyse
        """
        result = {
            'success': True,
            'analysis_summary': {
                'total_records': len(data),
                'date_range': {},
                'anomalies_count': 0,
                'severity_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            },
            'anomalies': [],
            'trends': {},
            'seasonal_patterns': {},
            'recommendations': [],
            'processing_time': 0.0
        }
        
        try:
            start_time = datetime.now()
            
            if not data:
                result['success'] = False
                result['error'] = "Aucune donnée fournie pour l'analyse"
                return result
            
            # Préparer les données
            df = self._prepare_dataframe(data)
            if df.empty:
                result['success'] = False
                result['error'] = "Impossible de préparer les données pour l'analyse"
                return result
            
            # Calculer la plage de dates
            result['analysis_summary']['date_range'] = {
                'start_date': df['date'].min().strftime('%Y-%m-%d'),
                'end_date': df['date'].max().strftime('%Y-%m-%d'),
                'total_days': (df['date'].max() - df['date'].min()).days
            }
            
            # Effectuer les analyses selon la configuration
            config = analysis_config or {}
            enabled_analyses = config.get('enabled_analyses', list(self.analysis_methods.keys()))
            
            all_anomalies = []
            
            for analysis_name in enabled_analyses:
                if analysis_name in self.analysis_methods:
                    try:
                        anomalies = self.analysis_methods[analysis_name](df, config)
                        all_anomalies.extend(anomalies)
                    except Exception as e:
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append(f"Erreur dans {analysis_name}: {str(e)}")
            
            # Trier les anomalies par sévérité
            all_anomalies.sort(key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.severity], reverse=True)
            
            # Convertir en dictionnaires pour la sérialisation
            result['anomalies'] = [self._anomaly_to_dict(anomaly) for anomaly in all_anomalies]
            
            # Calculer les statistiques
            result['analysis_summary']['anomalies_count'] = len(all_anomalies)
            for anomaly in all_anomalies:
                result['analysis_summary']['severity_distribution'][anomaly.severity] += 1
            
            # Analyser les tendances
            result['trends'] = self._calculate_trends(df)
            
            # Analyser les patterns saisonniers
            result['seasonal_patterns'] = self._calculate_seasonal_patterns(df)
            
            # Générer des recommandations
            result['recommendations'] = self._generate_recommendations(all_anomalies, df)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur analyse temporelle: {str(e)}"
        
        return result
    
    def _prepare_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Prépare un DataFrame pandas à partir des données"""
        try:
            # Convertir en DataFrame
            df = pd.DataFrame(data)
            
            # Identifier les colonnes de date
            date_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'periode', 'time']):
                    date_columns.append(col)
            
            if not date_columns:
                # Essayer de détecter automatiquement
                for col in df.columns:
                    sample_values = df[col].dropna().head(5)
                    if all(self._is_date_like(str(val)) for val in sample_values):
                        date_columns.append(col)
                        break
            
            if not date_columns:
                raise ValueError("Aucune colonne de date trouvée")
            
            # Utiliser la première colonne de date trouvée
            date_col = date_columns[0]
            df['date'] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Identifier les colonnes de montant
            amount_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['montant', 'amount', 'debit', 'credit', 'solde', 'total']):
                    amount_columns.append(col)
            
            # Convertir les montants en numérique
            for col in amount_columns:
                df[col] = df[col].apply(self._parse_amount)
            
            # Créer une colonne montant principale si elle n'existe pas
            if 'montant' not in df.columns and amount_columns:
                df['montant'] = df[amount_columns[0]]
            
            # Supprimer les lignes avec des dates invalides
            df = df.dropna(subset=['date'])
            
            # Trier par date
            df = df.sort_values('date')
            
            return df
            
        except Exception as e:
            print(f"Erreur préparation DataFrame: {e}")
            return pd.DataFrame()
    
    def _is_date_like(self, value: str) -> bool:
        """Vérifie si une valeur ressemble à une date"""
        date_patterns = [
            r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
            r'\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}',
            r'\d{8}',  # YYYYMMDD
            r'\d{6}'   # YYMMDD
        ]
        
        return any(re.match(pattern, str(value).strip()) for pattern in date_patterns)
    
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
    
    def _analyze_trends(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Analyse les tendances temporelles"""
        anomalies = []
        
        if 'montant' not in df.columns or len(df) < 10:
            return anomalies
        
        try:
            # Grouper par mois pour l'analyse de tendance
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_data = df.groupby('year_month')['montant'].sum().reset_index()
            monthly_data['year_month'] = monthly_data['year_month'].dt.to_timestamp()
            
            if len(monthly_data) < 3:
                return anomalies
            
            # Calculer la tendance linéaire
            x = np.arange(len(monthly_data))
            y = monthly_data['montant'].values
            
            # Régression linéaire simple
            slope, intercept = np.polyfit(x, y, 1)
            trend_line = slope * x + intercept
            
            # Détecter les ruptures de tendance
            for i in range(2, len(monthly_data)):
                actual = y[i]
                expected = trend_line[i]
                
                if expected != 0:
                    deviation = abs(actual - expected) / abs(expected)
                    
                    if deviation > self.severity_thresholds['trend_deviation']:
                        severity = 'high' if deviation > 0.5 else 'medium'
                        
                        anomalies.append(TemporalAnomaly(
                            type=TemporalAnomalyType.TREND_BREAK,
                            severity=severity,
                            description=f"Rupture de tendance détectée en {monthly_data.iloc[i]['year_month'].strftime('%m/%Y')}",
                            period=monthly_data.iloc[i]['year_month'].strftime('%Y-%m'),
                            expected_value=expected,
                            actual_value=actual,
                            confidence=min(deviation, 1.0),
                            recommendations=[
                                "Vérifier les écritures comptables de cette période",
                                "Analyser les événements exceptionnels du mois"
                            ]
                        ))
        
        except Exception as e:
            print(f"Erreur analyse tendances: {e}")
        
        return anomalies
    
    def _analyze_seasonality(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Analyse les patterns saisonniers"""
        anomalies = []
        
        if 'montant' not in df.columns or len(df) < 24:  # Au moins 2 ans de données
            return anomalies
        
        try:
            # Grouper par mois de l'année
            df['month'] = df['date'].dt.month
            monthly_patterns = df.groupby('month')['montant'].agg(['mean', 'std']).reset_index()
            
            # Analyser chaque mois
            for month in range(1, 13):
                month_data = df[df['month'] == month]['montant']
                
                if len(month_data) > 1:
                    pattern_info = monthly_patterns[monthly_patterns['month'] == month]
                    if not pattern_info.empty:
                        expected_mean = pattern_info.iloc[0]['mean']
                        expected_std = pattern_info.iloc[0]['std']
                        
                        # Détecter les déviations saisonnières
                        for value in month_data:
                            if expected_std > 0:
                                z_score = abs(value - expected_mean) / expected_std
                                
                                if z_score > self.severity_thresholds['seasonal_deviation']:
                                    severity = 'high' if z_score > 2.0 else 'medium'
                                    
                                    anomalies.append(TemporalAnomaly(
                                        type=TemporalAnomalyType.SEASONAL_DEVIATION,
                                        severity=severity,
                                        description=f"Déviation saisonnière en {month:02d}",
                                        period=f"Mois {month:02d}",
                                        expected_value=expected_mean,
                                        actual_value=value,
                                        confidence=min(z_score / 3.0, 1.0),
                                        recommendations=[
                                            "Vérifier si cette variation est justifiée par l'activité",
                                            "Comparer avec les années précédentes"
                                        ]
                                    ))
        
        except Exception as e:
            print(f"Erreur analyse saisonnalité: {e}")
        
        return anomalies
    
    def _detect_outliers(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Détecte les valeurs aberrantes"""
        anomalies = []
        
        if 'montant' not in df.columns or len(df) < 10:
            return anomalies
        
        try:
            amounts = df['montant'].values
            mean_amount = np.mean(amounts)
            std_amount = np.std(amounts)
            
            if std_amount == 0:
                return anomalies
            
            # Détecter les outliers avec Z-score
            z_scores = np.abs((amounts - mean_amount) / std_amount)
            
            for i, z_score in enumerate(z_scores):
                if z_score > self.severity_thresholds['outlier_zscore']:
                    severity = 'critical' if z_score > 3.0 else 'high' if z_score > 2.5 else 'medium'
                    
                    anomalies.append(TemporalAnomaly(
                        type=TemporalAnomalyType.OUTLIER,
                        severity=severity,
                        description=f"Valeur aberrante détectée: {amounts[i]:.2f}",
                        period=df.iloc[i]['date'].strftime('%Y-%m-%d'),
                        expected_value=mean_amount,
                        actual_value=amounts[i],
                        confidence=min(z_score / 3.0, 1.0),
                        recommendations=[
                            "Vérifier la saisie de cette écriture",
                            "Confirmer que le montant est correct",
                            "Vérifier les pièces justificatives"
                        ]
                    ))
        
        except Exception as e:
            print(f"Erreur détection outliers: {e}")
        
        return anomalies
    
    def _analyze_frequency(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Analyse la fréquence des écritures"""
        anomalies = []
        
        try:
            # Analyser les intervalles entre les écritures
            df_sorted = df.sort_values('date')
            date_diffs = df_sorted['date'].diff().dt.days.dropna()
            
            if len(date_diffs) > 5:
                mean_interval = date_diffs.mean()
                std_interval = date_diffs.std()
                
                # Détecter les intervalles anormaux
                for i, interval in enumerate(date_diffs):
                    if std_interval > 0:
                        z_score = abs(interval - mean_interval) / std_interval
                        
                        if z_score > 2.0 and interval > mean_interval * 2:
                            severity = 'medium' if interval < mean_interval * 5 else 'high'
                            
                            anomalies.append(TemporalAnomaly(
                                type=TemporalAnomalyType.INCONSISTENT_FREQUENCY,
                                severity=severity,
                                description=f"Intervalle anormal de {interval:.0f} jours entre écritures",
                                period=df_sorted.iloc[i+1]['date'].strftime('%Y-%m-%d'),
                                expected_value=mean_interval,
                                actual_value=interval,
                                confidence=min(z_score / 3.0, 1.0),
                                recommendations=[
                                    "Vérifier s'il manque des écritures dans cette période",
                                    "Contrôler la régularité de la saisie comptable"
                                ]
                            ))
        
        except Exception as e:
            print(f"Erreur analyse fréquence: {e}")
        
        return anomalies
    
    def _detect_gaps(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Détecte les périodes manquantes"""
        anomalies = []
        
        try:
            if len(df) < 2:
                return anomalies
            
            # Créer une série de dates complète
            start_date = df['date'].min()
            end_date = df['date'].max()
            
            # Analyser par semaine pour détecter les gaps
            df['week'] = df['date'].dt.to_period('W')
            weekly_counts = df.groupby('week').size()
            
            # Créer la série complète de semaines
            all_weeks = pd.period_range(start_date, end_date, freq='W')
            
            for week in all_weeks:
                if week not in weekly_counts.index:
                    # Période manquante détectée
                    anomalies.append(TemporalAnomaly(
                        type=TemporalAnomalyType.MISSING_PERIOD,
                        severity='medium',
                        description=f"Aucune écriture trouvée pour la semaine {week}",
                        period=str(week),
                        recommendations=[
                            "Vérifier s'il devrait y avoir des écritures cette semaine",
                            "Contrôler la complétude de la saisie comptable"
                        ]
                    ))
        
        except Exception as e:
            print(f"Erreur détection gaps: {e}")
        
        return anomalies
    
    def _analyze_retroactive_entries(self, df: pd.DataFrame, config: Dict) -> List[TemporalAnomaly]:
        """Analyse les écritures rétroactives"""
        anomalies = []
        
        try:
            # Supposer qu'il y a une colonne de date de saisie
            if 'date_saisie' in df.columns:
                df['date_saisie'] = pd.to_datetime(df['date_saisie'], errors='coerce')
                
                # Calculer l'écart entre date d'écriture et date de saisie
                df['ecart_jours'] = (df['date_saisie'] - df['date']).dt.days
                
                # Détecter les écritures rétroactives importantes
                retroactive_entries = df[df['ecart_jours'] > self.severity_thresholds['retroactive_days']]
                
                for _, entry in retroactive_entries.iterrows():
                    severity = 'high' if entry['ecart_jours'] > 90 else 'medium'
                    
                    anomalies.append(TemporalAnomaly(
                        type=TemporalAnomalyType.RETROACTIVE_ENTRY,
                        severity=severity,
                        description=f"Écriture rétroactive de {entry['ecart_jours']:.0f} jours",
                        period=entry['date'].strftime('%Y-%m-%d'),
                        actual_value=entry['ecart_jours'],
                        recommendations=[
                            "Vérifier la justification de cette écriture rétroactive",
                            "S'assurer que les impacts sur les périodes antérieures sont pris en compte"
                        ]
                    ))
            
            # Détecter les écritures futures
            today = datetime.now()
            future_entries = df[df['date'] > today]
            
            for _, entry in future_entries.iterrows():
                days_future = (entry['date'] - today).days
                severity = 'high' if days_future > 30 else 'medium'
                
                anomalies.append(TemporalAnomaly(
                    type=TemporalAnomalyType.FUTURE_ENTRY,
                    severity=severity,
                    description=f"Écriture datée dans le futur ({days_future} jours)",
                    period=entry['date'].strftime('%Y-%m-%d'),
                    actual_value=days_future,
                    recommendations=[
                        "Vérifier la date de cette écriture",
                        "Corriger si c'est une erreur de saisie"
                    ]
                ))
        
        except Exception as e:
            print(f"Erreur analyse écritures rétroactives: {e}")
        
        return anomalies
    
    def _calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calcule les tendances générales"""
        trends = {}
        
        try:
            if 'montant' in df.columns and len(df) > 1:
                # Tendance mensuelle
                df['year_month'] = df['date'].dt.to_period('M')
                monthly_data = df.groupby('year_month')['montant'].sum()
                
                if len(monthly_data) > 1:
                    x = np.arange(len(monthly_data))
                    y = monthly_data.values
                    slope, _ = np.polyfit(x, y, 1)
                    
                    trends['monthly_trend'] = {
                        'slope': float(slope),
                        'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                        'strength': abs(slope) / (np.mean(y) + 1e-10)
                    }
                
                # Volatilité
                if len(monthly_data) > 2:
                    volatility = np.std(monthly_data) / (np.mean(monthly_data) + 1e-10)
                    trends['volatility'] = {
                        'coefficient': float(volatility),
                        'level': 'high' if volatility > 0.5 else 'medium' if volatility > 0.2 else 'low'
                    }
        
        except Exception as e:
            print(f"Erreur calcul tendances: {e}")
        
        return trends
    
    def _calculate_seasonal_patterns(self, df: pd.DataFrame) -> Dict:
        """Calcule les patterns saisonniers"""
        patterns = {}
        
        try:
            if 'montant' in df.columns and len(df) > 12:
                # Pattern mensuel
                df['month'] = df['date'].dt.month
                monthly_avg = df.groupby('month')['montant'].mean()
                
                patterns['monthly_pattern'] = {
                    month: float(avg) for month, avg in monthly_avg.items()
                }
                
                # Identifier les mois les plus actifs
                max_month = monthly_avg.idxmax()
                min_month = monthly_avg.idxmin()
                
                patterns['peak_month'] = int(max_month)
                patterns['low_month'] = int(min_month)
                patterns['seasonality_ratio'] = float(monthly_avg.max() / (monthly_avg.min() + 1e-10))
        
        except Exception as e:
            print(f"Erreur calcul patterns saisonniers: {e}")
        
        return patterns
    
    def _generate_recommendations(self, anomalies: List[TemporalAnomaly], df: pd.DataFrame) -> List[str]:
        """Génère des recommandations basées sur les anomalies détectées"""
        recommendations = []
        
        # Compter les types d'anomalies
        anomaly_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.type.value
            anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
        
        # Recommandations spécifiques
        if anomaly_counts.get('outlier', 0) > 0:
            recommendations.append(
                f"Contrôler {anomaly_counts['outlier']} valeur(s) aberrante(s) détectée(s)"
            )
        
        if anomaly_counts.get('trend_break', 0) > 0:
            recommendations.append(
                "Analyser les ruptures de tendance pour identifier les causes"
            )
        
        if anomaly_counts.get('missing_period', 0) > 0:
            recommendations.append(
                "Vérifier la complétude des écritures comptables sur toute la période"
            )
        
        if anomaly_counts.get('retroactive_entry', 0) > 0:
            recommendations.append(
                "Documenter les justifications des écritures rétroactives importantes"
            )
        
        # Recommandations générales
        critical_count = sum(1 for a in anomalies if a.severity == 'critical')
        if critical_count > 0:
            recommendations.append(
                f"Traiter en priorité les {critical_count} anomalie(s) critique(s)"
            )
        
        if not recommendations:
            recommendations.append("Cohérence temporelle globalement satisfaisante")
        
        return recommendations
    
    def _anomaly_to_dict(self, anomaly: TemporalAnomaly) -> Dict:
        """Convertit une anomalie en dictionnaire"""
        return {
            'type': anomaly.type.value,
            'severity': anomaly.severity,
            'description': anomaly.description,
            'period': anomaly.period,
            'expected_value': anomaly.expected_value,
            'actual_value': anomaly.actual_value,
            'confidence': anomaly.confidence,
            'recommendations': anomaly.recommendations or [],
            'affected_accounts': anomaly.affected_accounts or []
        }
    
    def get_analysis_methods(self) -> List[str]:
        """Retourne la liste des méthodes d'analyse disponibles"""
        return list(self.analysis_methods.keys())
    
    def configure_thresholds(self, new_thresholds: Dict) -> None:
        """Configure les seuils de détection"""
        self.severity_thresholds.update(new_thresholds)

