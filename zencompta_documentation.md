# Documentation ZenCompta - Application d'Audit Comptable Professionnel

## 🎯 Vue d'ensemble du projet

ZenCompta est une application web professionnelle d'audit comptable développée pour répondre aux besoins des experts-comptables, commissaires aux comptes et auditeurs. L'application offre une interface moderne, conforme aux normes comptables internationales, et conçue pour inspirer confiance aux professionnels exigeants.

## 🏗️ Architecture technique

### Frontend (React)
- **Framework** : React 18 avec Vite
- **Styling** : Tailwind CSS + shadcn/ui
- **Icônes** : Lucide React
- **État** : React Hooks (useState, useEffect)
- **Communication** : Fetch API avec credentials

### Backend (Flask)
- **Framework** : Flask avec SQLAlchemy
- **Base de données** : SQLite
- **Authentification** : Sessions Flask sécurisées
- **API** : REST avec validation des données
- **CORS** : Configuration pour communication frontend-backend

### Structure des dossiers
```
zencompta/                    # Frontend React
├── src/
│   ├── components/
│   │   ├── AuthModal.jsx     # Modal d'authentification
│   │   ├── Dashboard.jsx     # Dashboard utilisateur
│   │   └── AdminDashboard.jsx # Dashboard administrateur
│   ├── App.jsx               # Composant principal
│   └── App.css               # Styles personnalisés

zencompta_backend/            # Backend Flask
├── src/
│   ├── models/
│   │   ├── user.py           # Modèle utilisateur
│   │   └── audit_project.py  # Modèle projet d'audit
│   ├── routes/
│   │   ├── auth.py           # Routes d'authentification
│   │   ├── user.py           # Routes utilisateur
│   │   ├── audit_projects.py # Routes projets d'audit
│   │   └── admin.py          # Routes administration
│   └── main.py               # Application Flask principale
```

## 🔐 Authentification et sécurité

### Système d'authentification
- **Inscription** : Validation email, mot de passe sécurisé
- **Connexion** : Sessions Flask avec cookies sécurisés
- **Rôles** : Utilisateur standard et Administrateur
- **Validation** : Côté client et serveur

### Compte administrateur par défaut
- **Email** : admin@zencompta.com
- **Mot de passe** : Admin123!
- **Rôle** : admin

### Sécurité
- Hachage des mots de passe avec Werkzeug
- Validation des entrées utilisateur
- Protection CSRF via sessions
- Configuration CORS sécurisée

## 📊 Fonctionnalités principales

### 1. Page d'accueil marketing
- **Hero section** impactante avec accroche marketing
- **Services** : Audit des états financiers, rapports analytiques, conformité
- **Avantages** : Qualité professionnelle, collaboration, gain de temps
- **Témoignages** clients authentiques
- **FAQ** détaillée
- **Formulaire de contact** responsive
- **Design** : Thème professionnel bleu marine/blanc

### 2. Dashboard utilisateur
- **Statistiques** : Total projets, en cours, terminés, cette année
- **Gestion des projets** : Création, modification, visualisation
- **Interface** moderne avec cartes interactives
- **Actions rapides** : Nouveau projet, import données, rapports
- **Activité récente** : Suivi des dernières modifications

### 3. Gestion des projets d'audit
- **Création** : Nom entreprise, exercice, norme comptable
- **Normes supportées** : IFRS, SYSCOHADA, US GAAP, PCG, Autre
- **Statuts** : Brouillon, En cours, Terminé
- **Détails** : Vue d'ensemble, données, analyse, rapports
- **Progression** : Suivi étape par étape de l'audit

### 4. Espace administrateur
- **Vue d'ensemble** : Statistiques globales du système
- **Gestion utilisateurs** : Liste, statuts, recherche, filtres
- **Gestion projets** : Vue globale de tous les projets
- **Statistiques** : Utilisateurs actifs, projets par mois, répartition normes
- **Actions admin** : Suspension/activation comptes

## 🗄️ Modèles de données

