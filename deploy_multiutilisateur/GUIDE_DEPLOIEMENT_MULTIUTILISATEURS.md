# Guide complet de déploiement multi-utilisateurs
# NSIA Call Center - Streamlit + SharePoint + Microsoft Entra ID + Teams

## 📋 Vue d'ensemble
Ce guide explique comment déployer l'application NSIA Call Center pour un accès multi-utilisateurs via Microsoft Teams.

### Architecture cible
```
Téléconseillers → Teams → Streamlit Community Cloud → SharePoint Lists
                                                      ↓
                                               Données partagées
```

### Prérequis
- Compte GitHub professionnel NSIA
- Accès au portail Microsoft Entra ID (service informatique NSIA)
- Accès à SharePoint : https://assurancesnsia.sharepoint.com/sites/NSIACallCenter
- Listes SharePoint créées : APPELS_CALL_CENTER et REFERENCES_CALL_CENTER

### Durée estimée
- GitHub + Streamlit Cloud : 30 min
- Microsoft Entra ID : 45 min (par le service informatique)
- Configuration Teams : 10 min

---

## 📦 Étape 1 : Préparer le dossier de déploiement

### Fichiers à déployer
```
deploy_multiutilisateur/
├── app.py                      # Application Streamlit
├── sharepoint_service.py       # Module Microsoft Graph
├── points_de_vente.py          # Références points de vente
├── requirements.txt            # Dépendances Python
├── runtime.txt                 # Version Python 3.12
├── .gitignore                  # Exclusion fichiers sensibles
└── .streamlit/
    └── config.toml             # Thème NSIA
```

### Fichiers à NE JAMAIS déployer
- `.streamlit/secrets.toml` → contient les identifiants Microsoft
- `BDD_CALL_CENTER.xlsm` → fichier Excel local
- Tout fichier avec données clients

### Vérification avant déploiement
```bash
# Vérifier que le dossier ne contient pas de fichiers sensibles
cd deploy_multiutilisateur
find . -name "*.xlsm" -o -name "*.xlsx" -o -name "secrets.toml"
# Doit retourner vide
```

---

## 🐙 Étape 2 : Créer le repository GitHub privé

### 2.1 Créer un compte GitHub NSIA
1. Aller sur https://github.com
2. Cliquer sur **Sign up**
3. Utiliser l'email professionnel NSIA : `@assurancesnsia.com` ou similaire
4. Vérifier l'email

### 2.2 Créer le repository
1. Se connecter à https://github.com
2. Cliquer sur **+** en haut à droite → **New repository**
3. Remplir :
   - **Repository name** : `NSIA-Call-Center`
   - **Description** : `Application Streamlit Call Center NSIA - SharePoint + Entra ID`
   - **Visibility** : ✅ **Private** (très important)
   - ❌ Ne pas cocher "Add a README file"
   - ❌ Ne pas ajouter de .gitignore (on a le nôtre)
   - ❌ Ne pas ajouter de licence
4. Cliquer sur **Create repository**

### 2.3 Installer Git et GitHub Desktop (optionnel mais plus simple)
**Option A : GitHub Desktop (recommandé pour débutants)**
1. Télécharger : https://desktop.github.com
2. Installer et se connecter avec le compte GitHub NSIA
3. File → Clone repository → NSIA-Call-Center
4. Choisir comme destination : `C:\Users\houno\Desktop\NSIA_Call_Center`

**Option B : Ligne de commande Git**
```bash
# Installer Git depuis https://git-scm.com
# Puis dans un terminal :
cd C:\Users\houno\Desktop
git clone https://github.com/VOTRE_USERNAME/NSIA-Call-Center.git
cd NSIA-Call-Center
```

### 2.4 Copier les fichiers
**Si vous avez utilisé GitHub Desktop :**
1. Ouvrir le dossier cloné : `C:\Users\houno\Desktop\NSIA_Call_Center`
2. Copier TOUT le contenu de `deploy_multiutilisateur/` dans ce dossier
3. Vérifier que `.gitignore` est bien présent

