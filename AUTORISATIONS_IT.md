# Validation demandée au service informatique NSIA

## Finalité

Autoriser l'application « NSIA Call Center » hébergée sur Streamlit Community
Cloud à lire et mettre à jour uniquement les deux listes du site SharePoint :

`https://assurancesnsia.sharepoint.com/sites/NSIACallCenter`

- `APPELS_CALL_CENTER`
- `REFERENCES_CALL_CENTER`

## Configuration Microsoft Entra demandée

1. Créer une inscription d'application appartenant au tenant NSIA.
2. Nom proposé : `NSIA Call Center Streamlit`.
3. Ajouter une plateforme **Web**.
4. Ajouter l'URI de redirection définitif :
   `https://VOTRE-APPLICATION.streamlit.app/oauth2callback`.
5. Créer un secret client avec une durée et une procédure de renouvellement
   approuvées par NSIA.
6. Autoriser la connexion des comptes du tenant NSIA.
7. Pour Microsoft Graph, privilégier une permission d'application sélectionnée,
   par exemple `Sites.Selected` ou `Lists.SelectedOperations.Selected`.
8. Accorder explicitement le rôle d'écriture uniquement au site ou aux deux
   listes nécessaires.
9. Ne pas accorder `Sites.ReadWrite.All` si une permission sélectionnée suffit.
10. Donner le consentement administrateur selon la procédure interne.

L'authentification OIDC identifie l'utilisateur. L'accès technique à SharePoint
est réalisé par l'application enregistrée ; les autorisations sélectionnées
doivent donc empêcher tout accès à d'autres sites NSIA.

## Informations à remettre au responsable du déploiement

- identifiant du tenant ;
- identifiant de l'application ;
- secret client, transmis par un canal sécurisé ;
- confirmation de l'URI de redirection ;
- confirmation du site ou des listes effectivement autorisés ;
- date d'expiration du secret et propriétaire de son renouvellement.

Ces valeurs ne doivent jamais être envoyées dans GitHub, Teams ou par capture
d'écran. Elles seront placées dans le coffre de secrets de Streamlit.

## Points à valider explicitement

- traitement temporaire des données par un hébergeur externe situé aux
  États-Unis ;
- utilisation d'un dépôt GitHub privé ;
- accès depuis des postes NSIA et depuis Teams ;
- identité de la personne ou du compte NSIA propriétaire du déploiement ;
- règles de conservation, journalisation et export des données.

## Contrôle après configuration

La page **Paramètres** de l'application propose « Tester la connexion
SharePoint ». Ce test confirme seulement l'accès au site et aux deux listes ;
il n'affiche aucune donnée cliente.
