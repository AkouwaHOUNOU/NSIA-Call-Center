# Guide de déploiement NSIA Call Center

## 1. Microsoft Entra ID
1. Connectez-vous au portail Azure avec un compte administrateur NSIA.
2. Créez une application **Confidentielle** dans **Microsoft Entra ID > Inscriptions d'applications**.
3. Dans **Certificats et secrets**, générez un secret client et notez-le.
4. Sous **Autorisations d'API**, ajoutez l'API **Microsoft Graph** et sélectionnez les autorisations :
   - `Sites.Selected` (application)
   - `User.Read` (délégué)
5. Dans l'onglet **Authentification** :
   - Ajoutez une plateforme de type **Web**.
   - URI de redirection : `https://VOTRE-APPLICATION.streamlit.app/oauth2callback`
6. Notez l'**ID de tenant**, l'**ID d'application** et le **secret client**.

## 2. Dépôt GitHub privé
1. Créez un compte GitHub dédié à NSIA ou utilisez un compte existant propriété de la responsable.
2. Créez un dépôt **privé**.
3. Déposez uniquement les fichiers du projet, sans `BDD_CALL_CENTER.xlsm`, sans `.streamlit/secrets.toml`.
4. Vérifiez que le `.gitignore` est bien présent.

## 3. Streamlit Community Cloud
1. Connectez-vous sur https://share.streamlit.io avec le compte propriétaire.
2. Créez une nouvelle app depuis le dépôt GitHub privé.
3. Branche : `main`, fichier principal : `app.py`, version Python : `3.12`.
4. Dans **Settings > Secrets**, collez la configuration du fichier `.streamlit/secrets.example.toml` avec les vrais identifiants Microsoft Entra.
5. Lancez le déploiement.

## 4. Microsoft Teams
1. Ouvrez le canal **Application call center**.
2. Ajoutez un onglet de type **Website**.
3. Collez l'URL finale `https://VOTRE-APPLICATION.streamlit.app`.
4. Si l'authentification intégrée bloque, utilisez l'option **Ouvrir dans le navigateur**.