**Si vous avez utilisé Git en ligne de commande :**
```bash
cd C:\Users\houno\Desktop\NSIA_Call_Center
cp -r ../NSIA_assurance_projet/call_center_app/deploy_multiutilisateur/* .
cp -r ../NSIA_assurance_projet/call_center_app/deploy_multiutilisateur/.* . 2>/dev/null || true
```

### 2.5 Vérifier avant le commit
```bash
cd C:\Users\houno\Desktop\NSIA_Call_Center

# Vérifier les fichiers
dir

# Vérifier qu'il n'y a pas de fichiers sensibles
dir .streamlit
# Doit afficher seulement config.toml, PAS secrets.toml

# Vérifier .gitignore
type .gitignore
# Doit contenir : *.xlsm, *.xlsx, secrets.toml, .env, __pycache__
```

### 2.6 Premier commit et push

**Avec GitHub Desktop :**
1. Ouvrir GitHub Desktop
2. Sélectionner le repository `NSIA-Call-Center`
3. Dans "Changes", vous devriez voir tous les fichiers
4. **Summary** : `Initial commit - Déploiement NSIA Call Center`
5. **Description** : `Application Streamlit pour call center NSIA avec SharePoint`
6. Cliquer sur **Commit to main**
7. Cliquer sur **Push origin**

**Avec ligne de commande :**
```bash
cd C:\Users\houno\Desktop\NSIA_Call_Center
git add .
git commit -m "Initial commit - Déploiement NSIA Call Center"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/NSIA-Call-Center.git
git push -u origin main
```

### 2.7 Vérifier sur GitHub
1. Aller sur https://github.com/VOTRE_USERNAME/NSIA-Call-Center
2. Vérifier que tous les fichiers sont présents
3. Vérifier que le repository est bien **Private**
4. Vérifier qu'aucun fichier sensible n'est visible

---

## ☁️ Étape 3 : Déployer sur Streamlit Community Cloud

### 3.1 Créer un compte Streamlit
1. Aller sur https://share.streamlit.io
2. Cliquer sur **Sign up**
3. Choisir **Continue with GitHub**
4. Autoriser Streamlit à accéder à votre compte GitHub
5. Vérifier que vous voyez le repository `NSIA-Call-Center`

### 3.2 Créer l'application
1. Cliquer sur **New app** en haut à droite
2. **Repository** : sélectionner `NSIA-Call-Center`
3. **Branch** : `main`
4. **Main file path** : `app.py`
5. **Python version** : `3.12` (ou la version indiquée dans runtime.txt)
6. Cliquer sur **Deploy**

### 3.3 Surveiller le déploiement
- Un écran de progression s'affiche
- Streamlit installe les dépendances depuis requirements.txt
- Cela prend 2-3 minutes la première fois
- Si erreur : vérifier les logs en cliquant sur "Manage app" → "Logs"

### 3.4 Obtenir le lien public
- Une fois déployé, l'URL est : `https://nsia-call-center.streamlit.app`
- Le nom exact dépend de votre username GitHub
- Vous pouvez changer le nom dans Settings → General → App name

### 3.5 Configurer les secrets Streamlit
**IMPORTANT : Ne jamais commit de secrets dans GitHub**

1. Dans Streamlit Cloud, aller sur votre app
2. Cliquer sur **Settings** (icône engrenage)
3. Cliquer sur **Secrets**
4. Coller le contenu suivant :

```toml
[application]
auth_required = true
allowed_email_domain = "assurancesnsia.com"

[auth]
redirect_uri = "https://VOTRE-APP.streamlit.app/oauth2callback"
cookie_secret = "CHANGEZ-CETTE-VALEUR-EN-PRODUCTION"
client_id = "VOTRE_CLIENT_ID"
client_secret = "VOTRE_CLIENT_SECRET"

[sharepoint]
tenant_id = "VOTRE_TENANT_ID"
client_id = "VOTRE_CLIENT_ID"
client_secret = "VOTRE_CLIENT_SECRET"
site_url = "https://assurancesnsia.sharepoint.com/sites/NSIACallCenter"
```

