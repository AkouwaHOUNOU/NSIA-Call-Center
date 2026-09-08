# Guide de dÃ©ploiement NSIA Call Center
# AccÃ¨s multi-utilisateurs via Teams et navigateur

## Ã‰tape 1 : Microsoft Entra ID (par le service informatique NSIA)

### 1.1 CrÃ©er l'application
1. Se connecter au portail Azure : https://entra.microsoft.com
2. Aller dans **IdentitÃ© > Applications > Inscriptions d'applications**
3. Cliquer sur **Nouvelle inscription**
4. Remplir :
   - **Nom** : `NSIA Call Center`
   - **Comptes pris en charge** : `Comptes dans cet annuaire organisationnel uniquement`
   - **URI de redirection** : laisser vide pour l'instant
5. Cliquer sur **S'inscrire**

### 1.2 CrÃ©er un secret client
1. Dans l'application crÃ©e, aller dans **Certificats et secrets**
2. Cliquer sur **Nouveau secret client**
3. Ajouter une description : `Streamlit Call Center`
4. DurÃ©e : `12 mois`
5. Cliquer sur **Ajouter**
6. **COPIEZ IMMÃ‰DIATEMENT LA VALEUR DU SECRET** (elle ne sera plus affichÃ©e)

### 1.3 Autorisations API
1. Aller dans **Autorisations des API**
2. Cliquer sur **Ajouter une autorisation > Microsoft Graph**
3. SÃ©lectionner **Autorisations d'application**
4. Ajouter : `Sites.Selected` (case Ã  cocher)
5. Cliquer sur **Ajouter des autorisations**
6. Dans **Autorisations dÃ©lÃ©guÃ©es**, ajouter : `User.Read`
7. Cliquer sur **Accorder le consentement d'administrateur**

### 1.4 Authentification
1. Aller dans **Authentification**
2. Cliquer sur **Ajouter une plateforme > Web**
3. URI de redirection : `https://VOTRE-APPLICATION.streamlit.app/oauth2callback`
4. Activer **Jetons d'accÃ¨s** et **Jetons d'identitÃ©**
5. Cliquer sur **Configurer**

### 1.5 Noter les identifiants
- **ID de tenant** : `Azure Active Directory > Vue d'ensemble > ID de tenant`
- **ID d'application (client)** : visible dans la page de l'application
- **Secret client** : copiÃ© Ã  l'Ã©tape 1.2

---

## Ã‰tape 2 : DÃ©pÃ´t GitHub privÃ©

### 2.1 CrÃ©er un compte GitHub NSIA
1. Aller sur https://github.com
2. CrÃ©er un compte avec l'email professionnel NSIA
3. VÃ©rifier l'email

### 2.2 CrÃ©er le dÃ©pÃ´t
1. Cliquer sur **New repository**
2. Nom : `NSIA-Call-Center`
3. VisibilitÃ© : **Private**
4. Cliquer sur **Create repository**

### 2.3 DÃ©poser les fichiers
1. TÃ©lÃ©charger et installer GitHub Desktop : https://desktop.github.com
2. Cloner le dÃ©pÃ´t `NSIA-Call-Center` sur le PC
3. Copier le contenu du dossier `deploy_patronne` dans le dossier clonÃ©
4. **NE PAS COPIER** `.streamlit/secrets.toml` ni `BDD_CALL_CENTER.xlsm`
5. VÃ©rifier que `.gitignore` est bien prÃ©sent
6. Commit et push via GitHub Desktop

---

## Ã‰tape 3 : Streamlit Community Cloud

### 3.1 CrÃ©er le compte
1. Aller sur https://share.streamlit.io
2. Se connecter avec le compte GitHub NSIA
3. Autoriser Streamlit Ã  accÃ©der au dÃ©pÃ´t

### 3.2 DÃ©ployer l'application
1. Cliquer sur **New app**
2. SÃ©lectionner le dÃ©pÃ´t `NSIA-Call-Center`
3. Branche : `main`
4. Fichier principal : `app.py`
5. Version Python : `3.12`
6. Cliquer sur **Deploy**

### 3.3 Configurer les secrets
1. Aller dans **Settings > Secrets**
2. Coller le contenu de `.streamlit/secrets.example.toml`
3. Remplacer les valeurs par les identifiants Microsoft Entra
4. Sauvegarder

### 3.4 Obtenir le lien public
1. Une fois le dÃ©ploiement rÃ©ussi, noter l'URL : `https://nsia-call-center.streamlit.app`
2. Tester l'accÃ¨s avec un compte Microsoft NSIA

---

## Ã‰tape 4 : Microsoft Teams

### 4.1 Ajouter l'onglet
1. Ouvrir Teams avec le compte NSIA
2. Aller dans le canal **Application call center**
3. Cliquer sur **+** en haut des onglets
4. SÃ©lectionner **Website**
5. Nom : `NSIA Call Center`
6. URL : `https://nsia-call-center.streamlit.app`
7. Cliquer sur **Enregistrer**

### 4.2 Si l'authentification bloque
- Dans Teams, l'authentification Microsoft peut ne pas fonctionner en mode intÃ©grÃ©
- Solution : utiliser l'option **Ouvrir dans le navigateur** depuis Teams
- Ou partager le lien directement : `https://nsia-call-center.streamlit.app`

---

## VÃ©rification finale

### Test 1 : AccÃ¨s utilisateur
- Se connecter avec un compte Microsoft NSIA
- VÃ©rifier que l'authentification fonctionne
- CrÃ©er un appel test dans SharePoint
- VÃ©rifier que l'appel apparaÃ®t dans Historique

### Test 2 : AccÃ¨s multi-utilisateurs
- Ouvrir l'application depuis deux navigateurs diffÃ©rents
- Se connecter avec deux comptes diffÃ©rents
- VÃ©rifier que les donnÃ©es sont partagÃ©es

### Test 3 : Teams
- Ouvrir l'application depuis le canal Teams
- VÃ©rifier l'affichage et les fonctionnalitÃ©s

---

## DÃ©pannage

### Erreur d'authentification Microsoft
- VÃ©rifier que l'URI de redirection correspond exactement
- VÃ©rifier que le consentement admin a Ã©tÃ© accordÃ©
- Attendre quelques minutes aprÃ¨s la configuration Entra

### Erreur SharePoint
- VÃ©rifier que les listes existent avec les bons noms
- VÃ©rifier que `Sites.Selected` est bien accordÃ©
- Tester la connexion dans ParamÃ¨tres > Tester la connexion

### Application en veille
- Streamlit Community Cloud se met en veille aprÃ¨s ~12h d'inactivitÃ©
- Le rÃ©veil prend 30-60 secondes
- Les donnÃ©es ne sont pas perdues

---

## Transmission Ã  la responsable

### Documents Ã  fournir
1. Ce guide (`GUIDE_DEPLOIEMENT.md`)
2. AccÃ¨s au dÃ©pÃ´t GitHub privÃ©
3. AccÃ¨s au compte Streamlit
4. AccÃ¨s Ã  l'application Microsoft Entra

### Points d'attention
- Le fichier `secrets.toml` ne doit jamais Ãªtre partagÃ©
- Le fichier Excel original n'est pas dÃ©ployÃ©
- Les identifiants Microsoft sont gÃ©rÃ©s par le service informatique
