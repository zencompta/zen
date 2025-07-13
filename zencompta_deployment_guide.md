# Guide de Déploiement de ZenCompta en Production

Ce guide détaille les étapes et les meilleures pratiques pour déployer l'application ZenCompta (frontend React et backend Flask) sur un serveur de production.

## 1. Prérequis du Serveur

Avant de commencer, assurez-vous que votre serveur de production dispose des éléments suivants :

- **Système d'exploitation** : Linux (Ubuntu, CentOS, Debian, etc.) est recommandé.
- **Serveur Web** : Nginx ou Apache pour servir le frontend statique et agir comme proxy inverse pour le backend.
- **Base de données** : PostgreSQL est fortement recommandé pour la production (SQLite est pour le développement).
- **Environnement d'exécution** :
    - Node.js (pour le build du frontend)
    - Python 3.11+ (pour le backend Flask)
    - `pip` et `npm` (ou `pnpm`)
- **Outils** : `git`, `venv` (pour Python), `pm2` (pour la gestion des processus Node.js) ou `Gunicorn`/`uWSGI` (pour Flask).

## 2. Déploiement du Backend (Flask)

Le backend Flask doit être configuré pour la production, en utilisant un serveur WSGI (Web Server Gateway Interface) comme Gunicorn ou uWSGI, et une base de données robuste comme PostgreSQL.

### 2.1. Configuration de la Base de Données (PostgreSQL)

1. **Installer PostgreSQL** sur votre serveur :
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```
2. **Créer un utilisateur et une base de données** pour ZenCompta :
   ```bash
   sudo -u postgres psql
   # Dans le shell psql:
   CREATE USER zencompta_user WITH PASSWORD 'votre_mot_de_passe_fort';
   CREATE DATABASE zencompta_db OWNER zencompta_user;
   \q
   ```
3. **Mettre à jour la configuration Flask** : Modifiez `zencompta_backend/src/main.py` pour utiliser PostgreSQL. Vous devrez installer `psycopg2-binary`.
   ```python
   # zencompta_backend/src/main.py
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zencompta_user:votre_mot_de_passe_fort@localhost/zencompta_db'
   ```
   **Note** : Remplacez `localhost` par l'adresse IP de votre serveur de base de données si elle est séparée.

### 2.2. Préparation de l'Environnement Python

1. **Cloner le dépôt** (ou transférer les fichiers) sur votre serveur :
   ```bash
   git clone <URL_DE_VOTRE_DEPOT_BACKEND> /var/www/zencompta_backend
   cd /var/www/zencompta_backend
   ```
2. **Créer et activer un environnement virtuel** :
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```
3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt # Créez ce fichier avec `pip freeze > requirements.txt` en dev
   pip install gunicorn psycopg2-binary
   ```
4. **Initialiser la base de données** (créer les tables) :
   ```bash
   python -c 


'''python
from src.main import app, db
with app.app_context():
    db.create_all()
'''
   ```

### 2.3. Utilisation de Gunicorn

Gunicorn est un serveur WSGI Python qui sert d'interface entre votre application Flask et le serveur web (Nginx).

1. **Tester Gunicorn** :
   ```bash
   gunicorn --bind 0.0.0.0:5000 src.main:app
   ```
   Vous devriez voir votre application Flask accessible sur le port 5000.

2. **Créer un service Systemd pour Gunicorn** (pour une gestion automatique au démarrage) :
   Créez un fichier `/etc/systemd/system/zencompta_backend.service` :
   ```ini
   [Unit]
   Description=Gunicorn instance for ZenCompta Backend
   After=network.target

   [Service]
   User=www-data # Ou un autre utilisateur système dédié
   Group=www-data
   WorkingDirectory=/var/www/zencompta_backend
   ExecStart=/var/www/zencompta_backend/venv/bin/gunicorn --workers 3 --bind unix:/var/www/zencompta_backend/zencompta_backend.sock src.main:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   - `User` et `Group` : Assurez-vous que l'utilisateur `www-data` (ou celui que vous choisissez) a les permissions nécessaires sur le dossier du projet.
   - `ExecStart` : Spécifie la commande Gunicorn. `--workers 3` est un bon point de départ (ajustez selon le nombre de cœurs CPU). Nous utilisons un socket Unix pour une meilleure performance avec Nginx.