5. Remplacer les valeurs par les identifiants Microsoft Entra
6. Cliquer sur **Save**
7. L'application redémarre automatiquement

### 3.6 Vérifier le déploiement
1. Ouvrir `https://VOTRE-APP.streamlit.app`
2. Vous devriez voir l'interface NSIA Call Center
3. En mode démo : message "Mode démo activé"
4. Une fois Entra configuré : page de connexion Microsoft

---

## 🔐 Étape 4 : Configurer Microsoft Entra ID

> **Cette étape doit être réalisée par le service informatique NSIA**

### 4.1 Accéder au portail Entra ID
1. Aller sur https://entra.microsoft.com
2. Se connecter avec un compte administrateur NSIA
3. Si demandé, choisir l'annuaire NSIA

### 4.2 Créer l'application
1. Menu gauche : **Identité > Applications > Inscriptions d'applications**
2. Cliquer sur **Nouvelle inscription**
3. Remplir :
   - **Nom** : `NSIA Call Center`
   - **Comptes pris en charge** : `Comptes dans cet annuaire organisationnel uniquement`
   - **URI de redirection** : laisser vide pour l'instant
4. Cliquer sur **S'inscrire**

### 4.3 Noter les identifiants
Après création, sur la page de l'application :
- **ID d'application (client)** : copier cette valeur
- **ID de tenant (répertoire)** : disponible dans "Vue d'ensemble"

### 4.4 Créer un secret client
1. Menu gauche : **Certificats et secrets**
2. Cliquer sur **Nouveau secret client**
3. Remplir :
   - **Description** : `Streamlit Call Center - Production`
   - **Expiration** : `12 mois` (ou `24 mois`)
4. Cliquer sur **Ajouter**
5. **COPIEZ IMMÉDIATEMENT LA VALEUR DU SECRET**
   - Elle ne sera plus affichée après fermeture
   - Stockez-la temporairement dans un endroit sécurisé

### 4.5 Ajouter les autorisations API
1. Menu gauche : **Autorisations des API**
2. Cliquer sur **Ajouter une autorisation > Microsoft Graph**
3. Sélectionner **Autorisations d'application** (pas déléguées)
4. Cocher `Sites.Selected`
5. Cliquer sur **Ajouter des autorisations**
6. Dans **Autorisations déléguées**, ajouter : `User.Read`
7. Cliquer sur **Accorder le consentement d'administrateur pour NSIA**

### 4.6 Configurer l'authentification
1. Menu gauche : **Authentification**
2. Cliquer sur **Ajouter une plateforme > Web**
3. URI de redirection : `https://VOTRE-APP.streamlit.app/oauth2callback`
4. Activer :
   - ✅ Jetons d'accès
   - ✅ Jetons d'identité
5. Cliquer sur **Configurer**

### 4.7 Configurer les API permissions pour SharePoint
1. Dans **Autorisations des API**, cliquer sur **Accorder le consentement**
2. Vérifier que `Sites.Selected` est bien accordé

### 4.8 Accorder l'accès au site SharePoint
1. Aller sur https://assurancesnsia.sharepoint.com/sites/NSIACallCenter
2. Cliquer sur **Paramètres > Autorisations du site**
3. Cliquer sur **Autorisations d'application**
4. Ajouter l'application `NSIA Call Center`
5. Accorder les permissions : **Lecture/Écriture** sur les listes

---

## 📊 Étape 5 : Créer les listes SharePoint

