import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour les serveurs
import io
import base64
from PIL import Image as PILImage

class ReportGenerator:
    """Générateur de rapports d'audit de haute qualité"""
    
    def __init__(self, project_data: Dict, analysis_results: List[Dict], accounting_standard: str = 'IFRS'):
        self.project_data = project_data
        self.analysis_results = analysis_results
        self.accounting_standard = accounting_standard
        
        # Configuration des couleurs du thème professionnel
        self.colors = {
            'primary': HexColor('#1e40af'),      # Bleu marine
            'secondary': HexColor('#64748b'),     # Gris ardoise
            'accent': HexColor('#059669'),        # Vert émeraude
            'warning': HexColor('#d97706'),       # Orange
            'danger': HexColor('#dc2626'),        # Rouge
            'light_gray': HexColor('#f8fafc'),    # Gris très clair
            'dark_gray': HexColor('#334155')      # Gris foncé
        }
        
        # Styles de paragraphe personnalisés
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
        # Configuration des graphiques
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
    
    def _create_custom_styles(self):
        """Crée des styles personnalisés pour le rapport"""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=20,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold'
        ))
        
        # En-tête de section
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=15,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.colors['primary'],
            borderPadding=5
        ))
        
        # Corps de texte professionnel
        self.styles.add(ParagraphStyle(
            name='ProfessionalBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Style pour les recommandations
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leftIndent=20,
            bulletIndent=10,
            fontName='Helvetica',
            textColor=self.colors['dark_gray']
        ))
    
    def generate_comprehensive_report(self, output_path: str) -> Dict[str, Any]:
        """Génère un rapport d'audit complet et professionnel"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # 1. Page de couverture
            story.extend(self._create_cover_page())
            story.append(PageBreak())
            
            # 2. Résumé exécutif
            story.extend(self._create_executive_summary())
            story.append(PageBreak())
            
            # 3. Table des matières
            story.extend(self._create_table_of_contents())
            story.append(PageBreak())
            
            # 4. Informations du projet
            story.extend(self._create_project_information())
            
            # 5. Résultats d'analyse
            story.extend(self._create_analysis_results())
            
            # 6. Graphiques et visualisations
            story.extend(self._create_visualizations())
            
            # 7. Recommandations
            story.extend(self._create_recommendations())
            
            # 8. Annexes
            story.extend(self._create_appendices())
            
            # Construire le PDF
            doc.build(story)
            
            return {
                'success': True,
                'file_path': output_path,
                'pages_count': len([item for item in story if isinstance(item, PageBreak)]) + 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_cover_page(self) -> List:
        """Crée la page de couverture professionnelle"""
        elements = []
        
        # Logo ou en-tête (espace réservé)
        elements.append(Spacer(1, 2*inch))
        
        # Titre principal
        title = f"RAPPORT D'AUDIT COMPTABLE"
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Sous-titre avec nom de l'entreprise
        subtitle = f"Entreprise: {self.project_data.get('company_name', 'N/A')}"
        elements.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Informations de l'audit
        audit_info = f"""
        <b>Exercice:</b> {self.project_data.get('audit_year', 'N/A')}<br/>
        <b>Norme comptable:</b> {self.project_data.get('accounting_standard', 'N/A')}<br/>
        <b>Date du rapport:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Généré par:</b> ZenCompta Professional
        """
        elements.append(Paragraph(audit_info, self.styles['ProfessionalBody']))
        elements.append(Spacer(1, 2*inch))
        
        # Note de confidentialité
        confidentiality = """
        <b>CONFIDENTIEL</b><br/>
        Ce rapport contient des informations confidentielles et privilégiées. 
        Il est destiné exclusivement à l'usage de la direction et des auditeurs autorisés.
        """
        elements.append(Paragraph(confidentiality, self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_executive_summary(self) -> List:
        """Crée le résumé exécutif"""
        elements = []
        
        elements.append(Paragraph("RÉSUMÉ EXÉCUTIF", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Synthèse des résultats
        summary_text = self._generate_executive_summary_text()
        elements.append(Paragraph(summary_text, self.styles['ProfessionalBody']))
        
        # Tableau de synthèse des risques
        risk_summary = self._create_risk_summary_table()
        elements.append(Spacer(1, 0.2*inch))
        elements.append(risk_summary)
        
        return elements
    
    def _create_table_of_contents(self) -> List:
        """Crée la table des matières"""
        elements = []
        
        elements.append(Paragraph("TABLE DES MATIÈRES", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        toc_data = [
            ['Section', 'Page'],
            ['1. Informations du Projet', '4'],
            ['2. Analyse de la Balance', '5'],
            ['3. Analyse des Écritures', '7'],
            ['4. Analyse par Ratios', '9'],
            ['5. Détection de Fraude', '11'],
            ['6. Visualisations', '13'],
            ['7. Recommandations', '15'],
            ['8. Annexes', '17']
        ]
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(toc_table)
        
        return elements
    
    def _create_project_information(self) -> List:
        """Crée la section d'informations du projet"""
        elements = []
        
        elements.append(Paragraph("1. INFORMATIONS DU PROJET", self.styles['SectionHeader']))
        
        # Tableau des informations du projet
        project_info = [
            ['Élément', 'Valeur'],
            ['Nom de l\'entreprise', self.project_data.get('company_name', 'N/A')],
            ['Exercice comptable', str(self.project_data.get('audit_year', 'N/A'))],
            ['Norme comptable', self.project_data.get('accounting_standard', 'N/A')],
            ['Date de création', self.project_data.get('created_at', 'N/A')],
            ['Statut du projet', self.project_data.get('status', 'N/A')],
            ['Nombre d\'écritures', str(self._get_total_entries())],
            ['Période d\'analyse', self._get_analysis_period()]
        ]
        
        info_table = Table(project_info, colWidths=[2.5*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Objectifs de l'audit
        objectives_text = f"""
        <b>Objectifs de l'audit:</b><br/>
        • Vérifier la conformité aux normes {self.accounting_standard}<br/>
        • Détecter les anomalies et incohérences comptables<br/>
        • Évaluer les risques financiers et opérationnels<br/>
        • Fournir des recommandations d'amélioration<br/>
        • Assurer la fiabilité des états financiers
        """
        elements.append(Paragraph(objectives_text, self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_analysis_results(self) -> List:
        """Crée les sections de résultats d'analyse"""
        elements = []
        
        for analysis in self.analysis_results:
            analysis_type = analysis.get('analysis_type', 'unknown')
            
            if analysis_type == 'balance_analysis':
                elements.extend(self._create_balance_analysis_section(analysis))
            elif analysis_type == 'journal_analysis':
                elements.extend(self._create_journal_analysis_section(analysis))
            elif analysis_type == 'ratio_analysis':
                elements.extend(self._create_ratio_analysis_section(analysis))
            elif analysis_type == 'fraud_detection':
                elements.extend(self._create_fraud_analysis_section(analysis))
        
        return elements
    
    def _create_balance_analysis_section(self, analysis: Dict) -> List:
        """Crée la section d'analyse de balance"""
        elements = []
        
        elements.append(Paragraph("2. ANALYSE DE LA BALANCE", self.styles['SectionHeader']))
        
        # Résumé de l'équilibre comptable
        balance_check = analysis.get('summary', {}).get('balance_check', {})
        
        balance_text = f"""
        <b>Vérification de l'équilibre comptable:</b><br/>
        • Total Débit: {balance_check.get('total_debit', 0):,.2f} €<br/>
        • Total Crédit: {balance_check.get('total_credit', 0):,.2f} €<br/>
        • Différence: {balance_check.get('difference', 0):,.2f} €<br/>
        • Équilibré: {'Oui' if balance_check.get('is_balanced', False) else 'Non'}<br/>
        • Écart en %: {balance_check.get('balance_percentage', 0):.4f}%
        """
        elements.append(Paragraph(balance_text, self.styles['ProfessionalBody']))
        
        # Anomalies détectées
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("<b>Anomalies détectées:</b>", self.styles['ProfessionalBody']))
            
            for anomaly in anomalies[:5]:  # Limiter à 5 anomalies principales
                anomaly_text = f"• {anomaly.get('description', 'Anomalie non décrite')}"
                elements.append(Paragraph(anomaly_text, self.styles['Recommendation']))
        
        # Niveau de risque
        risk_level = analysis.get('risk_level', 'low')
        risk_color = self._get_risk_color(risk_level)
        risk_text = f"<b>Niveau de risque global:</b> <font color='{risk_color}'>{risk_level.upper()}</font>"
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(risk_text, self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_journal_analysis_section(self, analysis: Dict) -> List:
        """Crée la section d'analyse des journaux"""
        elements = []
        
        elements.append(Paragraph("3. ANALYSE DES ÉCRITURES DE JOURNAL", self.styles['SectionHeader']))
        
        # Statistiques des écritures
        summary = analysis.get('summary', {})
        unbalanced_entries = summary.get('unbalanced_entries', 0)
        
        journal_text = f"""
        <b>Statistiques des écritures:</b><br/>
        • Écritures déséquilibrées: {unbalanced_entries}<br/>
        • Anomalies détectées: {len(analysis.get('anomalies', []))}<br/>
        • Niveau de risque: {analysis.get('risk_level', 'low').upper()}
        """
        elements.append(Paragraph(journal_text, self.styles['ProfessionalBody']))
        
        # Détail des anomalies
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("<b>Détail des anomalies:</b>", self.styles['ProfessionalBody']))
            
            # Grouper par type d'anomalie
            anomaly_types = {}
            for anomaly in anomalies:
                anom_type = anomaly.get('type', 'unknown')
                if anom_type not in anomaly_types:
                    anomaly_types[anom_type] = []
                anomaly_types[anom_type].append(anomaly)
            
            for anom_type, anom_list in anomaly_types.items():
                type_text = f"<b>{anom_type.replace('_', ' ').title()}:</b> {len(anom_list)} occurrence(s)"
                elements.append(Paragraph(type_text, self.styles['Recommendation']))
        
        return elements
    
    def _create_ratio_analysis_section(self, analysis: Dict) -> List:
        """Crée la section d'analyse par ratios"""
        elements = []
        
        elements.append(Paragraph("4. ANALYSE PAR RATIOS FINANCIERS", self.styles['SectionHeader']))
        
        ratios = analysis.get('ratios', {})
        interpretations = analysis.get('interpretations', [])
        
        # Tableau des ratios
        ratio_data = [['Ratio', 'Valeur', 'Interprétation']]
        
        for category, category_ratios in ratios.items():
            for ratio_name, ratio_value in category_ratios.items():
                interpretation = self._get_ratio_interpretation(ratio_name, ratio_value)
                ratio_data.append([
                    ratio_name.replace('_', ' ').title(),
                    f"{ratio_value:.3f}" if isinstance(ratio_value, (int, float)) else str(ratio_value),
                    interpretation
                ])
        
        if len(ratio_data) > 1:
            ratio_table = Table(ratio_data, colWidths=[2*inch, 1*inch, 2.5*inch])
            ratio_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(ratio_table)
        
        # Interprétations générales
        if interpretations:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("<b>Interprétations:</b>", self.styles['ProfessionalBody']))
            for interpretation in interpretations:
                elements.append(Paragraph(f"• {interpretation}", self.styles['Recommendation']))
        
        return elements
    
    def _create_fraud_analysis_section(self, analysis: Dict) -> List:
        """Crée la section de détection de fraude"""
        elements = []
        
        elements.append(Paragraph("5. DÉTECTION D'INDICATEURS DE FRAUDE", self.styles['SectionHeader']))
        
        indicators = analysis.get('indicators', [])
        risk_level = analysis.get('risk_level', 'low')
        
        fraud_text = f"""
        <b>Résumé de l'analyse:</b><br/>
        • Indicateurs détectés: {len(indicators)}<br/>
        • Niveau de risque de fraude: <font color='{self._get_risk_color(risk_level)}'>{risk_level.upper()}</font>
        """
        elements.append(Paragraph(fraud_text, self.styles['ProfessionalBody']))
        
        if indicators:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("<b>Indicateurs détectés:</b>", self.styles['ProfessionalBody']))
            
            for indicator in indicators:
                severity = indicator.get('severity', 'low')
                description = indicator.get('description', 'Indicateur non décrit')
                indicator_text = f"• [{severity.upper()}] {description}"
                elements.append(Paragraph(indicator_text, self.styles['Recommendation']))
        else:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Aucun indicateur de fraude majeur détecté.", self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_visualizations(self) -> List:
        """Crée les graphiques et visualisations"""
        elements = []
        
        elements.append(Paragraph("6. VISUALISATIONS ET GRAPHIQUES", self.styles['SectionHeader']))
        
        # Graphique de répartition des risques
        risk_chart = self._create_risk_distribution_chart()
        if risk_chart:
            elements.append(risk_chart)
            elements.append(Spacer(1, 0.3*inch))
        
        # Graphique d'évolution des montants
        amount_chart = self._create_amount_evolution_chart()
        if amount_chart:
            elements.append(amount_chart)
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_recommendations(self) -> List:
        """Crée la section des recommandations"""
        elements = []
        
        elements.append(Paragraph("7. RECOMMANDATIONS", self.styles['SectionHeader']))
        
        # Collecter toutes les recommandations
        all_recommendations = []
        for analysis in self.analysis_results:
            recommendations = analysis.get('recommendations', [])
            all_recommendations.extend(recommendations)
        
        if all_recommendations:
            elements.append(Paragraph("<b>Recommandations prioritaires:</b>", self.styles['ProfessionalBody']))
            
            for i, recommendation in enumerate(all_recommendations[:10], 1):  # Top 10
                rec_text = f"{i}. {recommendation}"
                elements.append(Paragraph(rec_text, self.styles['Recommendation']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("Aucune recommandation spécifique. Les analyses n'ont révélé aucun problème majeur.", self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_appendices(self) -> List:
        """Crée les annexes"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("8. ANNEXES", self.styles['SectionHeader']))
        
        # Annexe A: Méthodologie
        elements.append(Paragraph("Annexe A: Méthodologie d'audit", self.styles['CustomSubtitle']))
        methodology_text = f"""
        Cette analyse a été réalisée selon les normes {self.accounting_standard} en utilisant les méthodes suivantes:
        
        • Analyse de l'équilibre comptable global
        • Vérification de la cohérence des écritures
        • Calcul et interprétation des ratios financiers
        • Application de la loi de Benford pour la détection de fraude
        • Analyse statistique des montants et des dates
        • Contrôles de vraisemblance selon les normes sectorielles
        """
        elements.append(Paragraph(methodology_text, self.styles['ProfessionalBody']))
        
        # Annexe B: Définitions
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Annexe B: Définitions et seuils", self.styles['CustomSubtitle']))
        definitions_text = """
        • <b>Seuil de matérialité:</b> 5% du résultat net ou 0.5% du total actif
        • <b>Variance significative:</b> Écart supérieur à 10% par rapport à la moyenne
        • <b>Montant élevé:</b> Supérieur à 100 000 € (ajustable selon le contexte)
        • <b>Loi de Benford:</b> Distribution naturelle des premiers chiffres dans les données financières
        """
        elements.append(Paragraph(definitions_text, self.styles['ProfessionalBody']))
        
        return elements
    
    def _generate_executive_summary_text(self) -> str:
        """Génère le texte du résumé exécutif"""
        total_analyses = len(self.analysis_results)
        high_risk_analyses = len([a for a in self.analysis_results if a.get('risk_level') == 'high'])
        
        company_name = self.project_data.get('company_name', "l'entreprise")
        summary = f"""
        Ce rapport présente les résultats de l'audit comptable de {company_name} 
        pour l'exercice {self.project_data.get('audit_year', 'N/A')}, réalisé selon les normes {self.accounting_standard}.
        
        <b>Synthèse des analyses:</b><br/>
        • {total_analyses} analyses ont été effectuées
        • {high_risk_analyses} analyses présentent un risque élevé
        • {self._get_total_entries()} écritures comptables ont été examinées
        
        <b>Conclusion générale:</b><br/>
        {self._generate_overall_conclusion()}
        """
        
        return summary
    
    def _generate_overall_conclusion(self) -> str:
        """Génère la conclusion générale basée sur les analyses"""
        risk_levels = [analysis.get('risk_level', 'low') for analysis in self.analysis_results]
        
        if 'critical' in risk_levels:
            return "Des risques critiques ont été identifiés nécessitant une attention immédiate."
        elif 'high' in risk_levels:
            return "Des risques élevés ont été détectés et doivent être traités prioritairement."
        elif 'medium' in risk_levels:
            return "Quelques points d'attention ont été identifiés mais le niveau de risque reste modéré."
        else:
            return "L'audit n'a révélé aucun risque majeur. La comptabilité présente un niveau de fiabilité satisfaisant."
    
    def _create_risk_summary_table(self) -> Table:
        """Crée un tableau de synthèse des risques"""
        risk_data = [['Type d\'analyse', 'Niveau de risque', 'Anomalies']]
        
        for analysis in self.analysis_results:
            analysis_name = analysis.get('analysis_type', 'Unknown').replace('_', ' ').title()
            risk_level = analysis.get('risk_level', 'low').upper()
            anomalies_count = len(analysis.get('anomalies', []))
            
            risk_data.append([analysis_name, risk_level, str(anomalies_count)])
        
        risk_table = Table(risk_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return risk_table
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Retourne la couleur associée au niveau de risque"""
        colors_map = {
            'low': '#059669',      # Vert
            'medium': '#d97706',   # Orange
            'high': '#dc2626',     # Rouge
            'critical': '#7c2d12'  # Rouge foncé
        }
        return colors_map.get(risk_level.lower(), '#64748b')
    
    def _get_ratio_interpretation(self, ratio_name: str, ratio_value: float) -> str:
        """Retourne l'interprétation d'un ratio"""
        interpretations = {
            'current_ratio': 'Bon' if 1 <= ratio_value <= 2 else 'À surveiller',
            'debt_to_assets': 'Acceptable' if ratio_value <= 0.6 else 'Élevé',
            'inventory_turnover': 'Efficace' if ratio_value >= 4 else 'Lent'
        }
        return interpretations.get(ratio_name, 'À analyser')
    
    def _get_total_entries(self) -> int:
        """Retourne le nombre total d'écritures"""
        # Cette méthode devrait être alimentée par les données réelles
        return self.project_data.get('total_entries', 0)
    
    def _get_analysis_period(self) -> str:
        """Retourne la période d'analyse"""
        return f"01/01/{self.project_data.get('audit_year', 2025)} - 31/12/{self.project_data.get('audit_year', 2025)}"
    
    def _create_risk_distribution_chart(self) -> Optional[Image]:
        """Crée un graphique de répartition des risques"""
        try:
            # Compter les niveaux de risque
            risk_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
            
            for analysis in self.analysis_results:
                risk_level = analysis.get('risk_level', 'low').lower()
                if risk_level == 'low':
                    risk_counts['Low'] += 1
                elif risk_level == 'medium':
                    risk_counts['Medium'] += 1
                elif risk_level == 'high':
                    risk_counts['High'] += 1
                elif risk_level == 'critical':
                    risk_counts['Critical'] += 1
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#059669', '#d97706', '#dc2626', '#7c2d12']
            
            labels = [k for k, v in risk_counts.items() if v > 0]
            sizes = [v for v in risk_counts.values() if v > 0]
            colors_filtered = [colors[i] for i, v in enumerate(risk_counts.values()) if v > 0]
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors_filtered, autopct='%1.1f%%', startangle=90)
                ax.set_title('Répartition des Niveaux de Risque', fontsize=14, fontweight='bold')
                
                # Sauvegarder en mémoire
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close()
                
                # Créer l'objet Image pour ReportLab
                img = Image(img_buffer, width=5*inch, height=3*inch)
                return img
            
        except Exception as e:
            print(f"Erreur lors de la création du graphique: {e}")
        
        return None
    
    def _create_amount_evolution_chart(self) -> Optional[Image]:
        """Crée un graphique d'évolution des montants"""
        try:
            # Données simulées pour l'exemple
            # Dans un vrai cas, ces données viendraient de l'analyse des écritures
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
            debits = [150000, 180000, 165000, 200000, 175000, 190000]
            credits = [145000, 175000, 170000, 195000, 180000, 185000]
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            x = range(len(months))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], debits, width, label='Débits', color='#1e40af', alpha=0.8)
            ax.bar([i + width/2 for i in x], credits, width, label='Crédits', color='#059669', alpha=0.8)
            
            ax.set_xlabel('Mois')
            ax.set_ylabel('Montants (€)')
            ax.set_title('Évolution des Débits et Crédits', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(months)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Sauvegarder en mémoire
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Créer l'objet Image pour ReportLab
            img = Image(img_buffer, width=5*inch, height=3*inch)
            return img
            
        except Exception as e:
            print(f"Erreur lors de la création du graphique d'évolution: {e}")
        
        return None
    
    def generate_executive_summary_only(self, output_path: str) -> Dict[str, Any]:
        """Génère uniquement un résumé exécutif (version courte)"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Titre
            story.append(Paragraph("RÉSUMÉ EXÉCUTIF - AUDIT COMPTABLE", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Informations de base
            info_text = f"""
            <b>Entreprise:</b> {self.project_data.get('company_name', 'N/A')}<br/>
            <b>Exercice:</b> {self.project_data.get('audit_year', 'N/A')}<br/>
            <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}
            """
            story.append(Paragraph(info_text, self.styles['ProfessionalBody']))
            story.append(Spacer(1, 0.2*inch))
            
            # Résumé des résultats
            summary_text = self._generate_executive_summary_text()
            story.append(Paragraph(summary_text, self.styles['ProfessionalBody']))
            
            # Tableau de synthèse
            story.append(Spacer(1, 0.2*inch))
            risk_table = self._create_risk_summary_table()
            story.append(risk_table)
            
            # Recommandations principales
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("<b>Recommandations principales:</b>", self.styles['ProfessionalBody']))
            
            all_recommendations = []
            for analysis in self.analysis_results:
                all_recommendations.extend(analysis.get('recommendations', []))
            
            for i, rec in enumerate(all_recommendations[:5], 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['Recommendation']))
            
            doc.build(story)
            
            return {'success': True, 'file_path': output_path}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

