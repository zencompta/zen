"""
Service de visualisations avancées
Génère des graphiques 3D, tableaux de bord exécutifs, cartes de chaleur pour les risques
et chronologies visuelles des événements
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D

@dataclass
class VisualizationConfig:
    """Configuration pour les visualisations"""
    theme: str = "plotly_white"
    color_palette: List[str] = None
    font_family: str = "Arial"
    font_size: int = 12
    width: int = 1200
    height: int = 800
    
    def __post_init__(self):
        if self.color_palette is None:
            self.color_palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]

@dataclass
class RiskHeatmapData:
    """Données pour la carte de chaleur des risques"""
    risk_name: str
    category: str
    probability: float  # 1-5
    impact: float      # 1-5
    current_controls: str
    residual_risk: float
    owner: str

@dataclass
class TimelineEvent:
    """Événement pour la chronologie"""
    date: datetime
    title: str
    description: str
    category: str
    impact_level: str  # low, medium, high, critical
    related_accounts: List[str]

class AdvancedVisualizationService:
    """Service de génération de visualisations avancées"""
    
    def __init__(self):
        self.config = VisualizationConfig()
        self.risk_categories = {
            "financial": "Risques Financiers",
            "operational": "Risques Opérationnels", 
            "compliance": "Risques de Conformité",
            "strategic": "Risques Stratégiques",
            "technology": "Risques Technologiques",
            "reputation": "Risques de Réputation"
        }
        
    def create_3d_financial_surface(self, 
                                  data: Dict[str, Any], 
                                  x_metric: str, 
                                  y_metric: str, 
                                  z_metric: str) -> str:
        """Crée un graphique 3D de surface pour l'analyse financière"""
        
        # Préparer les données
        x_data = data.get(x_metric, [])
        y_data = data.get(y_metric, [])
        z_data = data.get(z_metric, [])
        
        if not all([x_data, y_data, z_data]):
            raise ValueError("Données insuffisantes pour le graphique 3D")
        
        # Créer la surface 3D
        fig = go.Figure(data=[go.Surface(
            x=x_data,
            y=y_data,
            z=z_data,
            colorscale='Viridis',
            showscale=True
        )])
        
        fig.update_layout(
            title=f'Analyse 3D: {z_metric} en fonction de {x_metric} et {y_metric}',
            scene=dict(
                xaxis_title=x_metric.replace('_', ' ').title(),
                yaxis_title=y_metric.replace('_', ' ').title(),
                zaxis_title=z_metric.replace('_', ' ').title(),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            width=self.config.width,
            height=self.config.height,
            font=dict(family=self.config.font_family, size=self.config.font_size)
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_3d_scatter_analysis(self, 
                                 companies_data: List[Dict[str, Any]], 
                                 x_metric: str, 
                                 y_metric: str, 
                                 z_metric: str,
                                 size_metric: str = None,
                                 color_metric: str = None) -> str:
        """Crée un graphique 3D scatter pour comparer plusieurs entreprises"""
        
        # Extraire les données
        x_values = [company.get(x_metric, 0) for company in companies_data]
        y_values = [company.get(y_metric, 0) for company in companies_data]
        z_values = [company.get(z_metric, 0) for company in companies_data]
        names = [company.get('name', f'Entreprise {i}') for i, company in enumerate(companies_data)]
        
        # Taille et couleur des points
        sizes = [company.get(size_metric, 10) for company in companies_data] if size_metric else [10] * len(companies_data)
        colors = [company.get(color_metric, 0) for company in companies_data] if color_metric else x_values
        
        fig = go.Figure(data=[go.Scatter3d(
            x=x_values,
            y=y_values,
            z=z_values,
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                colorscale='Viridis',
                showscale=True,
                opacity=0.8,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            text=names,
            hovertemplate=
            '<b>%{text}</b><br>' +
            f'{x_metric}: %{{x}}<br>' +
            f'{y_metric}: %{{y}}<br>' +
            f'{z_metric}: %{{z}}<br>' +
            '<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'Analyse Comparative 3D: {x_metric} vs {y_metric} vs {z_metric}',
            scene=dict(
                xaxis_title=x_metric.replace('_', ' ').title(),
                yaxis_title=y_metric.replace('_', ' ').title(),
                zaxis_title=z_metric.replace('_', ' ').title()
            ),
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_executive_dashboard(self, 
                                 financial_data: Dict[str, Any],
                                 kpis: List[Dict[str, Any]],
                                 trends: Dict[str, List[float]],
                                 alerts: List[Dict[str, Any]]) -> str:
        """Crée un tableau de bord exécutif complet"""
        
        # Créer une grille de sous-graphiques
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=[
                'KPIs Principaux', 'Tendances Financières', 'Alertes Critiques',
                'Performance vs Budget', 'Analyse des Ratios', 'Cash Flow',
                'Comparaison Sectorielle', 'Risques Identifiés', 'Prévisions'
            ],
            specs=[
                [{"type": "indicator"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "scatter"}, {"type": "waterfall"}],
                [{"type": "bar"}, {"type": "heatmap"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.05
        )
        
        # 1. KPIs Principaux (Indicateurs)
        for i, kpi in enumerate(kpis[:3]):
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=kpi['current_value'],
                    delta={'reference': kpi['target_value'], 'relative': True},
                    title={'text': kpi['name']},
                    number={'suffix': kpi.get('suffix', '')},
                    domain={'row': 0, 'column': 0}
                ),
                row=1, col=1
            )
        
        # 2. Tendances Financières
        for metric, values in trends.items():
            fig.add_trace(
                go.Scatter(
                    y=values,
                    mode='lines+markers',
                    name=metric,
                    line=dict(width=3)
                ),
                row=1, col=2
            )
        
        # 3. Alertes Critiques
        alert_categories = [alert['category'] for alert in alerts]
        alert_counts = {}
        for cat in alert_categories:
            alert_counts[cat] = alert_counts.get(cat, 0) + 1
        
        fig.add_trace(
            go.Bar(
                x=list(alert_counts.keys()),
                y=list(alert_counts.values()),
                marker_color='red',
                opacity=0.7
            ),
            row=1, col=3
        )
        
        # 4. Performance vs Budget
        budget_data = financial_data.get('budget_comparison', {})
        if budget_data:
            fig.add_trace(
                go.Scatter(
                    x=list(budget_data.keys()),
                    y=[v['actual'] for v in budget_data.values()],
                    mode='lines+markers',
                    name='Réalisé',
                    line=dict(color='blue', width=3)
                ),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=list(budget_data.keys()),
                    y=[v['budget'] for v in budget_data.values()],
                    mode='lines+markers',
                    name='Budget',
                    line=dict(color='green', width=3, dash='dash')
                ),
                row=2, col=1
            )
        
        # 5. Analyse des Ratios (Radar Chart simulé avec scatter)
        ratios = financial_data.get('ratios', {})
        if ratios:
            ratio_names = list(ratios.keys())
            ratio_values = list(ratios.values())
            
            fig.add_trace(
                go.Scatterpolar(
                    r=ratio_values,
                    theta=ratio_names,
                    fill='toself',
                    name='Ratios Actuels'
                ),
                row=2, col=2
            )
        
        # 6. Cash Flow (Waterfall)
        cash_flow_data = financial_data.get('cash_flow', {})
        if cash_flow_data:
            fig.add_trace(
                go.Waterfall(
                    name="Cash Flow",
                    orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=["Exploitation", "Investissement", "Financement", "Net"],
                    y=[
                        cash_flow_data.get('operating', 0),
                        cash_flow_data.get('investing', 0),
                        cash_flow_data.get('financing', 0),
                        cash_flow_data.get('net', 0)
                    ]
                ),
                row=2, col=3
            )
        
        # Mise à jour du layout
        fig.update_layout(
            title_text="Tableau de Bord Exécutif",
            title_x=0.5,
            showlegend=False,
            height=1200,
            width=1600,
            font=dict(family=self.config.font_family, size=10)
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_risk_heatmap(self, risks: List[RiskHeatmapData]) -> str:
        """Crée une carte de chaleur des risques"""
        
        # Préparer les données pour la heatmap
        risk_matrix = np.zeros((5, 5))
        risk_labels = [['' for _ in range(5)] for _ in range(5)]
        risk_details = [[[] for _ in range(5)] for _ in range(5)]
        
        for risk in risks:
            prob_idx = int(risk.probability) - 1
            impact_idx = int(risk.impact) - 1
            
            if 0 <= prob_idx < 5 and 0 <= impact_idx < 5:
                risk_matrix[impact_idx][prob_idx] += 1
                risk_details[impact_idx][prob_idx].append(risk.risk_name)
        
        # Créer la heatmap avec Plotly
        fig = go.Figure(data=go.Heatmap(
            z=risk_matrix,
            x=['Très Faible', 'Faible', 'Moyen', 'Élevé', 'Très Élevé'],
            y=['Très Faible', 'Faible', 'Moyen', 'Élevé', 'Très Élevé'],
            colorscale=[
                [0, 'green'],
                [0.3, 'yellow'], 
                [0.6, 'orange'],
                [1, 'red']
            ],
            showscale=True,
            hovertemplate='Probabilité: %{x}<br>Impact: %{y}<br>Nombre de risques: %{z}<extra></extra>'
        ))
        
        # Ajouter les annotations
        annotations = []
        for i in range(5):
            for j in range(5):
                if risk_matrix[i][j] > 0:
                    risk_names = risk_details[i][j]
                    annotation_text = f"{int(risk_matrix[i][j])}<br>{'<br>'.join(risk_names[:3])}"
                    if len(risk_names) > 3:
                        annotation_text += f"<br>+{len(risk_names)-3} autres"
                    
                    annotations.append(
                        dict(
                            x=j, y=i,
                            text=annotation_text,
                            showarrow=False,
                            font=dict(color="white" if risk_matrix[i][j] > 2 else "black", size=10)
                        )
                    )
        
        fig.update_layout(
            title='Carte de Chaleur des Risques',
            xaxis_title='Probabilité',
            yaxis_title='Impact',
            annotations=annotations,
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_detailed_risk_analysis(self, risks: List[RiskHeatmapData]) -> str:
        """Crée une analyse détaillée des risques avec graphiques multiples"""
        
        # Créer des sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Distribution des Risques par Catégorie',
                'Risques par Niveau de Criticité',
                'Évolution du Risque Résiduel',
                'Top 10 des Risques Critiques'
            ],
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "bar"}]
            ]
        )
        
        # 1. Distribution par catégorie
        categories = [risk.category for risk in risks]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        fig.add_trace(
            go.Pie(
                labels=list(category_counts.keys()),
                values=list(category_counts.values()),
                hole=0.3
            ),
            row=1, col=1
        )
        
        # 2. Risques par niveau de criticité
        criticality_levels = []
        for risk in risks:
            score = risk.probability * risk.impact
            if score >= 20:
                criticality_levels.append('Critique')
            elif score >= 12:
                criticality_levels.append('Élevé')
            elif score >= 6:
                criticality_levels.append('Moyen')
            else:
                criticality_levels.append('Faible')
        
        criticality_counts = {}
        for level in criticality_levels:
            criticality_counts[level] = criticality_counts.get(level, 0) + 1
        
        colors = {'Critique': 'red', 'Élevé': 'orange', 'Moyen': 'yellow', 'Faible': 'green'}
        fig.add_trace(
            go.Bar(
                x=list(criticality_counts.keys()),
                y=list(criticality_counts.values()),
                marker_color=[colors.get(k, 'blue') for k in criticality_counts.keys()]
            ),
            row=1, col=2
        )
        
        # 3. Risque résiduel vs initial
        initial_scores = [risk.probability * risk.impact for risk in risks]
        residual_scores = [risk.residual_risk for risk in risks]
        
        fig.add_trace(
            go.Scatter(
                x=initial_scores,
                y=residual_scores,
                mode='markers',
                marker=dict(
                    size=10,
                    color=initial_scores,
                    colorscale='Reds',
                    showscale=True
                ),
                text=[risk.risk_name for risk in risks],
                hovertemplate='<b>%{text}</b><br>Risque Initial: %{x}<br>Risque Résiduel: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Ligne de référence (y=x)
        max_score = max(max(initial_scores), max(residual_scores))
        fig.add_trace(
            go.Scatter(
                x=[0, max_score],
                y=[0, max_score],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Référence (pas d\'amélioration)'
            ),
            row=2, col=1
        )
        
        # 4. Top 10 des risques critiques
        risks_sorted = sorted(risks, key=lambda r: r.probability * r.impact, reverse=True)[:10]
        
        fig.add_trace(
            go.Bar(
                x=[risk.probability * risk.impact for risk in risks_sorted],
                y=[risk.risk_name for risk in risks_sorted],
                orientation='h',
                marker_color='red',
                opacity=0.7
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Analyse Détaillée des Risques",
            showlegend=False,
            height=1000,
            width=1400
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_timeline_visualization(self, events: List[TimelineEvent]) -> str:
        """Crée une chronologie visuelle des événements"""
        
        # Trier les événements par date
        events_sorted = sorted(events, key=lambda e: e.date)
        
        # Préparer les données
        dates = [event.date for event in events_sorted]
        titles = [event.title for event in events_sorted]
        categories = [event.category for event in events_sorted]
        impacts = [event.impact_level for event in events_sorted]
        
        # Couleurs par niveau d'impact
        impact_colors = {
            'low': 'green',
            'medium': 'yellow', 
            'high': 'orange',
            'critical': 'red'
        }
        
        colors = [impact_colors.get(impact, 'blue') for impact in impacts]
        
        # Créer le graphique timeline
        fig = go.Figure()
        
        # Ajouter les événements
        fig.add_trace(go.Scatter(
            x=dates,
            y=[1] * len(dates),  # Tous sur la même ligne
            mode='markers+text',
            marker=dict(
                size=15,
                color=colors,
                line=dict(width=2, color='black')
            ),
            text=titles,
            textposition="top center",
            hovertemplate=
            '<b>%{text}</b><br>' +
            'Date: %{x}<br>' +
            'Catégorie: ' + '<br>'.join([f'{cat}' for cat in categories]) + '<br>' +
            '<extra></extra>',
            showlegend=False
        ))
        
        # Ajouter une ligne de base
        fig.add_trace(go.Scatter(
            x=[min(dates), max(dates)],
            y=[1, 1],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))
        
        # Ajouter des annotations pour les événements critiques
        for i, event in enumerate(events_sorted):
            if event.impact_level == 'critical':
                fig.add_annotation(
                    x=event.date,
                    y=1.2,
                    text=f"⚠️ {event.title}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="red",
                    bgcolor="rgba(255,0,0,0.1)",
                    bordercolor="red"
                )
        
        fig.update_layout(
            title='Chronologie des Événements Comptables',
            xaxis_title='Date',
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[0.5, 1.5]
            ),
            height=400,
            width=self.config.width,
            showlegend=True
        )
        
        # Ajouter une légende pour les niveaux d'impact
        for impact, color in impact_colors.items():
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=impact.title(),
                showlegend=True
            ))
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_interactive_timeline(self, events: List[TimelineEvent]) -> str:
        """Crée une chronologie interactive avec zoom et filtres"""
        
        # Grouper les événements par catégorie
        categories = list(set([event.category for event in events]))
        
        fig = go.Figure()
        
        for i, category in enumerate(categories):
            category_events = [e for e in events if e.category == category]
            category_events.sort(key=lambda e: e.date)
            
            dates = [event.date for event in category_events]
            y_positions = [i + 1] * len(category_events)
            titles = [event.title for event in category_events]
            descriptions = [event.description for event in category_events]
            
            # Couleurs par niveau d'impact
            impact_colors = {
                'low': 'green',
                'medium': 'yellow',
                'high': 'orange', 
                'critical': 'red'
            }
            
            colors = [impact_colors.get(event.impact_level, 'blue') for event in category_events]
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=y_positions,
                mode='markers+lines',
                name=category,
                marker=dict(
                    size=12,
                    color=colors,
                    line=dict(width=2, color='black')
                ),
                line=dict(width=2),
                text=titles,
                hovertemplate=
                '<b>%{text}</b><br>' +
                'Date: %{x}<br>' +
                'Catégorie: ' + category + '<br>' +
                'Description: ' + '<br>'.join([desc[:100] + '...' if len(desc) > 100 else desc for desc in descriptions]) + '<br>' +
                '<extra></extra>'
            ))
        
        fig.update_layout(
            title='Chronologie Interactive des Événements',
            xaxis_title='Date',
            yaxis_title='Catégories',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(1, len(categories) + 1)),
                ticktext=categories
            ),
            height=600,
            width=self.config.width,
            hovermode='closest'
        )
        
        # Ajouter des boutons de filtre
        buttons = []
        for category in ['Tous'] + categories:
            if category == 'Tous':
                visible = [True] * len(categories)
            else:
                visible = [cat == category for cat in categories]
            
            buttons.append(dict(
                label=category,
                method="update",
                args=[{"visible": visible}]
            ))
        
        fig.update_layout(
            updatemenus=[dict(
                type="buttons",
                direction="left",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=1.02,
                yanchor="top"
            )]
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_animated_trend_analysis(self, 
                                     time_series_data: Dict[str, List[Dict[str, Any]]],
                                     metrics: List[str]) -> str:
        """Crée une analyse de tendances animée"""
        
        # Préparer les données pour l'animation
        all_dates = set()
        for metric_data in time_series_data.values():
            all_dates.update([d['date'] for d in metric_data])
        
        all_dates = sorted(list(all_dates))
        
        fig = go.Figure()
        
        # Ajouter les traces pour chaque métrique
        for metric in metrics:
            if metric in time_series_data:
                metric_data = time_series_data[metric]
                dates = [d['date'] for d in metric_data]
                values = [d['value'] for d in metric_data]
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title(),
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
        
        # Configuration de l'animation
        fig.update_layout(
            title='Analyse de Tendances Animée',
            xaxis_title='Date',
            yaxis_title='Valeur',
            height=600,
            width=self.config.width,
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 500, "redraw": True},
                                     "fromcurrent": True, "transition": {"duration": 300}}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": True},
                                       "mode": "immediate",
                                       "transition": {"duration": 0}}])
                ]
            )]
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def export_visualization(self, fig_html: str, format: str = "png") -> str:
        """Exporte une visualisation dans différents formats"""
        # Cette méthode peut être étendue pour exporter en PNG, SVG, PDF
        # Pour l'instant, retourne le HTML
        return fig_html
    
    def get_visualization_config(self) -> VisualizationConfig:
        """Retourne la configuration actuelle des visualisations"""
        return self.config
    
    def update_visualization_config(self, new_config: Dict[str, Any]):
        """Met à jour la configuration des visualisations"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