### 5.1 Liste APPELS_CALL_CENTER
1. Aller sur https://assurancesnsia.sharepoint.com/sites/NSIACallCenter
2. Cliquer sur **Nouveau > Liste**
3. Nom : `APPELS_CALL_CENTER`
4. Créer les colonnes suivantes :

| Nom de colonne | Type |
|----------------|------|
| Date | Date et heure |
| TO | Texte |
| Nom du Client | Texte |
| telephone | Texte |
| Immatriculation | Texte |
| Police | Texte |
| Campagne | Texte |
| Reception | Texte |
| Prise d'appel | Texte |
| Produit existant | Texte |
| Produit proposé | Texte |
| Feedback | Texte |
| CA | Nombre |
| Point de vente | Texte |
| Heure_appel | Texte |
| Statut | Texte |
| Motif_non_reponse | Texte |
| Commentaire | Texte multiligne |
| Satisfaction | Texte |
| Recommendation | Texte |
| Produit souhaite | Texte |

### 5.2 Liste REFERENCES_CALL_CENTER
1. Créer une nouvelle liste : `REFERENCES_CALL_CENTER`
2. Colonnes :

| Nom de colonne | Type |
|----------------|------|
| Type | Texte (ex: CAMPAGNE, TO, PRODUIT) |
| Valeur | Texte |
| Actif | Oui/Non |

3. Ajouter des valeurs de référence :
   - Type: `CAMPAGNE`, Valeur: `SATURATION`, Actif: `Oui`
   - Type: `CAMPAGNE`, Valeur: `RELANCE`, Actif: `Oui`
   - Type: `CAMPAGNE`, Valeur: `RECUPERATION`, Actif: `Oui`
   - Type: `TO`, Valeur: `Audrey`, Actif: `Oui`
   - Type: `PRODUIT`, Valeur: `AUTOMOBILE`, Actif: `Oui`
   - etc.

---

## 👥 Étape 6 : Ajouter l'application dans Microsoft Teams

### 6.1 Méthode recommandée : Onglet Website
1. Ouvrir Microsoft Teams avec le compte NSIA
2. Aller dans le canal **Application call center**
3. Cliquer sur **+** en haut des onglets
4. Sélectionner **Website**
5. Remplir :
   - **Nom** : `NSIA Call Center`
   - **URL** : `https://VOTRE-APP.streamlit.app`
6. Cliquer sur **Enregistrer**

### 6.2 Si l'authentification bloque dans Teams
**Problème** : Le SSO Microsoft peut ne pas fonctionner dans l'onglet Teams intégré.

**Solution 1 : Ouvrir dans le navigateur**
1. Dans Teams, cliquer sur l'icône ** Ouvrir dans le navigateur** (en haut à droite de l'onglet)
2. L'authentification Microsoft fonctionne correctement dans le navigateur

**Solution 2 : Partager le lien directement**
1. Dans Teams, taper le lien dans le chat : `https://VOTRE-APP.streamlit.app`
2. Les utilisateurs cliquent et s'authentifient dans leur navigateur

### 6.3 Configurer les permissions Teams
1. Dans le canal, cliquer sur **Paramètres du canal**
2. Vérifier que les téléconseillers ont les droits :
   - ✅ Lire et écrire des messages
   - ✅ Ajouter des onglets
3. Ajouter les membres du call center au canal

---

## ✅ Étape 7 : Vérification finale

### Checklist de vérification

**Application déployée :**
- [ ] L'application Streamlit est accessible via le lien public
- [ ] Le thème NSIA s'affiche correctement
- [ ] Les 6 pages sont présentes : Saisie, Tableau de bord, Historique, Opérateurs, Références, Paramètres

**Authentification :**
- [ ] La page de connexion Microsoft s'affiche
- [ ] Un compte NSIA peut se connecter
- [ ] Un compte externe est refusé

**SharePoint :**
- [ ] Les listes APPELS_CALL_CENTER et REFERENCES_CALL_CENTER existent
- [ ] La connexion fonctionne depuis Paramètres > Tester la connexion
- [ ] Les données s'affichent dans Historique