3. **Activer et démarrer le service** :
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start zencompta_backend
   sudo systemctl enable zencompta_backend
   ```
   Vérifiez le statut avec `sudo systemctl status zencompta_backend`.

### 2.4. Configuration Nginx pour le Backend

Nginx agira comme un proxy inverse, transmettant les requêtes du port 80/443 à Gunicorn.

1. **Créer un fichier de configuration Nginx** pour votre site :
   Créez un fichier `/etc/nginx/sites-available/zencompta_backend` :
   ```nginx
   server {
       listen 80;
       server_name api.votre-domaine.com; # Remplacez par votre sous-domaine API

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/zencompta_backend/zencompta_backend.sock;
       }
   }
   ```
2. **Activer la configuration** :
   ```bash
   sudo ln -s /etc/nginx/sites-available/zencompta_backend /etc/nginx/sites-enabled
   sudo nginx -t # Tester la configuration
   sudo systemctl restart nginx
   ```

## 3. Déploiement du Frontend (React)

Le frontend React est une application statique qui peut être servie directement par Nginx.

### 3.1. Build de l'Application React

1. **Cloner le dépôt** (ou transférer les fichiers) sur votre serveur :
   ```bash
   git clone <URL_DE_VOTRE_DEPOT_FRONTEND> /var/www/zencompta_frontend
   cd /var/www/zencompta_frontend
   ```
2. **Installer les dépendances et construire l'application** :
   ```bash
   npm install # ou pnpm install
   npm run build # Cela créera un dossier `dist` ou `build`
   ```
   Le dossier `dist` (ou `build`) contient tous les fichiers statiques optimisés pour la production.

### 3.2. Configuration Nginx pour le Frontend

Nginx servira les fichiers statiques du frontend.

1. **Créer un fichier de configuration Nginx** pour votre site :
   Créez un fichier `/etc/nginx/sites-available/zencompta_frontend` :
   ```nginx
   server {
       listen 80;
       server_name www.votre-domaine.com votre-domaine.com; # Remplacez par votre domaine

       root /var/www/zencompta_frontend/dist; # Chemin vers votre dossier de build
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```
2. **Activer la configuration** :
   ```bash
   sudo ln -s /etc/nginx/sites-available/zencompta_frontend /etc/nginx/sites-enabled
   sudo nginx -t # Tester la configuration
   sudo systemctl restart nginx
   ```

## 4. Configuration HTTPS (SSL/TLS)

Il est crucial de sécuriser votre application avec HTTPS. Let's Encrypt offre des certificats SSL gratuits et faciles à installer avec Certbot.

1. **Installer Certbot** :
   ```bash
   sudo snap install core; sudo snap refresh core
   sudo snap install --classic certbot
   sudo ln -s /snap/bin/certbot /usr/bin/certbot
   ```
2. **Obtenir et installer les certificats** pour vos domaines (frontend et backend API) :
   ```bash
   sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com -d api.votre-domaine.com
   ```
   Suivez les instructions. Certbot modifiera automatiquement vos configurations Nginx pour inclure les certificats et rediriger le trafic HTTP vers HTTPS.

3. **Vérifier le renouvellement automatique** :
   ```bash
   sudo systemctl status snap.certbot.renew.service
   ```

## 5. Sécurité et Maintenance

### 5.1. Sécurité
- **Firewall** : Configurez un firewall (ex: UFW) pour n'autoriser que les ports nécessaires (80, 443, 22).
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```
- **Mots de passe forts** : Utilisez des mots de passe complexes pour tous les comptes système et de base de données.
- **Mises à jour régulières** : Maintenez votre système d'exploitation, Python, Node.js et toutes les dépendances à jour.
- **Variables d'environnement** : Ne stockez jamais d'informations sensibles (clés secrètes, mots de passe DB) directement dans le code. Utilisez des variables d'environnement ou un gestionnaire de secrets.
  - Pour Flask, vous pouvez utiliser `python-dotenv` en développement et des variables d'environnement système en production (`export SECRET_KEY='...'`).
  - Pour Gunicorn, vous pouvez les définir dans le fichier de service Systemd (`Environment=



### 5.2. Maintenance et Monitoring
- **Logs** : Configurez la rotation des logs pour Nginx, Gunicorn et votre application Flask afin d'éviter que les fichiers de log ne remplissent le disque.
- **Monitoring** : Utilisez des outils de monitoring (ex: Prometheus, Grafana, Datadog) pour surveiller la performance du serveur, l'utilisation des ressources, et les erreurs de l'application.
- **Sauvegardes** : Mettez en place des sauvegardes régulières de votre base de données PostgreSQL et de vos fichiers d'application.
- **Déploiements automatisés** : Pour les mises à jour futures, envisagez d'utiliser des outils d'intégration continue/déploiement continu (CI/CD) comme GitLab CI/CD, GitHub Actions, ou Jenkins pour automatiser le processus de build et de déploiement.

## 6. Considérations supplémentaires

- **Gestion des secrets** : Pour les environnements de production complexes, utilisez un gestionnaire de secrets dédié (ex: HashiCorp Vault, AWS Secrets Manager) plutôt que des variables d'environnement directes.
- **Mise à l'échelle** : Si votre application gagne en popularité, vous devrez envisager des stratégies de mise à l'échelle, comme l'ajout de plus de workers Gunicorn, l'utilisation de plusieurs serveurs (load balancing), ou l'adoption de services cloud managés (ex: AWS Elastic Beanstalk, Google App Engine).
- **Tests** : Assurez-vous d'avoir une suite de tests robustes (unitaires, d'intégration, end-to-end) et exécutez-les avant chaque déploiement en production.

Ce guide fournit une base solide pour le déploiement de ZenCompta. Adaptez-le à vos besoins spécifiques et à l'infrastructure de votre serveur.


