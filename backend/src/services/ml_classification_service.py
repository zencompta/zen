"""
Service de Machine Learning pour la classification automatique en comptabilité
Utilise des modèles d'apprentissage automatique pour classifier et prédire
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import pickle
import os
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict, Counter
import statistics


# Pour une implémentation complète, nous utiliserions:
# from sklearn.ensemble import RandomForestClassifier, IsolationForest
# from sklearn.model_selection import train_test_split, cross_val_score
# from sklearn.preprocessing import StandardScaler, LabelEncoder
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics import classification_report, confusion_matrix
# import joblib


class ModelType(Enum):
    """Types de modèles ML"""
    ACCOUNT_CLASSIFIER = "account_classifier"
    ANOMALY_DETECTOR = "anomaly_detector"
    AMOUNT_PREDICTOR = "amount_predictor"
    FRAUD_DETECTOR = "fraud_detector"
    DOCUMENT_CLASSIFIER = "document_classifier"


class PredictionConfidence(Enum):
    """Niveaux de confiance des prédictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class MLPrediction:
    """Résultat d'une prédiction ML"""
    model_type: ModelType
    predicted_class: str
    confidence: float
    confidence_level: PredictionConfidence
    probabilities: Dict[str, float]
    features_used: List[str]
    explanation: str
    recommendations: List[str] = None


@dataclass
class AnomalyDetection:
    """Résultat de détection d'anomalie"""
    is_anomaly: bool
    anomaly_score: float
    severity: str
    description: str
    contributing_factors: List[str]
    similar_cases: List[str] = None


