"""
Service d'envoi d'e-mails via Gmail SMTP
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """Service pour l'envoi d'e-mails via Gmail SMTP"""
    
    def __init__(self):
        # Configuration SMTP Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Informations d'authentification (à configurer via variables d'environnement)
        self.sender_email = os.getenv('GMAIL_EMAIL', 'cavenrogroup@gmail.com')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD', 'mjzrvlauixqgajgq')  # Mot de passe d'application Gmail
        self.sender_name = "ZenCompta"
        
        # Templates d'e-mails
        self.templates = {
            'welcome': self._get_welcome_template(),
            'limit_reached': self._get_limit_reached_template(),
            'subscription_activated': self._get_subscription_activated_template(),
            'subscription_expiring': self._get_subscription_expiring_template()
        }
    
    def _get_welcome_template(self) -> Dict[str, str]:
        """Template d'e-mail de bienvenue"""
        return {
            'subject': '🎉 Bienvenue sur ZenCompta - Votre audit comptable révolutionné !',
            'html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .feature { background: white; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
                    .cta { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Bienvenue sur ZenCompta !</h1>
                        <p>L'audit comptable révolutionné par l'Intelligence Artificielle</p>
                    </div>
                    <div class="content">
                        <h2>Félicitations {user_name} !</h2>
                        <p>Vous venez de rejoindre la révolution de l'audit comptable. ZenCompta vous offre des outils d'analyse avancés alimentés par l'IA pour transformer vos processus d'audit.</p>
                        
                        <h3>🎁 Votre offre de bienvenue :</h3>
                        <div class="feature">
                            <strong>3 audits gratuits</strong> pour découvrir toute la puissance de ZenCompta !
                        </div>
                        
                        <h3>🔥 Fonctionnalités révolutionnaires à votre disposition :</h3>
                        
                        <div class="feature">
                            <h4>🤖 Intelligence Artificielle Avancée</h4>
                            <p>• Classification automatique des documents<br>
                            • Détection d'anomalies en temps réel<br>
                            • Suggestions de corrections intelligentes</p>
                        </div>
                        
                        <div class="feature">
                            <h4>📊 Visualisations 3D Spectaculaires</h4>
                            <p>• Graphiques 3D interactifs<br>
                            • Tableaux de bord exécutifs<br>
                            • Cartes de chaleur des risques</p>
                        </div>
                        
                        <div class="feature">
                            <h4>📋 Templates Professionnels</h4>
                            <p>• Rapports personnalisés par secteur<br>
                            • Branding client intégré<br>
                            • Export multi-formats (PDF, Word, Excel, PowerPoint)</p>
                        </div>
                        
                        <div class="feature">
                            <h4>⚖️ Conformité Réglementaire</h4>
                            <p>• Support IFRS, SYSCOHADA, SYSCEBNL<br>
                            • Validation en temps réel<br>
                            • Alertes de non-conformité</p>
                        </div>
                        
                        <a href="http://localhost:5000" class="cta">🚀 Commencer mon premier audit</a>
                        
                        <p><strong>Besoin d'aide ?</strong> Notre équipe est là pour vous accompagner :</p>
                        <p>📧 support@zencompta.com | 📞 +33 1 23 45 67 89</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 ZenCompta - L'audit comptable révolutionné</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_limit_reached_template(self) -> Dict[str, str]:
        """Template d'e-mail pour limite atteinte"""
        return {
            'subject': '🚨 Limite atteinte - Débloquez le potentiel illimité de ZenCompta !',
            'html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .plan { background: white; margin: 20px 0; padding: 25px; border-radius: 10px; border: 2px solid #ddd; position: relative; }
                    .plan.recommended { border-color: #667eea; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }
                    .plan.recommended::before { content: "⭐ RECOMMANDÉ"; position: absolute; top: -10px; left: 20px; background: #667eea; color: white; padding: 5px 15px; border-radius: 15px; font-size: 12px; font-weight: bold; }
                    .price { font-size: 32px; font-weight: bold; color: #667eea; }
                    .savings { background: #2ecc71; color: white; padding: 5px 10px; border-radius: 15px; font-size: 14px; font-weight: bold; }
                    .cta { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; font-weight: bold; }
                    .cta.secondary { background: #2ecc71; }
                    .feature-list { list-style: none; padding: 0; }
                    .feature-list li { padding: 8px 0; border-bottom: 1px solid #eee; }
                    .feature-list li:before { content: "✅ "; color: #2ecc71; font-weight: bold; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 Vous avez atteint votre limite !</h1>
                        <p>Mais ce n'est que le début de votre aventure ZenCompta...</p>
                    </div>
                    <div class="content">
                        <h2>Bonjour {user_name},</h2>
                        <p>Vous avez utilisé vos <strong>3 audits gratuits</strong> ! Nous espérons que vous avez pu découvrir la puissance révolutionnaire de ZenCompta.</p>
                        
                        <p><strong>🎯 Pourquoi nos clients nous choisissent :</strong></p>
                        <ul>
                            <li><strong>Gain de temps de 85%</strong> sur vos audits</li>
                            <li><strong>Précision de 99.7%</strong> grâce à l'IA</li>
                            <li><strong>ROI de 400%</strong> dès le premier mois</li>
                            <li><strong>Satisfaction client de 98%</strong></li>
                        </ul>
                        
                        <h3>🚀 Débloquez votre potentiel avec nos offres exclusives :</h3>
                        
                        <div class="plan recommended">
                            <h3>💎 Abonnement Annuel</h3>
                            <div class="price">200.000 FCFA<span style="font-size: 16px;">/an</span></div>
                            <div class="savings">ÉCONOMISEZ 133.000 FCFA !</div>
                            <ul class="feature-list">
                                <li>Audits illimités pendant 1 an</li>
                                <li>Toutes les fonctionnalités IA avancées</li>
                                <li>Templates professionnels illimités</li>
                                <li>Visualisations 3D premium</li>
                                <li>Support VIP prioritaire</li>
                                <li>Formation personnalisée incluse</li>
                                <li>Mises à jour exclusives en avant-première</li>
                            </ul>
                            <a href="http://localhost:5000/subscribe?plan=yearly" class="cta">💎 Choisir l'Annuel</a>
                        </div>
                        
                        <div class="plan">
                            <h3>⚡ Abonnement Mensuel</h3>
                            <div class="price">30.000 FCFA<span style="font-size: 16px;">/mois</span></div>
                            <ul class="feature-list">
                                <li>Audits illimités pendant 1 mois</li>
                                <li>Toutes les fonctionnalités IA</li>
                                <li>Templates professionnels</li>
                                <li>Visualisations 3D</li>
                                <li>Support prioritaire</li>
                                <li>Rapports personnalisés</li>
                            </ul>
                            <a href="http://localhost:5000/subscribe?plan=monthly" class="cta secondary">⚡ Choisir le Mensuel</a>
                        </div>
                        
                        <h3>🎁 Offre spéciale limitée :</h3>
                        <p style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                            <strong>⏰ Les 100 premiers abonnés annuels bénéficient d'un mois supplémentaire GRATUIT !</strong><br>
                            Plus que <strong>{remaining_spots}</strong> places disponibles.
                        </p>
                        
                        <h3>💬 Ce que disent nos clients :</h3>
                        <blockquote style="background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; font-style: italic;">
                            "ZenCompta a révolutionné notre cabinet. Nous traitons 3x plus de dossiers avec une précision inégalée !"<br>
                            <strong>- Marie Dubois, Expert-Comptable</strong>
                        </blockquote>
                        
                        <p><strong>Questions ? Besoin d'aide ?</strong></p>
                        <p>📧 support@zencompta.com | 📞 +33 1 23 45 67 89</p>
                        <p>💬 Chat en direct disponible 24/7</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 ZenCompta - L'audit comptable révolutionné</p>
                        <p>Vous recevez cet e-mail car vous avez atteint votre limite d'audits gratuits.</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_subscription_activated_template(self) -> Dict[str, str]:
        """Template d'e-mail pour abonnement activé"""
        return {
            'subject': '🎉 Votre abonnement ZenCompta est activé - Audits illimités !',
            'html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .feature { background: white; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #2ecc71; }
                    .cta { background: #2ecc71; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Félicitations !</h1>
                        <p>Votre abonnement {plan_name} est maintenant actif</p>
                    </div>
                    <div class="content">
                        <h2>Bonjour {user_name},</h2>
                        <p>Merci pour votre confiance ! Votre abonnement <strong>{plan_name}</strong> est maintenant actif et vous donne accès à :</p>
                        
                        <div class="feature">
                            <h4>🚀 Audits Illimités</h4>
                            <p>Effectuez autant d'audits que vous le souhaitez jusqu'au {expiry_date}</p>
                        </div>
                        
                        <div class="feature">
                            <h4>🤖 IA Premium</h4>
                            <p>Accès complet à nos algorithmes d'intelligence artificielle les plus avancés</p>
                        </div>
                        
                        <div class="feature">
                            <h4>📊 Visualisations 3D</h4>
                            <p>Créez des rapports visuels époustouflants avec nos graphiques 3D interactifs</p>
                        </div>
                        
                        <div class="feature">
                            <h4>🎨 Templates Premium</h4>
                            <p>Accès à tous nos templates professionnels et personnalisation avancée</p>
                        </div>
                        
                        <a href="http://localhost:5000" class="cta">🚀 Commencer mes audits illimités</a>
                        
                        <p><strong>Support VIP :</strong> En tant qu'abonné, vous bénéficiez d'un support prioritaire !</p>
                        <p>📧 vip@zencompta.com | 📞 +33 1 23 45 67 89</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 ZenCompta - L'audit comptable révolutionné</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_subscription_expiring_template(self) -> Dict[str, str]:
        """Template d'e-mail pour abonnement qui expire"""
        return {
            'subject': '⏰ Votre abonnement ZenCompta expire bientôt - Renouvelez maintenant !',
            'html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                    .cta { background: #e67e22; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⏰ Attention !</h1>
                        <p>Votre abonnement expire dans {days_remaining} jours</p>
                    </div>
                    <div class="content">
                        <h2>Bonjour {user_name},</h2>
                        <p>Votre abonnement <strong>{plan_name}</strong> expire le <strong>{expiry_date}</strong>.</p>
                        
                        <p>Ne perdez pas l'accès à vos fonctionnalités premium !</p>
                        
                        <a href="http://localhost:5000/renew" class="cta">🔄 Renouveler maintenant</a>
                        
                        <p>Besoin d'aide ? Contactez-nous :</p>
                        <p>📧 support@zencompta.com | 📞 +33 1 23 45 67 89</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 ZenCompta - L'audit comptable révolutionné</p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   attachments: Optional[List[str]] = None) -> bool:
        """Envoie un e-mail via Gmail SMTP"""
        try:
            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # Ajouter les pièces jointes si nécessaire
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Créer une connexion sécurisée et envoyer l'e-mail
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            logger.info(f"E-mail envoyé avec succès à {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'e-mail à {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Envoie l'e-mail de bienvenue"""
        template = self.templates['welcome']
        html_content = template['html'].format(user_name=user_name)
        
        return self.send_email(
            to_email=user_email,
            subject=template['subject'],
            html_content=html_content
        )
    
    def send_limit_reached_email(self, user_email: str, user_name: str, remaining_spots: int = 47) -> bool:
        """Envoie l'e-mail de limite atteinte"""
        template = self.templates['limit_reached']
        html_content = template['html'].format(
            user_name=user_name,
            remaining_spots=remaining_spots
        )
        
        return self.send_email(
            to_email=user_email,
            subject=template['subject'],
            html_content=html_content
        )
    
    def send_subscription_activated_email(self, user_email: str, user_name: str, 
                                        plan_name: str, expiry_date: str) -> bool:
        """Envoie l'e-mail d'abonnement activé"""
        template = self.templates['subscription_activated']
        html_content = template['html'].format(
            user_name=user_name,
            plan_name=plan_name,
            expiry_date=expiry_date
        )
        
        return self.send_email(
            to_email=user_email,
            subject=template['subject'],
            html_content=html_content
        )
    
    def send_subscription_expiring_email(self, user_email: str, user_name: str, 
                                       plan_name: str, expiry_date: str, days_remaining: int) -> bool:
        """Envoie l'e-mail d'abonnement qui expire"""
        template = self.templates['subscription_expiring']
        html_content = template['html'].format(
            user_name=user_name,
            plan_name=plan_name,
            expiry_date=expiry_date,
            days_remaining=days_remaining
        )
        
        return self.send_email(
            to_email=user_email,
            subject=template['subject'],
            html_content=html_content
        )

# Instance globale du service d'e-mail
email_service = EmailService()

