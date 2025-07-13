"""
Service de contenu intelligent
Génère automatiquement des commentaires, recommandations contextuelles, 
comparaisons sectorielles et benchmarking automatique
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import statistics
from collections import defaultdict
import re

@dataclass
class SectorBenchmark:
    """Données de benchmark sectoriel"""
    sector: str
    metrics: Dict[str, float]
    percentiles: Dict[str, Dict[str, float]]  # P25, P50, P75, P90
    sample_size: int
    last_updated: str

@dataclass
class ContextualRecommendation:
    """Recommandation contextuelle"""
    category: str
    priority: str  # high, medium, low
    title: str
    description: str
    impact: str
    implementation_effort: str
    timeline: str
    related_metrics: List[str]

class IntelligentContentService:
    """Service de génération de contenu intelligent"""
    
    def __init__(self):
        self.sector_benchmarks = {}
        self.recommendation_templates = {}
        self.commentary_patterns = {}
        self._initialize_benchmark_data()
        self._initialize_recommendation_templates()
        self._initialize_commentary_patterns()
    
    def _initialize_benchmark_data(self):
        """Initialise les données de benchmark par secteur"""
        # Données de benchmark simulées (en production, ces données viendraient d'une base de données)
        self.sector_benchmarks = {
            "banking": SectorBenchmark(
                sector="banking",
                metrics={
                    "roe": 12.5,  # Return on Equity
                    "roa": 1.2,   # Return on Assets
                    "cost_income_ratio": 65.0,
                    "tier1_capital_ratio": 14.5,
                    "npl_ratio": 3.2,  # Non-performing loans
                    "net_interest_margin": 2.8
                },
                percentiles={
                    "roe": {"p25": 8.0, "p50": 12.5, "p75": 16.0, "p90": 20.0},
                    "roa": {"p25": 0.8, "p50": 1.2, "p75": 1.6, "p90": 2.0},
                    "cost_income_ratio": {"p25": 55.0, "p50": 65.0, "p75": 75.0, "p90": 85.0},
                    "tier1_capital_ratio": {"p25": 12.0, "p50": 14.5, "p75": 17.0, "p90": 20.0}
                },
                sample_size=150,
                last_updated="2024-12-01"
            ),
            "retail": SectorBenchmark(
                sector="retail",
                metrics={
                    "gross_margin": 35.0,
                    "inventory_turnover": 6.5,
                    "current_ratio": 1.8,
                    "debt_to_equity": 0.6,
                    "sales_growth": 8.5,
                    "ebitda_margin": 12.0
                },
                percentiles={
                    "gross_margin": {"p25": 25.0, "p50": 35.0, "p75": 45.0, "p90": 55.0},
                    "inventory_turnover": {"p25": 4.0, "p50": 6.5, "p75": 9.0, "p90": 12.0},
                    "current_ratio": {"p25": 1.2, "p50": 1.8, "p75": 2.5, "p90": 3.2}
                },
                sample_size=200,
                last_updated="2024-12-01"
            ),
            "manufacturing": SectorBenchmark(
                sector="manufacturing",
                metrics={
                    "asset_turnover": 1.4,
                    "working_capital_ratio": 15.0,
                    "capacity_utilization": 78.0,
                    "quality_score": 95.5,
                    "safety_incidents": 2.1,
                    "energy_efficiency": 85.0
                },
                percentiles={
                    "asset_turnover": {"p25": 1.0, "p50": 1.4, "p75": 1.8, "p90": 2.2},
                    "capacity_utilization": {"p25": 65.0, "p50": 78.0, "p75": 88.0, "p90": 95.0}
                },
                sample_size=120,
                last_updated="2024-12-01"
            )
        }
    
    def _initialize_recommendation_templates(self):
        """Initialise les templates de recommandations"""
        self.recommendation_templates = {
            "financial_performance": {
                "low_profitability": {
                    "title": "Amélioration de la rentabilité",
                    "description": "Les indicateurs de rentabilité sont en dessous des standards sectoriels",
                    "recommendations": [
                        "Analyser la structure des coûts pour identifier les opportunités d'optimisation",
                        "Revoir la stratégie de pricing pour améliorer les marges",
                        "Évaluer les investissements non-productifs",
                        "Mettre en place un suivi mensuel des indicateurs de performance"
                    ]
                },
                "high_leverage": {
                    "title": "Gestion de l'endettement",
                    "description": "Le niveau d'endettement nécessite une attention particulière",
                    "recommendations": [
                        "Élaborer un plan de désendettement progressif",
                        "Négocier les conditions de financement avec les créanciers",
                        "Prioriser la génération de cash-flow libre",
                        "Évaluer les opportunités de refinancement"
                    ]
                }
            },
            "operational_efficiency": {
                "inventory_management": {
                    "title": "Optimisation de la gestion des stocks",
                    "description": "Les ratios de rotation des stocks peuvent être améliorés",
                    "recommendations": [
                        "Implémenter un système de gestion des stocks en temps réel",
                        "Optimiser les niveaux de stock de sécurité",
                        "Améliorer la prévision de la demande",
                        "Négocier des délais de livraison plus courts avec les fournisseurs"
                    ]
                }
            },
            "risk_management": {
                "concentration_risk": {
                    "title": "Diversification des risques",
                    "description": "Concentration excessive identifiée dans certains domaines",
                    "recommendations": [
                        "Diversifier le portefeuille clients/fournisseurs",
                        "Développer de nouveaux marchés géographiques",
                        "Mettre en place des limites de concentration",
                        "Renforcer le suivi des risques de contrepartie"
                    ]
                }
            }
        }
    
    def _initialize_commentary_patterns(self):
        """Initialise les patterns de génération de commentaires"""
        self.commentary_patterns = {
            "trend_analysis": {
                "positive": [
                    "L'évolution positive de {metric} ({value}%) témoigne d'une amélioration {period}",
                    "La progression de {metric} de {value}% sur {period} est encourageante",
                    "L'indicateur {metric} affiche une croissance soutenue de {value}% {period}"
                ],
                "negative": [
                    "La baisse de {metric} ({value}%) sur {period} nécessite une attention particulière",
                    "Le recul de {metric} de {value}% {period} soulève des questions",
                    "La détérioration de {metric} ({value}%) {period} est préoccupante"
                ],
                "stable": [
                    "L'indicateur {metric} reste stable à {value}% {period}",
                    "La stabilité de {metric} ({value}%) {period} témoigne d'une situation maîtrisée"
                ]
            },
            "benchmark_comparison": {
                "above_median": [
                    "{metric} ({value}) se situe au-dessus de la médiane sectorielle ({benchmark})",
                    "Avec {value}, {metric} surperforme la médiane du secteur ({benchmark})",
                    "L'indicateur {metric} ({value}) dépasse favorablement le benchmark sectoriel ({benchmark})"
                ],
                "below_median": [
                    "{metric} ({value}) se situe en dessous de la médiane sectorielle ({benchmark})",
                    "Avec {value}, {metric} sous-performe par rapport au secteur ({benchmark})",
                    "L'indicateur {metric} ({value}) est inférieur au benchmark sectoriel ({benchmark})"
                ]
            }
        }
    
    def generate_automatic_commentary(self, 
                                    financial_data: Dict[str, Any], 
                                    sector: str,
                                    period: str = "sur l'exercice") -> Dict[str, str]:
        """Génère automatiquement des commentaires sur les données financières"""
        
        commentary = {}
        
        # Analyse des tendances
        if 'trends' in financial_data:
            commentary['trend_analysis'] = self._generate_trend_commentary(
                financial_data['trends'], period
            )
        
        # Comparaison sectorielle
        if sector in self.sector_benchmarks:
            commentary['sector_comparison'] = self._generate_benchmark_commentary(
                financial_data, sector
            )
        
        # Analyse des ratios clés
        if 'ratios' in financial_data:
            commentary['ratio_analysis'] = self._generate_ratio_commentary(
                financial_data['ratios']
            )
        
        # Points d'attention
        commentary['key_points'] = self._identify_key_points(financial_data, sector)
        
        return commentary
    
    def _generate_trend_commentary(self, trends: Dict[str, float], period: str) -> str:
        """Génère des commentaires sur les tendances"""
        comments = []
        
        for metric, change in trends.items():
            if abs(change) < 2:  # Variation faible
                pattern_type = "stable"
                template = np.random.choice(self.commentary_patterns["trend_analysis"]["stable"])
            elif change > 0:  # Tendance positive
                pattern_type = "positive"
                template = np.random.choice(self.commentary_patterns["trend_analysis"]["positive"])
            else:  # Tendance négative
                pattern_type = "negative"
                template = np.random.choice(self.commentary_patterns["trend_analysis"]["negative"])
            
            comment = template.format(
                metric=metric.replace('_', ' ').title(),
                value=abs(round(change, 1)),
                period=period
            )
            comments.append(comment)
        
        return ". ".join(comments) + "."
    
    def _generate_benchmark_commentary(self, data: Dict[str, Any], sector: str) -> str:
        """Génère des commentaires de comparaison sectorielle"""
        if sector not in self.sector_benchmarks:
            return "Données de benchmark non disponibles pour ce secteur."
        
        benchmark = self.sector_benchmarks[sector]
        comments = []
        
        # Comparer les métriques disponibles
        for metric, value in data.get('current_metrics', {}).items():
            if metric in benchmark.metrics:
                sector_median = benchmark.metrics[metric]
                
                if value > sector_median:
                    template = np.random.choice(self.commentary_patterns["benchmark_comparison"]["above_median"])
                else:
                    template = np.random.choice(self.commentary_patterns["benchmark_comparison"]["below_median"])
                
                comment = template.format(
                    metric=metric.replace('_', ' ').title(),
                    value=round(value, 1),
                    benchmark=round(sector_median, 1)
                )
                comments.append(comment)
        
        return ". ".join(comments) + "."
    
    def _generate_ratio_commentary(self, ratios: Dict[str, float]) -> str:
        """Génère des commentaires sur les ratios financiers"""
        comments = []
        
        # Analyse des ratios de liquidité
        if 'current_ratio' in ratios:
            current_ratio = ratios['current_ratio']
            if current_ratio < 1.0:
                comments.append(f"Le ratio de liquidité générale ({current_ratio:.2f}) indique des difficultés potentielles de trésorerie")
            elif current_ratio > 2.5:
                comments.append(f"Le ratio de liquidité générale ({current_ratio:.2f}) suggère une gestion conservative de la trésorerie")
            else:
                comments.append(f"Le ratio de liquidité générale ({current_ratio:.2f}) est dans une fourchette acceptable")
        
        # Analyse des ratios de rentabilité
        if 'roe' in ratios:
            roe = ratios['roe']
            if roe < 5:
                comments.append(f"La rentabilité des capitaux propres ({roe:.1f}%) est faible")
            elif roe > 20:
                comments.append(f"La rentabilité des capitaux propres ({roe:.1f}%) est excellente")
            else:
                comments.append(f"La rentabilité des capitaux propres ({roe:.1f}%) est satisfaisante")
        
        return ". ".join(comments) + "."
    
    def _identify_key_points(self, data: Dict[str, Any], sector: str) -> str:
        """Identifie les points clés à retenir"""
        key_points = []
        
        # Points basés sur les seuils critiques
        current_metrics = data.get('current_metrics', {})
        
        if 'debt_to_equity' in current_metrics:
            debt_ratio = current_metrics['debt_to_equity']
            if debt_ratio > 1.5:
                key_points.append("Niveau d'endettement élevé nécessitant une surveillance")
        
        if 'cash_ratio' in current_metrics:
            cash_ratio = current_metrics['cash_ratio']
            if cash_ratio < 0.1:
                key_points.append("Position de trésorerie tendue")
        
        # Points basés sur les tendances
        trends = data.get('trends', {})
        declining_metrics = [k for k, v in trends.items() if v < -10]
        if declining_metrics:
            key_points.append(f"Détérioration significative observée sur: {', '.join(declining_metrics)}")
        
        if not key_points:
            key_points.append("Situation financière globalement stable")
        
        return ". ".join(key_points) + "."
    
    def generate_contextual_recommendations(self, 
                                          financial_data: Dict[str, Any], 
                                          sector: str,
                                          risk_profile: str = "medium") -> List[ContextualRecommendation]:
        """Génère des recommandations contextuelles"""
        
        recommendations = []
        current_metrics = financial_data.get('current_metrics', {})
        
        # Recommandations basées sur la performance financière
        if 'roe' in current_metrics and current_metrics['roe'] < 8:
            recommendations.append(ContextualRecommendation(
                category="financial_performance",
                priority="high",
                title="Amélioration de la rentabilité",
                description="La rentabilité des capitaux propres est en dessous des standards sectoriels",
                impact="Amélioration de la valorisation et de l'attractivité pour les investisseurs",
                implementation_effort="Medium",
                timeline="6-12 mois",
                related_metrics=["roe", "roa", "net_margin"]
            ))
        
        # Recommandations basées sur la liquidité
        if 'current_ratio' in current_metrics and current_metrics['current_ratio'] < 1.2:
            recommendations.append(ContextualRecommendation(
                category="liquidity_management",
                priority="high",
                title="Renforcement de la position de liquidité",
                description="Le ratio de liquidité indique des risques de trésorerie",
                impact="Réduction du risque de défaillance et amélioration de la flexibilité financière",
                implementation_effort="Low",
                timeline="1-3 mois",
                related_metrics=["current_ratio", "quick_ratio", "cash_ratio"]
            ))
        
        # Recommandations sectorielles
        if sector in self.sector_benchmarks:
            sector_recs = self._generate_sector_specific_recommendations(
                current_metrics, sector, risk_profile
            )
            recommendations.extend(sector_recs)
        
        return recommendations
    
    def _generate_sector_specific_recommendations(self, 
                                                metrics: Dict[str, float], 
                                                sector: str,
                                                risk_profile: str) -> List[ContextualRecommendation]:
        """Génère des recommandations spécifiques au secteur"""
        
        recommendations = []
        benchmark = self.sector_benchmarks[sector]
        
        if sector == "banking":
            # Recommandations spécifiques au secteur bancaire
            if 'tier1_capital_ratio' in metrics:
                if metrics['tier1_capital_ratio'] < benchmark.metrics['tier1_capital_ratio']:
                    recommendations.append(ContextualRecommendation(
                        category="regulatory_compliance",
                        priority="high",
                        title="Renforcement des fonds propres",
                        description="Le ratio de fonds propres Tier 1 est en dessous de la médiane sectorielle",
                        impact="Conformité réglementaire et réduction du risque systémique",
                        implementation_effort="High",
                        timeline="12-18 mois",
                        related_metrics=["tier1_capital_ratio", "leverage_ratio"]
                    ))
        
        elif sector == "retail":
            # Recommandations spécifiques au commerce de détail
            if 'inventory_turnover' in metrics:
                if metrics['inventory_turnover'] < benchmark.metrics['inventory_turnover']:
                    recommendations.append(ContextualRecommendation(
                        category="operational_efficiency",
                        priority="medium",
                        title="Optimisation de la gestion des stocks",
                        description="La rotation des stocks est inférieure à la médiane sectorielle",
                        impact="Amélioration du cash-flow et réduction des coûts de stockage",
                        implementation_effort="Medium",
                        timeline="3-6 mois",
                        related_metrics=["inventory_turnover", "days_sales_outstanding"]
                    ))
        
        return recommendations
    
    def perform_sector_comparison(self, 
                                company_metrics: Dict[str, float], 
                                sector: str) -> Dict[str, Any]:
        """Effectue une comparaison sectorielle détaillée"""
        
        if sector not in self.sector_benchmarks:
            return {"error": f"Données de benchmark non disponibles pour le secteur {sector}"}
        
        benchmark = self.sector_benchmarks[sector]
        comparison_results = {
            "sector": sector,
            "benchmark_date": benchmark.last_updated,
            "sample_size": benchmark.sample_size,
            "metrics_comparison": {},
            "percentile_ranking": {},
            "overall_score": 0
        }
        
        scores = []
        
        for metric, company_value in company_metrics.items():
            if metric in benchmark.metrics:
                sector_median = benchmark.metrics[metric]
                percentiles = benchmark.percentiles.get(metric, {})
                
                # Calcul du percentile
                percentile_rank = self._calculate_percentile_rank(
                    company_value, percentiles
                )
                
                # Score relatif (0-100)
                if metric in ['cost_income_ratio', 'npl_ratio', 'debt_to_equity']:
                    # Métriques où plus bas = mieux
                    score = max(0, 100 - (company_value / sector_median) * 50)
                else:
                    # Métriques où plus haut = mieux
                    score = min(100, (company_value / sector_median) * 50)
                
                scores.append(score)
                
                comparison_results["metrics_comparison"][metric] = {
                    "company_value": company_value,
                    "sector_median": sector_median,
                    "difference_pct": ((company_value - sector_median) / sector_median) * 100,
                    "performance": "above" if company_value > sector_median else "below"
                }
                
                comparison_results["percentile_ranking"][metric] = {
                    "percentile": percentile_rank,
                    "interpretation": self._interpret_percentile(percentile_rank)
                }
        
        # Score global
        if scores:
            comparison_results["overall_score"] = round(statistics.mean(scores), 1)
        
        return comparison_results
    
    def _calculate_percentile_rank(self, value: float, percentiles: Dict[str, float]) -> int:
        """Calcule le rang percentile d'une valeur"""
        if not percentiles:
            return 50  # Médiane par défaut
        
        if value <= percentiles.get("p25", value):
            return 25
        elif value <= percentiles.get("p50", value):
            return 50
        elif value <= percentiles.get("p75", value):
            return 75
        elif value <= percentiles.get("p90", value):
            return 90
        else:
            return 95
    
    def _interpret_percentile(self, percentile: int) -> str:
        """Interprète un rang percentile"""
        if percentile >= 90:
            return "Excellent (top 10%)"
        elif percentile >= 75:
            return "Très bon (top 25%)"
        elif percentile >= 50:
            return "Au-dessus de la médiane"
        elif percentile >= 25:
            return "En dessous de la médiane"
        else:
            return "Nécessite amélioration (bottom 25%)"
    
    def generate_executive_summary(self, 
                                 financial_data: Dict[str, Any], 
                                 sector: str,
                                 company_name: str) -> str:
        """Génère un résumé exécutif intelligent"""
        
        summary_parts = []
        
        # Introduction
        summary_parts.append(f"Analyse financière de {company_name} pour l'exercice en cours.")
        
        # Performance globale
        if 'current_metrics' in financial_data:
            metrics = financial_data['current_metrics']
            if 'roe' in metrics:
                roe = metrics['roe']
                if roe > 15:
                    summary_parts.append(f"L'entreprise affiche une rentabilité excellente avec un ROE de {roe:.1f}%.")
                elif roe > 10:
                    summary_parts.append(f"La rentabilité est satisfaisante avec un ROE de {roe:.1f}%.")
                else:
                    summary_parts.append(f"La rentabilité nécessite une attention avec un ROE de {roe:.1f}%.")
        
        # Comparaison sectorielle
        if sector in self.sector_benchmarks:
            summary_parts.append(f"Par rapport au secteur {sector}, l'entreprise présente des performances mitigées.")
        
        # Tendances
        if 'trends' in financial_data:
            trends = financial_data['trends']
            positive_trends = [k for k, v in trends.items() if v > 5]
            negative_trends = [k for k, v in trends.items() if v < -5]
            
            if positive_trends:
                summary_parts.append(f"Les tendances positives incluent: {', '.join(positive_trends)}.")
            if negative_trends:
                summary_parts.append(f"Les points d'attention concernent: {', '.join(negative_trends)}.")
        
        # Recommandations principales
        recommendations = self.generate_contextual_recommendations(financial_data, sector)
        high_priority_recs = [r for r in recommendations if r.priority == "high"]
        
        if high_priority_recs:
            summary_parts.append(f"Les priorités d'action incluent: {high_priority_recs[0].title.lower()}.")
        
        return " ".join(summary_parts)
    
    def get_benchmark_data(self, sector: str) -> Optional[SectorBenchmark]:
        """Retourne les données de benchmark pour un secteur"""
        return self.sector_benchmarks.get(sector)
    
    def update_benchmark_data(self, sector: str, new_data: Dict[str, Any]):
        """Met à jour les données de benchmark pour un secteur"""
        if sector in self.sector_benchmarks:
            benchmark = self.sector_benchmarks[sector]
            benchmark.metrics.update(new_data.get('metrics', {}))
            benchmark.percentiles.update(new_data.get('percentiles', {}))
            benchmark.last_updated = datetime.now().isoformat()
        else:
            # Créer un nouveau benchmark
            self.sector_benchmarks[sector] = SectorBenchmark(
                sector=sector,
                metrics=new_data.get('metrics', {}),
                percentiles=new_data.get('percentiles', {}),
                sample_size=new_data.get('sample_size', 0),
                last_updated=datetime.now().isoformat()
            )

