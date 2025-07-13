# ZenCompta v2.0 - Plateforme d'Audit Comptable Intelligente

## 🚀 Nouvelle Génération d'Audit Comptable

ZenCompta v2.0 révolutionne l'audit comptable avec des fonctionnalités d'intelligence artificielle avancées, une analyse comptable de pointe et une conformité réglementaire automatisée.

## ✨ Fonctionnalités Principales

### 🔍 Analyse Comptable Avancée
- **Détection automatique** du type de fichier comptable
- **Reconnaissance OCR** pour documents scannés
- **Validation croisée** entre différents documents
- **Analyse de cohérence temporelle**
- **Détection d'écritures suspectes**

### 🤖 Intelligence Artificielle
- **Classification automatique** avec modèles ML
- **Prédiction d'anomalies** basée sur l'historique
- **Suggestions automatiques** de corrections
- **Apprentissage adaptatif** selon les normes

### 📋 Conformité Réglementaire
- **Moteur de règles** par norme comptable (IFRS, SYSCOHADA, US GAAP, PCG, SYSCEBNL)- **Check-lists automatiques** selon les normes
- **Validation réglementaire** en temps réel
- **Alertes de non-conformité** intelligentes

### 📊 Tableau de Bord Intelligent
- **Monitoring en temps réel** des processus d'audit
- **Visualisations avancées** des données comptables
- **Alertes prioritaires** et notifications
- **Rapports personnalisables**

## 🏗️ Architecture Technique

### Backend (Flask)
```
backend/
├── src/
│   ├── main.py                 # Point d'entrée principal
│   ├── services/               # Services métier
│   │   ├── file_detector.py    # Détection automatique de fichiers
│   │   ├── ocr_service.py      # Service OCR
│   │   ├── cross_validation_service.py  # Validation croisée
│   │   ├── temporal_analysis_service.py # Analyse temporelle
│   │   ├── suspicious_entries_detector.py # Détection d'anomalies
│   │   ├── ml_classification_service.py # Machine Learning
│   │   ├── compliance_engine.py # Moteur de conformité
│   │   └── compliance_alerts_service.py # Alertes
│   └── static/                 # Fichiers frontend intégrés
└── requirements.txt
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── App.jsx                 # Application principale
│   ├── components/             # Composants React
│   │   ├── Dashboard.jsx       # Tableau de bord principal
│   │   ├── AdvancedAnalysis.jsx # Analyse avancée
│   │   ├── AIFeatures.jsx      # Fonctionnalités IA
│   │   ├── ComplianceCenter.jsx # Centre de conformité
│   │   └── AlertsDashboard.jsx # Tableau de bord alertes
│   └── ui/                     # Composants UI réutilisables
└── package.json
```

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.11+
- Node.js 20+
- pnpm (gestionnaire de paquets)

### Installation Rapide

1. **Cloner le projet**
```bash
git clone <repository-url>
cd zencompta-v2
```

2. **Installation Backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Installation Frontend**
```bash
cd frontend
pnpm install
```

4. **Construction et Intégration**
```bash
# Construire le frontend
cd frontend
pnpm build

# Copier vers le backend
cp -r dist/* ../backend/src/static/
```

5. **Démarrage de l'Application**
```bash
cd backend
python src/main.py
```

L'application sera accessible sur `http://localhost:5000`

## 🎯 Guide d'Utilisation

### 1. Authentification
- Créez un compte ou connectez-vous
- Accédez au dashboard principal

### 2. Analyse Avancée
- Uploadez vos documents comptables
- Sélectionnez le type d'analyse souhaité
- Laissez l'IA analyser et détecter les anomalies

### 3. Intelligence Artificielle
- Configurez les modèles selon vos besoins
- Entraînez les algorithmes avec vos données
- Bénéficiez des suggestions automatiques

### 4. Conformité Réglementaire
- Sélectionnez votre norme comptable
- Activez les validations automatiques
- Suivez les alertes de conformité

### 5. Tableau de Bord
- Monitez vos projets d'audit
- Consultez les alertes prioritaires
- Générez des rapports personnalisés

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Backend
FLASK_ENV=development
DATABASE_URL=sqlite:///zencompta.db
SECRET_KEY=your-secret-key

# IA et ML
ML_MODEL_PATH=./models/
OCR_API_KEY=your-ocr-api-key
```

### Personnalisation des Règles de Conformité
```python
# Exemple de règle personnalisée
compliance_rules = {
    "IFRS": {
        "revenue_recognition": {
            "rule": "check_ifrs15_compliance",
            "severity": "high"
        }
    }
}
```

## 📈 Performance et Scalabilité

- **Traitement parallèle** pour l'analyse de gros volumes
- **Cache intelligent** pour des réponses rapides
- **Optimisation des requêtes** de base de données
- **Architecture modulaire** pour la montée en charge

## 🔒 Sécurité

- **Chiffrement** des données sensibles
- **Authentification** sécurisée
- **Validation** des entrées utilisateur
- **Audit trail** complet des actions

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📞 Support

- **Documentation** : `/docs`
- **Issues** : GitHub Issues
- **Email** : support@zencompta.com

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**ZenCompta v2.0** - L'avenir de l'audit comptable est là ! 🚀