### Utilisateur (User)
```python
- id: Integer (Primary Key)
- email: String (Unique)
- password_hash: String
- first_name: String
- last_name: String
- company: String
- role: String (user/admin)
- status: String (active/suspended/deleted)
- email_verified: Boolean
- created_at: DateTime
- last_login: DateTime
```

### Projet d'audit (AuditProject)
```python
- id: Integer (Primary Key)
- company_name: String
- audit_year: Integer
- accounting_standard: String
- status: String (draft/in_progress/completed)
- user_id: Integer (Foreign Key)
- audit_data: Text (JSON)
- created_at: DateTime
- updated_at: DateTime
```

## 🚀 Installation et démarrage

### Prérequis
- Node.js 20+
- Python 3.11+
- npm/pnpm

### Frontend (React)
```bash
cd zencompta
pnpm install
pnpm run dev
# Accessible sur http://localhost:5173
```

### Backend (Flask)
```bash
cd zencompta_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install flask flask-sqlalchemy flask-cors
python src/main.py
# Accessible sur http://localhost:5000
```

## 📡 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Profil utilisateur

### Projets d'audit
- `GET /api/audit-projects` - Liste des projets
- `POST /api/audit-projects` - Créer un projet
- `GET /api/audit-projects/{id}` - Détails d'un projet
- `PUT /api/audit-projects/{id}` - Modifier un projet
- `DELETE /api/audit-projects/{id}` - Supprimer un projet

### Administration
- `GET /api/admin/users` - Liste des utilisateurs
- `PUT /api/admin/users/{id}/status` - Modifier statut utilisateur
- `GET /api/admin/projects` - Tous les projets
- `GET /api/admin/stats` - Statistiques système

## 🎨 Design et UX

### Thème professionnel
- **Couleurs principales** : Bleu marine (#1e40af), Blanc, Gris clair
- **Typographie** : Police système moderne et lisible
- **Layout** : Responsive, mobile-first
- **Composants** : shadcn/ui pour cohérence et qualité

### Expérience utilisateur
- **Navigation** intuitive avec breadcrumbs
- **Feedback** visuel (loading, success, erreurs)
- **Accessibilité** : Contraste, focus, navigation clavier
- **Performance** : Chargement optimisé, lazy loading

## 🔮 Fonctionnalités futures

### En développement
- **Import de données** : Excel, CSV, formats comptables
- **Génération de rapports** : PDF interactifs avec graphiques
- **Analyse automatique** : Détection d'anomalies, contrôles
- **Collaboration** : Commentaires, partage, workflow
- **Notifications** : Email, in-app, rappels

### Extensions possibles
- **API publique** pour intégrations tierces
- **Mobile app** React Native
- **IA comptable** pour assistance automatisée
- **Multi-tenant** pour cabinets d'audit
- **Audit trail** complet des modifications

## 📋 Conformité et normes

### Normes comptables supportées
- **IFRS** : International Financial Reporting Standards
- **SYSCOHADA** : Système Comptable Ouest-Africain
- **US GAAP** : Generally Accepted Accounting Principles
- **PCG** : Plan Comptable Général français

### Sécurité et conformité
- **RGPD** : Protection des données personnelles
- **Chiffrement** : Données sensibles protégées
- **Audit trail** : Traçabilité des actions
- **Sauvegarde** : Données sécurisées et récupérables

## 🛠️ Maintenance et support

### Monitoring
- **Logs** : Erreurs et activités tracées
- **Performance** : Métriques de réponse
- **Utilisation** : Statistiques d'usage
- **Santé** : Monitoring système automatique

### Support utilisateur
- **Documentation** : Guides utilisateur détaillés
- **FAQ** : Questions fréquentes intégrées
- **Contact** : Support technique disponible
- **Formation** : Ressources d'apprentissage

## 📞 Contact et support

Pour toute question technique ou demande de support :
- **Email** : contact@zencompta.com
- **Documentation** : Disponible dans l'application
- **Support** : Interface admin intégrée

---

**ZenCompta** - L'audit comptable réinventé pour les professionnels exigeants.
*Version 1.0.0 - Développé avec React, Flask et les meilleures pratiques de sécurité.*