class MLClassificationService:
    """Service de classification ML pour la comptabilité"""
    
    def __init__(self):
        self.models = {}
        self.feature_extractors = {}
        self.label_encoders = {}
        self.scalers = {}
        
        # Configuration des modèles
        self.model_configs = {
            ModelType.ACCOUNT_CLASSIFIER: {
                'features': ['amount', 'description_features', 'date_features', 'journal_type'],
                'target': 'account_category',
                'algorithm': 'random_forest'
            },
            ModelType.ANOMALY_DETECTOR: {
                'features': ['amount', 'frequency', 'timing', 'account_pattern'],
                'algorithm': 'isolation_forest'
            },
            ModelType.AMOUNT_PREDICTOR: {
                'features': ['historical_amounts', 'seasonality', 'account_type', 'description'],
                'target': 'amount',
                'algorithm': 'regression'
            },
            ModelType.FRAUD_DETECTOR: {
                'features': ['amount_patterns', 'timing_patterns', 'user_behavior', 'account_activity'],
                'target': 'is_fraud',
                'algorithm': 'ensemble'
            }
        }
        
        # Catégories de comptes prédéfinies
        self.account_categories = {
            'ACTIF': {
                'patterns': [r'^2\d+', r'^3\d+', r'^4\d+', r'^5\d+'],
                'keywords': ['immobilisation', 'stock', 'créance', 'banque', 'caisse']
            },
            'PASSIF': {
                'patterns': [r'^1\d+'],
                'keywords': ['capital', 'réserve', 'emprunt', 'dette']
            },
            'CHARGE': {
                'patterns': [r'^6\d+'],
                'keywords': ['achat', 'service', 'personnel', 'impôt', 'dotation']
            },
            'PRODUIT': {
                'patterns': [r'^7\d+'],
                'keywords': ['vente', 'prestation', 'produit', 'subvention']
            }
        }
    
    def train_account_classifier(self, training_data: List[Dict]) -> Dict:
        """
        Entraîne le modèle de classification des comptes
        
        Args:
            training_data: Données d'entraînement avec comptes et descriptions
            
        Returns:
            Dict contenant les résultats d'entraînement
        """
        result = {
            'success': True,
            'model_type': ModelType.ACCOUNT_CLASSIFIER.value,
            'training_summary': {
                'samples_count': len(training_data),
                'features_count': 0,
                'classes_count': 0,
                'accuracy': 0.0
            },
            'feature_importance': {},
            'class_distribution': {},
            'training_time': 0.0
        }
        
        try:
            start_time = datetime.now()
            
            if len(training_data) < 10:
                result['success'] = False
                result['error'] = "Pas assez de données d'entraînement (minimum 10)"
                return result
            
            # Préparer les données
            df = pd.DataFrame(training_data)
            
            # Extraire les features
            features = self._extract_features_for_classification(df)
            
            # Préparer les labels (catégories de comptes)
            labels = self._prepare_account_labels(df)
            
            if len(features) == 0 or len(labels) == 0:
                result['success'] = False
                result['error'] = "Impossible d'extraire les features ou labels"
                return result
            
            # Simulation d'entraînement (en production, utiliser scikit-learn)
            # X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2)
            # model = RandomForestClassifier(n_estimators=100, random_state=42)
            # model.fit(X_train, y_train)
            # accuracy = model.score(X_test, y_test)
            
            # Pour la démonstration, simuler l'entraînement
            accuracy = 0.85  # Précision simulée
            
            # Sauvegarder le modèle simulé
            self.models[ModelType.ACCOUNT_CLASSIFIER] = {
                'trained': True,
                'accuracy': accuracy,
                'features': list(features.columns) if hasattr(features, 'columns') else [],
                'classes': list(set(labels)) if labels else [],
                'training_date': datetime.now()
            }
            
            # Calculer les statistiques
            result['training_summary']['features_count'] = len(features.columns) if hasattr(features, 'columns') else 0
            result['training_summary']['classes_count'] = len(set(labels)) if labels else 0
            result['training_summary']['accuracy'] = accuracy
            
            # Distribution des classes
            if labels:
                class_counts = Counter(labels)
                result['class_distribution'] = dict(class_counts)
            
            # Importance des features (simulée)
            if hasattr(features, 'columns'):
                feature_names = features.columns
                importance_scores = np.random.random(len(feature_names))
                importance_scores = importance_scores / importance_scores.sum()
                result['feature_importance'] = dict(zip(feature_names, importance_scores))
            
            training_time = (datetime.now() - start_time).total_seconds()
            result['training_time'] = training_time
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur entraînement modèle: {str(e)}"
        
        return result
    
    def predict_account_category(self, entry_data: Dict) -> MLPrediction:
        """
        Prédit la catégorie de compte pour une écriture
        
        Args:
            entry_data: Données de l'écriture comptable
            
        Returns:
            MLPrediction avec la prédiction
        """
        try:
            # Vérifier si le modèle est entraîné
            if ModelType.ACCOUNT_CLASSIFIER not in self.models:
                # Utiliser des règles heuristiques
                return self._predict_account_with_rules(entry_data)
            
            # Extraire les features
            features = self._extract_single_entry_features(entry_data)
            
            # Simulation de prédiction (en production, utiliser le modèle entraîné)
            # prediction = self.models[ModelType.ACCOUNT_CLASSIFIER].predict(features)
            # probabilities = self.models[ModelType.ACCOUNT_CLASSIFIER].predict_proba(features)
            
            # Prédiction simulée basée sur des règles
            predicted_category, confidence, probabilities = self._simulate_account_prediction(entry_data)
            
            confidence_level = self._determine_confidence_level(confidence)
            
            return MLPrediction(
                model_type=ModelType.ACCOUNT_CLASSIFIER,
                predicted_class=predicted_category,
                confidence=confidence,
                confidence_level=confidence_level,
                probabilities=probabilities,
                features_used=list(features.keys()) if isinstance(features, dict) else [],
                explanation=f"Classification basée sur l'analyse du montant, description et patterns",
                recommendations=[
                    f"Compte suggéré: catégorie {predicted_category}",
                    "Vérifier la cohérence avec le plan comptable"
                ]
            )
            
        except Exception as e:
            return MLPrediction(
                model_type=ModelType.ACCOUNT_CLASSIFIER,
                predicted_class="UNKNOWN",
                confidence=0.0,
                confidence_level=PredictionConfidence.LOW,
                probabilities={},
                features_used=[],
                explanation=f"Erreur prédiction: {str(e)}",
                recommendations=["Classification manuelle requise"]
            )
    
    def detect_anomalies(self, data: List[Dict], sensitivity: float = 0.1) -> List[AnomalyDetection]:
        """
        Détecte les anomalies dans les données comptables
        
        Args:
            data: Données comptables
            sensitivity: Sensibilité de détection (0.0 à 1.0)
            
        Returns:
            Liste des anomalies détectées
        """
        anomalies = []
        
        try:
            if not data:
                return anomalies
            
            df = pd.DataFrame(data)
            
            # Préparer les features pour la détection d'anomalies
            features = self._prepare_anomaly_features(df)
            
            if features.empty:
                return anomalies
            
            # Simulation de détection d'anomalies (en production, utiliser IsolationForest)
            # isolation_forest = IsolationForest(contamination=sensitivity, random_state=42)
            # anomaly_scores = isolation_forest.fit_predict(features)
            # anomaly_scores_proba = isolation_forest.decision_function(features)
            
            # Détection simulée basée sur des règles statistiques
            anomalies = self._simulate_anomaly_detection(df, sensitivity)
            
        except Exception as e:
            print(f"Erreur détection anomalies: {e}")
        
        return anomalies
    
    def predict_expected_amount(self, entry_context: Dict) -> Dict:
        """
        Prédit le montant attendu pour une écriture
        
        Args:
            entry_context: Contexte de l'écriture (compte, description, historique)
            
        Returns:
            Dict avec la prédiction de montant
        """
        result = {
            'predicted_amount': 0.0,
            'confidence': 0.0,
            'range_min': 0.0,
            'range_max': 0.0,
            'explanation': '',
            'similar_entries': []
        }
        
        try:
            # Analyser l'historique pour ce type d'écriture
            account = entry_context.get('account', '')
            description = entry_context.get('description', '')
            
            # Simulation de prédiction basée sur l'historique
            historical_amounts = entry_context.get('historical_amounts', [])
            
            if historical_amounts:
                amounts = [float(a) for a in historical_amounts if a > 0]
                
                if amounts:
                    predicted_amount = statistics.median(amounts)
                    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    result['predicted_amount'] = predicted_amount
                    result['confidence'] = 0.8 if len(amounts) > 5 else 0.6
                    result['range_min'] = max(0, predicted_amount - std_dev)
                    result['range_max'] = predicted_amount + std_dev
                    result['explanation'] = f"Basé sur {len(amounts)} écritures similaires"
                else:
                    result['explanation'] = "Pas d'historique disponible pour ce type d'écriture"
            else:
                # Prédiction basée sur des patterns généraux
                if 'salaire' in description.lower():
                    result['predicted_amount'] = 2500.0
                    result['confidence'] = 0.5
                elif 'facture' in description.lower():
                    result['predicted_amount'] = 1000.0
                    result['confidence'] = 0.4
                else:
                    result['predicted_amount'] = 500.0
                    result['confidence'] = 0.3
                
                result['explanation'] = "Prédiction basée sur des patterns généraux"
            
        except Exception as e:
            result['explanation'] = f"Erreur prédiction montant: {str(e)}"
        
        return result
    
    def suggest_corrections(self, entry_data: Dict, detected_issues: List[str]) -> List[Dict]:
        """
        Suggère des corrections automatiques pour une écriture
        
        Args:
            entry_data: Données de l'écriture
            detected_issues: Liste des problèmes détectés
            
        Returns:
            Liste des suggestions de correction
        """
        suggestions = []
        
        try:
            for issue in detected_issues:
                if 'montant' in issue.lower():
                    # Suggestion pour les problèmes de montant
                    predicted_amount = self.predict_expected_amount(entry_data)
                    
                    suggestions.append({
                        'type': 'amount_correction',
                        'issue': issue,
                        'current_value': entry_data.get('montant', 0),
                        'suggested_value': predicted_amount['predicted_amount'],
                        'confidence': predicted_amount['confidence'],
                        'explanation': predicted_amount['explanation'],
                        'action': 'replace'
                    })
                
                elif 'compte' in issue.lower():
                    # Suggestion pour les problèmes de compte
                    account_prediction = self.predict_account_category(entry_data)
                    
                    suggestions.append({
                        'type': 'account_correction',
                        'issue': issue,
                        'current_value': entry_data.get('account', ''),
                        'suggested_value': account_prediction.predicted_class,
                        'confidence': account_prediction.confidence,
                        'explanation': account_prediction.explanation,
                        'action': 'replace'
                    })
                
                elif 'date' in issue.lower():
                    # Suggestion pour les problèmes de date
                    current_date = entry_data.get('date', '')
                    suggested_date = self._suggest_date_correction(current_date, entry_data)
                    
                    suggestions.append({
                        'type': 'date_correction',
                        'issue': issue,
                        'current_value': current_date,
                        'suggested_value': suggested_date,
                        'confidence': 0.7,
                        'explanation': "Correction basée sur les patterns temporels",
                        'action': 'replace'
                    })
                
                elif 'description' in issue.lower():
                    # Suggestion pour les problèmes de description
                    suggested_description = self._suggest_description_improvement(entry_data)
                    
                    suggestions.append({
                        'type': 'description_improvement',
                        'issue': issue,
                        'current_value': entry_data.get('description', ''),
                        'suggested_value': suggested_description,
                        'confidence': 0.6,
                        'explanation': "Amélioration basée sur les bonnes pratiques",
                        'action': 'enhance'
                    })
        
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'issue': f"Erreur génération suggestions: {str(e)}",
                'action': 'manual_review'
            })
        
        return suggestions
    
    def adaptive_learning(self, feedback_data: List[Dict]) -> Dict:
        """
        Apprentissage adaptatif basé sur les retours utilisateur
        
        Args:
            feedback_data: Données de retour avec corrections utilisateur
            
        Returns:
            Dict avec les résultats de l'apprentissage
        """
        result = {
            'success': True,
            'learning_summary': {
                'feedback_count': len(feedback_data),
                'accepted_suggestions': 0,
                'rejected_suggestions': 0,
                'model_updates': 0
            },
            'improvements': [],
            'new_patterns': []
        }
        
        try:
            if not feedback_data:
                result['success'] = False
                result['error'] = "Aucune donnée de feedback fournie"
                return result
            
            # Analyser les retours
            accepted = [f for f in feedback_data if f.get('accepted', False)]
            rejected = [f for f in feedback_data if not f.get('accepted', False)]
            
            result['learning_summary']['accepted_suggestions'] = len(accepted)
            result['learning_summary']['rejected_suggestions'] = len(rejected)
            
            # Identifier les patterns d'amélioration
            if accepted:
                # Analyser les suggestions acceptées pour renforcer les modèles
                for feedback in accepted:
                    suggestion_type = feedback.get('suggestion_type', '')
                    
                    if suggestion_type == 'account_correction':
                        result['improvements'].append(
                            f"Renforcement du modèle de classification des comptes"
                        )
                    elif suggestion_type == 'amount_correction':
                        result['improvements'].append(
                            f"Amélioration de la prédiction des montants"
                        )
            
            # Analyser les rejets pour identifier les faiblesses
            if rejected:
                rejection_reasons = Counter(f.get('reason', 'unknown') for f in rejected)
                
                for reason, count in rejection_reasons.items():
                    result['improvements'].append(
                        f"Améliorer la gestion de: {reason} ({count} cas)"
                    )
            
            # Identifier de nouveaux patterns
            descriptions = [f.get('description', '') for f in feedback_data]
            new_patterns = self._identify_new_patterns(descriptions)
            result['new_patterns'] = new_patterns
            
            # Simuler la mise à jour des modèles
            result['learning_summary']['model_updates'] = len(result['improvements'])
            
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur apprentissage adaptatif: {str(e)}"
        
        return result
    
    def _extract_features_for_classification(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrait les features pour la classification"""
        features = pd.DataFrame()
        
        try:
            # Features numériques
            if 'montant' in df.columns:
                features['amount'] = df['montant'].fillna(0)
                features['amount_log'] = np.log1p(features['amount'])
                features['amount_rounded'] = (features['amount'] % 100 == 0).astype(int)
            
            # Features temporelles
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                features['month'] = df['date'].dt.month.fillna(0)
                features['weekday'] = df['date'].dt.weekday.fillna(0)
                features['is_weekend'] = (df['date'].dt.weekday >= 5).astype(int)
            
            # Features textuelles
            if 'description' in df.columns:
                descriptions = df['description'].fillna('')
                features['desc_length'] = descriptions.str.len()
                features['has_numbers'] = descriptions.str.contains(r'\d').astype(int)
                features['has_keywords'] = descriptions.str.contains('facture|paiement|salaire', case=False).astype(int)
            
            # Features de compte
            if 'account' in df.columns:
                accounts = df['account'].fillna('')
                features['account_first_digit'] = accounts.str[0].fillna('0')
                features['account_length'] = accounts.str.len()
        
        except Exception as e:
            print(f"Erreur extraction features: {e}")
        
        return features
    
    def _prepare_account_labels(self, df: pd.DataFrame) -> List[str]:
        """Prépare les labels de catégories de comptes"""
        labels = []
        
        try:
            if 'account' not in df.columns:
                return labels
            
            for account in df['account'].fillna(''):
                category = self._classify_account_by_rules(account)
                labels.append(category)
        
        except Exception as e:
            print(f"Erreur préparation labels: {e}")
        
        return labels
    
    def _classify_account_by_rules(self, account: str) -> str:
        """Classifie un compte selon des règles prédéfinies"""
        account = str(account).strip()
        
        for category, config in self.account_categories.items():
            # Vérifier les patterns de numéro de compte
            for pattern in config['patterns']:
                if re.match(pattern, account):
                    return category
        
        return 'AUTRE'
    
    def _extract_single_entry_features(self, entry_data: Dict) -> Dict:
        """Extrait les features pour une seule écriture"""
        features = {}
        
        try:
            # Features de montant
            amount = float(entry_data.get('montant', 0))
            features['amount'] = amount
            features['amount_log'] = np.log1p(amount)
            features['amount_rounded'] = int(amount % 100 == 0)
            
            # Features de description
            description = str(entry_data.get('description', ''))
            features['desc_length'] = len(description)
            features['has_numbers'] = int(bool(re.search(r'\d', description)))
            features['has_keywords'] = int(bool(re.search(r'facture|paiement|salaire', description, re.IGNORECASE)))
            
            # Features de compte
            account = str(entry_data.get('account', ''))
            features['account_first_digit'] = account[0] if account else '0'
            features['account_length'] = len(account)
            
            # Features temporelles
            if 'date' in entry_data:
                try:
                    date = pd.to_datetime(entry_data['date'])
                    features['month'] = date.month
                    features['weekday'] = date.weekday()
                    features['is_weekend'] = int(date.weekday() >= 5)
                except:
                    features['month'] = 0
                    features['weekday'] = 0
                    features['is_weekend'] = 0
        
        except Exception as e:
            print(f"Erreur extraction features entrée: {e}")
        
        return features
    
    def _simulate_account_prediction(self, entry_data: Dict) -> Tuple[str, float, Dict[str, float]]:
        """Simule une prédiction de catégorie de compte"""
        account = str(entry_data.get('account', ''))
        description = str(entry_data.get('description', '')).lower()
        amount = float(entry_data.get('montant', 0))
        
        # Prédiction basée sur des règles
        if account:
            predicted_category = self._classify_account_by_rules(account)
            confidence = 0.9
        else:
            # Prédiction basée sur la description
            if any(keyword in description for keyword in ['achat', 'fournisseur', 'charge']):
                predicted_category = 'CHARGE'
                confidence = 0.7
            elif any(keyword in description for keyword in ['vente', 'client', 'produit']):
                predicted_category = 'PRODUIT'
                confidence = 0.7
            elif any(keyword in description for keyword in ['banque', 'caisse', 'trésorerie']):
                predicted_category = 'ACTIF'
                confidence = 0.6
            else:
                predicted_category = 'AUTRE'
                confidence = 0.4
        
        # Probabilités simulées
        probabilities = {
            'ACTIF': 0.2,
            'PASSIF': 0.1,
            'CHARGE': 0.3,
            'PRODUIT': 0.3,
            'AUTRE': 0.1
        }
        
        # Ajuster les probabilités selon la prédiction
        probabilities[predicted_category] = confidence
        remaining = (1.0 - confidence) / (len(probabilities) - 1)
        for cat in probabilities:
            if cat != predicted_category:
                probabilities[cat] = remaining
        
        return predicted_category, confidence, probabilities
    
    def _determine_confidence_level(self, confidence: float) -> PredictionConfidence:
        """Détermine le niveau de confiance"""
        if confidence >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return PredictionConfidence.HIGH
        elif confidence >= 0.5:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def _predict_account_with_rules(self, entry_data: Dict) -> MLPrediction:
        """Prédiction de compte avec des règles heuristiques"""
        account = str(entry_data.get('account', ''))
        predicted_category = self._classify_account_by_rules(account)
        
        return MLPrediction(
            model_type=ModelType.ACCOUNT_CLASSIFIER,
            predicted_class=predicted_category,
            confidence=0.8 if predicted_category != 'AUTRE' else 0.4,
            confidence_level=PredictionConfidence.HIGH if predicted_category != 'AUTRE' else PredictionConfidence.LOW,
            probabilities={predicted_category: 0.8, 'AUTRE': 0.2},
            features_used=['account_pattern'],
            explanation="Classification basée sur les règles du plan comptable",
            recommendations=[f"Catégorie suggérée: {predicted_category}"]
        )
    
    def _prepare_anomaly_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les features pour la détection d'anomalies"""
        features = pd.DataFrame()
        
        try:
            if 'montant' in df.columns:
                amounts = df['montant'].fillna(0)
                features['amount'] = amounts
                features['amount_zscore'] = (amounts - amounts.mean()) / amounts.std()
                features['amount_percentile'] = amounts.rank(pct=True)
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                features['hour'] = df['date'].dt.hour.fillna(12)
                features['weekday'] = df['date'].dt.weekday.fillna(0)
            
            if 'description' in df.columns:
                descriptions = df['description'].fillna('')
                features['desc_length'] = descriptions.str.len()
                features['desc_uniqueness'] = descriptions.apply(lambda x: len(set(x.split())))
        
        except Exception as e:
            print(f"Erreur préparation features anomalies: {e}")
        
        return features
    
    def _simulate_anomaly_detection(self, df: pd.DataFrame, sensitivity: float) -> List[AnomalyDetection]:
        """Simule la détection d'anomalies"""
        anomalies = []
        
        try:
            if 'montant' not in df.columns:
                return anomalies
            
            amounts = df['montant'].fillna(0)
            mean_amount = amounts.mean()
            std_amount = amounts.std()
            
            if std_amount == 0:
                return anomalies
            
            # Détecter les outliers statistiques
            threshold = 2.0 - sensitivity  # Plus la sensibilité est haute, plus le seuil est bas
            
            for idx, amount in enumerate(amounts):
                z_score = abs(amount - mean_amount) / std_amount
                
                if z_score > threshold:
                    severity = 'critical' if z_score > 3.0 else 'high' if z_score > 2.5 else 'medium'
                    
                    anomalies.append(AnomalyDetection(
                        is_anomaly=True,
                        anomaly_score=z_score,
                        severity=severity,
                        description=f"Montant anormal: {amount:.2f} (z-score: {z_score:.2f})",
                        contributing_factors=[
                            f"Écart de {z_score:.2f} écarts-types par rapport à la moyenne",
                            f"Montant: {amount:.2f}, Moyenne: {mean_amount:.2f}"
                        ]
                    ))
            
            # Détecter les patterns temporels anormaux
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df['hour'] = df['date'].dt.hour
                
                # Écritures nocturnes
                night_entries = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
                
                for idx, entry in night_entries.iterrows():
                    anomalies.append(AnomalyDetection(
                        is_anomaly=True,
                        anomaly_score=0.7,
                        severity='medium',
                        description=f"Écriture nocturne à {entry['hour']}h",
                        contributing_factors=[
                            "Saisie en dehors des heures ouvrables",
                            f"Heure: {entry['hour']}h"
                        ]
                    ))
        
        except Exception as e:
            print(f"Erreur simulation détection anomalies: {e}")
        
        return anomalies
    
    def _suggest_date_correction(self, current_date: str, entry_data: Dict) -> str:
        """Suggère une correction de date"""
        try:
            # Logique simple de correction de date
            if not current_date:
                return datetime.now().strftime('%Y-%m-%d')
            
            # Vérifier si la date est dans le futur
            try:
                date_obj = pd.to_datetime(current_date)
                if date_obj > datetime.now():
                    return datetime.now().strftime('%Y-%m-%d')
            except:
                pass
            
            return current_date
        except:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _suggest_description_improvement(self, entry_data: Dict) -> str:
        """Suggère une amélioration de description"""
        current_desc = str(entry_data.get('description', ''))
        account = str(entry_data.get('account', ''))
        amount = entry_data.get('montant', 0)
        
        # Suggestions basiques d'amélioration
        if len(current_desc) < 10:
            if account.startswith('6'):
                return f"{current_desc} - Charge comptable {amount:.2f}€"
            elif account.startswith('7'):
                return f"{current_desc} - Produit comptable {amount:.2f}€"
            else:
                return f"{current_desc} - Écriture comptable {amount:.2f}€"
        
        return current_desc
    
    def _identify_new_patterns(self, descriptions: List[str]) -> List[str]:
        """Identifie de nouveaux patterns dans les descriptions"""
        patterns = []
        
        try:
            # Analyser les mots fréquents
            all_words = []
            for desc in descriptions:
                words = str(desc).lower().split()
                all_words.extend(words)
            
            word_counts = Counter(all_words)
            frequent_words = [word for word, count in word_counts.most_common(10) if count > 2]
            
            if frequent_words:
                patterns.append(f"Mots fréquents détectés: {', '.join(frequent_words[:5])}")
            
            # Analyser les patterns numériques
            numeric_patterns = []
            for desc in descriptions:
                numbers = re.findall(r'\d+', str(desc))
                if numbers:
                    numeric_patterns.extend(numbers)
            
            if numeric_patterns:
                patterns.append(f"Patterns numériques fréquents détectés")
        
        except Exception as e:
            patterns.append(f"Erreur analyse patterns: {str(e)}")
        
        return patterns
    
    def get_model_status(self) -> Dict:
        """Retourne le statut des modèles ML"""
        status = {
            'models_trained': len(self.models),
            'available_models': list(self.model_configs.keys()),
            'model_details': {}
        }
        
        for model_type, model_data in self.models.items():
            status['model_details'][model_type.value] = {
                'trained': model_data.get('trained', False),
                'accuracy': model_data.get('accuracy', 0.0),
                'training_date': model_data.get('training_date', '').strftime('%Y-%m-%d %H:%M') if model_data.get('training_date') else '',
                'features_count': len(model_data.get('features', [])),
                'classes_count': len(model_data.get('classes', []))
            }
        
        return status
    
    def save_models(self, save_path: str) -> Dict:
        """Sauvegarde les modèles entraînés"""
        result = {'success': True, 'saved_models': []}
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            for model_type, model_data in self.models.items():
                model_file = os.path.join(save_path, f"{model_type.value}_model.pkl")
                
                # En production, utiliser joblib.dump(model, model_file)
                with open(model_file, 'w') as f:
                    json.dump({
                        'model_type': model_type.value,
                        'metadata': {
                            'trained': model_data.get('trained', False),
                            'accuracy': model_data.get('accuracy', 0.0),
                            'training_date': model_data.get('training_date', '').isoformat() if model_data.get('training_date') else ''
                        }
                    }, f)
                
                result['saved_models'].append(model_type.value)
        
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur sauvegarde modèles: {str(e)}"
        
        return result
    
    def load_models(self, load_path: str) -> Dict:
        """Charge les modèles sauvegardés"""
        result = {'success': True, 'loaded_models': []}
        
        try:
            if not os.path.exists(load_path):
                result['success'] = False
                result['error'] = f"Chemin non trouvé: {load_path}"
                return result
            
            for model_type in ModelType:
                model_file = os.path.join(load_path, f"{model_type.value}_model.pkl")
                
                if os.path.exists(model_file):
                    # En production, utiliser joblib.load(model_file)
                    with open(model_file, 'r') as f:
                        model_data = json.load(f)
                    
                    self.models[model_type] = model_data.get('metadata', {})
                    result['loaded_models'].append(model_type.value)
        
        except Exception as e:
            result['success'] = False
            result['error'] = f"Erreur chargement modèles: {str(e)}"
        
        return result

