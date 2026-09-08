# Message pour le service informatique NSIA

Bonjour,

Nous avons déployé une application Streamlit pour le call center NSIA. Elle est actuellement accessible en mode démo à cette adresse :

https://nsia-call-center-skdqbfuhqex7ja6qkmdwqt.streamlit.app

Pour passer en production avec authentification des utilisateurs et données partagées, nous avons besoin de votre aide pour 2 actions :

---

## Action 1 : Microsoft Entra ID

Créer une application confidentielle dans Entra ID :

- Nom : NSIA Call Center
- Comptes : comptes dans cet annuaire organisationnel uniquement
- Autorisations API Microsoft Graph :
  - Sites.Selected (autorisation d'application)
  - User.Read (autorisation déléguée)
- Accorder le consentement administrateur
- Créer un secret client valable 12 mois
- Configurer l'authentification Web avec l'URI de redirection :
  https://nsia-call-center-skdqbfuhqex7ja6qkmdwqt.streamlit.app/oauth2callback

Nous aurons besoin de :
- ID de tenant
- ID d'application (client)
- Secret client

---

## Action 2 : SharePoint

Créer deux listes sur le site https://assurancesnsia.sharepoint.com/sites/NSIACallCenter :

1. APPELS_CALL_CENTER avec les colonnes :
   Date, TO, Nom du Client, telephone, Immatriculation, Police, Campagne, Reception, Prise d'appel, Produit existant, Produit proposé, Feedback, CA, Point de vente, Heure_appel, Statut, Motif_non_reponse, Commentaire, Satisfaction, Recommendation, Produit souhaite

2. REFERENCES_CALL_CENTER avec les colonnes :
   Type, Valeur, Actif

Accorder à l'application NSIA Call Center les permissions Lecture/Écriture sur ces listes.

---

## Documents joints

- GUIDE_DEPLOIEMENT_MULTIUTILISATEURS.md : procédure détaillée
- Lien GitHub : https://github.com/AkouwaHOUNOU/NSIA-Call-Center

Une fois ces éléments configurés, nous pourrons activer l'authentification Microsoft et l'accès depuis Teams.

Merci de me tenir informé quand c'est prêt.

Cordialement,
Akouwa HOUNOU