**Multi-utilisateurs :**
- [ ] Deux personnes peuvent se connecter simultanément
- [ ] Les données saisies par une personne sont visibles par l'autre
- [ ] L'application ne plante pas avec 5+ utilisateurs connectés

**Teams :**
- [ ] L'onglet s'affiche dans le canal
- [ ] Le lien fonctionne depuis Teams
- [ ] L'authentification fonctionne dans le navigateur

### Test complet
1. Ouvrir l'application en navigation privée
2. Se connecter avec un compte NSIA
3. Créer un appel test dans Saisie
4. Ouvrir un autre navigateur en navigation privée
5. Se connecter avec un autre compte NSIA
6. Vérifier que l'appel test apparaît dans Historique

---

## 🆘 Dépannage

### Erreur : "Tenant SharePoint non configuré"
**Cause** : Les secrets Streamlit ne sont pas configurés ou incorrects
**Solution** :
1. Aller dans Streamlit Cloud → Settings → Secrets
2. Vérifier que tous les champs sont remplis
3. Vérifier que tenant_id n'est pas "TENANT_ID"
4. Sauvegarder et redémarrer l'application

### Erreur : "Unable to get authority configuration"
**Cause** : L'URI de redirection dans Entra ID ne correspond pas
**Solution** :
1. Vérifier l'URI dans Entra ID : Authentification → Web
2. Elle doit être exactement : `https://VOTRE-APP.streamlit.app/oauth2callback`
3. Pas de slash final, pas de caractère en trop

### Erreur : "Accès refusé SharePoint"
**Cause** : L'application Entra ID n'a pas accès au site SharePoint
**Solution** :
1. Vérifier que Sites.Selected est accordé dans Entra ID
2. Vérifier que l'application est autorisée sur le site SharePoint
3. Attendre 5-10 minutes après les modifications

### Application en veille
**Comportement normal** : Streamlit Community Cloud se met en veille après 12h d'inactivité
**Solution** : Le réveil prend 30-60 secondes, les données ne sont pas perdues

### Données qui ne s'affichent pas
**Cause** : Cache Streamlit
**Solution** :
1. Aller dans Paramètres > Vider le cache
2. Ou attendre le TTL du cache (30-60 secondes)

---

## 📞 Transmission à la responsable

### Documents à fournir
1. Ce guide (`GUIDE_DEPLOIEMENT_MULTIUTILISATEURS.md`)
2. Accès au repository GitHub privé `NSIA-Call-Center`
3. Accès au compte Streamlit Community Cloud
4. Accès à l'application Microsoft Entra ID
5. Lien public de l'application : `https://VOTRE-APP.streamlit.app`

### Points d'attention
- **Ne jamais partager** le fichier `.streamlit/secrets.toml`
- **Ne jamais commit** de secrets dans GitHub
- Les identifiants Microsoft sont gérés par le service informatique
- Le fichier Excel original n'est pas déployé

### Support
- En cas de problème : vérifier les logs Streamlit Cloud
- Pour modifier l'application : modifier le code → commit → push → déploiement automatique
- Pour ajouter des fonctionnalités : contacter le développeur

---

## 📝 Notes importantes

### Sécurité
- Toutes les données transitent par SharePoint (chiffrement Microsoft)
- Authentification centralisée via Entra ID
- Pas de données stockées localement sur les postes utilisateurs
- Accès traçable via les logs Microsoft

### Maintenance
- Les secrets client Entra ID expirent : prévoir le renouvellement avant 12 mois
- Surveiller les logs Streamlit Cloud pour détecter les erreurs
- Sauvegarder régulièrement les listes SharePoint

### Coûts
- Streamlit Community Cloud : **gratuit**
- Microsoft 365 : **déjà payé par NSIA**
- SharePoint : **déjà inclus dans Microsoft 365**
- **Coût total : 0 € supplémentaire**
