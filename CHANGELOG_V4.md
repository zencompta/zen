# Changelog - ZenCompta v4.0

## 🚀 Nouvelles Fonctionnalités

### 💰 4.1 Modèle Freemium et Abonnements
- **Offre Freemium** : Les nouveaux utilisateurs bénéficient de 3 audits gratuits pour découvrir la puissance de ZenCompta.
- **Abonnement Mensuel** : 30.000 FCFA/mois pour des audits illimités pendant 1 mois.
- **Abonnement Annuel** : 200.000 FCFA/an pour des audits illimités pendant 1 an.

### 📧 4.2 Communication Automatisée
- **SMTP Gmail intégré** : Envoi d'e-mails automatisés via le SMTP de Gmail.
- **E-mail de bienvenue** : Message automatique envoyé dès l'inscription, présentant les fonctionnalités clés de ZenCompta.
- **Alertes de limite atteinte** : Notification par e-mail lorsque l'utilisateur freemium atteint sa limite d'audits gratuits, avec des arguments percutants pour la souscription.

## ✨ Améliorations
- **Expérience utilisateur** : Parcours d'inscription et de connexion fluidifié.
- **Performance** : Optimisation des appels API pour la gestion des abonnements.

## 🐛 Corrections de Bugs
- Correction de l'import `AdminPanel` vers `AdminDashboard` dans `App.jsx`.
- Correction des chemins d'import des composants UI dans `App.jsx`, `AdvancedVisualizations.jsx` et `ReportGenerator.jsx`.

## 🛠️ Mises à Jour Techniques
- Ajout du modèle `Subscription` pour la gestion des abonnements.
- Création du service `SubscriptionService` pour la logique métier des abonnements.
- Implémentation du service `EmailService` pour l'envoi d'e-mails.
- Mise à jour du `main.py` pour enregistrer le blueprint des abonnements.
- Intégration du composant `SubscriptionManager.jsx` dans le frontend.
- Mise à jour du `Dashboard.jsx` pour inclure la navigation vers la gestion des abonnements.


