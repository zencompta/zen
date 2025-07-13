# ZenCompta v4.0 - Plateforme d'Audit Comptable Freemium

Bienvenue dans ZenCompta v4.0, la solution d'audit comptable qui révolutionne la gestion financière des entreprises. Cette version introduit un modèle freemium innovant, permettant aux utilisateurs de découvrir la puissance de nos outils avant de s'abonner à des plans illimités. De plus, nous avons intégré un système de communication automatisé par e-mail pour une expérience utilisateur fluide et engageante.

## 🚀 Nouvelles Fonctionnalités

### 💰 4.1 Modèle Freemium et Abonnements

ZenCompta v4.0 offre une flexibilité inégalée avec son modèle freemium et ses options d'abonnement adaptées à tous les besoins :

-   **Offre Freemium** : Les nouveaux utilisateurs bénéficient de **3 audits gratuits**. C'est l'opportunité parfaite de tester nos fonctionnalités avancées, de découvrir la précision de nos analyses et de constater par vous-même la valeur ajoutée de ZenCompta, sans aucun engagement financier initial.

-   **Abonnement Mensuel** : Pour seulement **30.000 FCFA par mois**, accédez à des **audits illimités** pendant 30 jours. Idéal pour les projets ponctuels ou pour une flexibilité maximale. C'est l'investissement le plus rentable pour une productivité continue.

-   **Abonnement Annuel** : Optez pour la tranquillité d'esprit avec notre abonnement annuel à **200.000 FCFA par an**. Profitez d'audits illimités pendant 12 mois, réalisant des économies substantielles par rapport à l'abonnement mensuel. C'est la solution ultime pour les professionnels exigeants qui visent l'excellence sur le long terme.

#### Pourquoi choisir ZenCompta Premium ?

*   **Libérez votre potentiel** : Dites adieu aux contraintes et réalisez autant d'audits que nécessaire. Votre productivité ne sera plus jamais limitée.
*   **Maîtrise budgétaire** : Des tarifs clairs et compétitifs, sans frais cachés. Choisissez l'option qui correspond le mieux à votre flux de travail et à votre budget.
*   **Accès exclusif** : Bénéficiez en priorité des futures mises à jour, des fonctionnalités premium et d'un support client dédié, vous assurant une longueur d'avance sur la concurrence.
*   **Investissement intelligent** : Chaque audit illimité est un pas de plus vers l'optimisation de vos finances. Ne laissez pas les opportunités vous échapper.

### 📧 4.2 Communication Automatisée

Pour une expérience utilisateur sans faille, ZenCompta v4.0 intègre un système de communication par e-mail intelligent :

-   **SMTP Gmail intégré** : Nous utilisons le service SMTP sécurisé de Gmail pour garantir la fiabilité et la délivrabilité de tous nos messages automatisés.

-   **E-mail de bienvenue personnalisé** : Dès votre inscription, recevez un e-mail chaleureux qui vous guide à travers les fonctionnalités clés de ZenCompta et vous aide à démarrer rapidement vos premiers audits gratuits.

-   **Alertes de limite atteinte intelligentes** : Lorsque vous approchez ou atteignez la limite de vos 3 audits gratuits, un e-mail vous est envoyé. Ce message n'est pas qu'une simple alerte ; il est conçu pour vous montrer la valeur inestimable de nos abonnements, avec des arguments percutants qui vous inciteront à passer au niveau supérieur et à débloquer un potentiel illimité.

## 🛠️ Installation et Démarrage

Pour installer et démarrer ZenCompta v4.0, suivez les étapes ci-dessous :

### Prérequis

-   Python 3.x
-   Node.js et pnpm
-   Accès à un compte Gmail pour le SMTP (avec mot de passe d'application généré)

### Backend (Flask)

1.  Naviguez vers le répertoire `backend` :
    ```bash
    cd backend
    ```
2.  Créez un environnement virtuel et activez-le :
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Installez les dépendances Python :
    ```bash
    pip install -r requirements.txt
    ```
4.  Configurez vos identifiants Gmail SMTP dans `src/services/email_service.py` (remplacez `YOUR_GMAIL_EMAIL` et `YOUR_GMAIL_APP_PASSWORD`) :
    ```python
    # Informations d'authentification Gmail
    GMAIL_EMAIL = 'cavenrogroup@gmail.com'
    GMAIL_APP_PASSWORD = 'mjzrvlauixqgajgq'
    ```
5.  Démarrez le serveur Flask :
    ```bash
    python3 src/main.py
    ```
    Le backend sera accessible sur `http://localhost:5000`.

### Frontend (React)

1.  Naviguez vers le répertoire `frontend` :
    ```bash
    cd frontend
    ```
2.  Installez les dépendances Node.js avec pnpm :
    ```bash
    pnpm install
    ```
3.  Construisez l'application React pour la production :
    ```bash
    pnpm build
    ```
    Les fichiers de production seront générés dans le répertoire `dist`.

### Intégration Frontend-Backend

Les fichiers de production du frontend (`dist` du répertoire `frontend`) doivent être copiés dans le répertoire `src/static` du backend pour que le serveur Flask puisse les servir.

1.  Assurez-vous que le backend est arrêté.
2.  Copiez les fichiers :
    ```bash
    cp -r frontend/dist/* backend/src/static/
    ```
3.  Redémarrez le serveur Flask comme indiqué ci-dessus. L'application complète sera alors accessible via `http://localhost:5000`.

## 🤝 Contribution

Nous accueillons les contributions ! Si vous souhaitez améliorer ZenCompta, n'hésitez pas à soumettre des pull requests ou à signaler des problèmes.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

