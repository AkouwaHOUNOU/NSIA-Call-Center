# Déploiement sur Streamlit Community Cloud

Cette procédure doit être réalisée avec des comptes appartenant à NSIA ou à la
responsable de l'application.

## 1. Validation préalable

Ne pas déployer avec de véritables données avant validation du document
`AUTORISATIONS_IT.md` par le service informatique.

## 2. Créer le dépôt privé

1. Créer un dépôt GitHub privé, par exemple `nsia-call-center`.
2. Donner à la responsable les droits d'administration.
3. Ajouter uniquement les fichiers du présent dossier.
4. Vérifier avant chaque envoi que les fichiers suivants sont absents :
   classeurs Excel, CSV, exports, `secrets.toml`, `.env` et données clientes.
5. Activer si possible l'analyse des secrets proposée par GitHub.

## 3. Préparer Microsoft Entra

Le service informatique réalise les opérations décrites dans
`AUTORISATIONS_IT.md`. L'URI de redirection doit se terminer exactement par
`/oauth2callback`.

## 4. Déployer l'application

1. Se connecter à `share.streamlit.io` avec le compte retenu par NSIA.
2. Autoriser l'accès au dépôt GitHub privé.
3. Choisir le dépôt, la branche principale et `app.py` comme fichier d'entrée.
4. Choisir Python 3.12 si cette version est proposée.
5. Ouvrir **Advanced settings / Secrets**.
6. Copier le contenu de `.streamlit/secrets.example.toml`.
7. Remplacer toutes les valeurs fictives par les valeurs remises par le service
   informatique.
8. Vérifier que `auth_required = true`.
9. Déployer et conserver l'adresse `https://...streamlit.app`.
10. Reporter cette adresse exacte dans l'URI de redirection Entra, puis
    redémarrer l'application si nécessaire.

## 5. Recette avec données fictives

1. Se connecter avec un compte Microsoft NSIA autorisé.
2. Ouvrir **Paramètres** et tester la connexion SharePoint.
3. Créer un appel portant explicitement le nom `CLIENT TEST A SUPPRIMER`.
4. Vérifier sa présence dans SharePoint et dans l'historique.
5. Vérifier son apparition dans le tableau de bord.
6. Supprimer l'appel fictif depuis l'historique.
7. Vérifier sa disparition dans SharePoint.
8. Redémarrer l'application et confirmer que les données restantes se
   rechargent correctement.

## 6. Passage de relais

Avant le départ de la stagiaire, vérifier que la responsable peut :

- administrer le dépôt privé ;
- ouvrir l'espace Streamlit ;
- consulter les journaux techniques ;
- redémarrer l'application ;
- mettre à jour les secrets ;
- contacter le propriétaire NSIA de l'inscription Microsoft Entra ;
- connaître la date d'expiration du secret client.

## Mise en veille

Après environ 12 heures sans trafic, Community Cloud peut mettre l'application
en veille. Un utilisateur autorisé peut la réveiller lors de sa prochaine
visite. Les données validées restent dans SharePoint ; aucun ordinateur local
ne doit rester allumé.
