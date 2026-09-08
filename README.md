# NSIA Call Center — Streamlit + SharePoint

Cette version conserve l'interface Streamlit existante et remplace le fichier
Excel local par les listes SharePoint communes de NSIA.

## Architecture retenue

- **Interface** : Streamlit, avec les couleurs et les six pages existantes.
- **Données permanentes** : listes SharePoint `APPELS_CALL_CENTER` et
  `REFERENCES_CALL_CENTER`.
- **Connexion aux données** : Microsoft Graph.
- **Authentification** : comptes Microsoft Entra ID de NSIA.
- **Hébergement** : Streamlit Community Cloud.
- **Accès utilisateur** : lien fixe ajouté au canal Teams.

Le projet ne contient volontairement **aucune donnée cliente, aucun fichier
Excel et aucun secret**.

## Ce qui a changé

Le design et les fonctions de l'application ont été conservés. Les opérations
suivantes utilisent maintenant SharePoint :

- lecture des appels ;
- enregistrement immédiat d'un appel ;
- modification d'un appel sélectionné avec contrôle de concurrence ;
- suppression contrôlée d'appels sélectionnés ;
- lecture des références ;
- ajout et désactivation des opérateurs ;
- alimentation des tableaux de bord et des exports.

Un message de réussite n'est affiché qu'après confirmation de SharePoint. Une
empreinte temporaire empêche un double clic de créer deux fois le même appel
dans une même session.

## Fichiers

- `app.py` : interface Streamlit adaptée ;
- `sharepoint_service.py` : accès isolé à Microsoft Graph ;
- `points_de_vente.py` : référentiel historique des points de vente ;
- `requirements.txt` : dépendances de production ;
- `requirements-dev.txt` : dépendances de test ;
- `.streamlit/config.toml` : thème NSIA ;
- `.streamlit/secrets.example.toml` : modèle sans véritables secrets ;
- `DEPLOIEMENT.md` : procédure de publication et de recette ;
- `AUTORISATIONS_IT.md` : configuration Microsoft et sécurité ;
- `TEAMS.md` : ajout de l'application dans Teams ;
- `SCHEMA_SHAREPOINT.md` : noms et types attendus des colonnes ;
- `tests/` : tests réalisés uniquement avec des données fictives.

## Décision sur les fichiers reçus

| Élément | Décision |
|---|---|
| Interface de `app(2).py` | Conservée à travers la version finale de `app.py` |
| Connexion de `sharepoint.py` | Remplacée par `sharepoint_service.py`, qui renouvelle le jeton et détecte les vrais noms internes des colonnes |
| `app_excel.py` et `BDD_CALL_CENTER(2).xlsm` | À conserver seulement comme sauvegarde locale, hors GitHub et hors Streamlit |
| `points_de_vente(2).py` | Référentiel conservé dans `points_de_vente.py` |
| `.gitignore` et thème | Conservés et renforcés |
| `*.pyc` et `*.bak` | Exclus du déploiement, car ce sont des caches ou des sauvegardes techniques |
| `lancer(2).bat` | Inutile sur Community Cloud ; à garder uniquement pour l'ancienne version locale si nécessaire |

La version finale ne contient donc qu'un seul chemin de production :
`app.py` → `sharepoint_service.py` → listes SharePoint.

## Préparation Microsoft obligatoire

Avant le déploiement, le service informatique doit :

1. créer une inscription d'application Microsoft Entra à locataire unique ;
2. enregistrer l'URL de redirection Streamlit terminant par `/oauth2callback` ;
3. autoriser l'application à accéder uniquement au site
   `https://assurancesnsia.sharepoint.com/sites/NSIACallCenter` ;
4. créer un secret d'application et définir sa date de renouvellement ;
5. remettre à la responsable les trois valeurs nécessaires : identifiant du
   locataire, identifiant de l'application et secret.

Les étapes techniques détaillées sont dans `GUIDE_SERVICE_INFORMATIQUE.md`.

## Déploiement sur Streamlit Community Cloud

1. Créer un dépôt GitHub **privé**, appartenant à NSIA ou à la responsable.
2. Y déposer uniquement les fichiers du présent dossier.
3. Vérifier que `BDD_CALL_CENTER.xlsm`, tout export et `secrets.toml` sont absents.
4. Connecter le dépôt à Streamlit Community Cloud.
5. Choisir `app.py` comme fichier principal.
6. Dans **Settings > Secrets**, copier le contenu de
   `.streamlit/secrets.example.toml`, puis remplacer les valeurs fictives.
7. Déployer et tester avec un compte Microsoft NSIA.
8. Garder l'application privée et inviter uniquement les personnes autorisées,
   sauf décision contraire écrite du service informatique.

Streamlit Community Cloud n'autorise actuellement qu'une application privée à
la fois. Le dépôt et le compte Streamlit doivent appartenir à NSIA ou à la
responsable, jamais exclusivement à la stagiaire.

## Mise en veille

Après environ 12 heures sans visite, Community Cloud peut arrêter temporairement
l'interface. Au prochain accès, un utilisateur autorisé réveille l'application
et attend son redémarrage.

Cette mise en veille ne supprime aucune donnée : après le redémarrage,
l'application recharge automatiquement les appels depuis SharePoint. En
revanche, un formulaire laissé ouvert pendant des heures sans avoir été validé
peut être perdu.

## Test local autorisé

Après installation de Python 3.12 :

```bash
python -m venv .venv
python -m pip install -r requirements.txt
streamlit run app.py
```

Pour un test local contrôlé, copier `secrets.example.toml` vers
`.streamlit/secrets.toml`, compléter les paramètres fournis par l'informatique
et utiliser l'URL de redirection locale déclarée dans Entra.

Pour lancer les tests sans aucune donnée réelle :

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Vérifications avant mise en production

- l'informatique a validé l'hébergement externe aux États-Unis ;
- l'accès Graph est limité au site NSIA Call Center ;
- tous les comptes de test non autorisés sont refusés ;
- création, lecture et suppression sont confirmées dans SharePoint ;
- deux utilisateurs voient les mêmes données après actualisation ;
- aucun secret ou fichier de données n'existe dans GitHub ;
- la responsable possède GitHub, Streamlit, Entra et SharePoint ;
- l'ouverture depuis Teams a été testée.

## Ancienne solution

Ne pas supprimer immédiatement la Power App ou le fichier Excel historique.
Ils servent de sauvegarde pendant la recette. Ils pourront être archivés après
validation complète de Streamlit par la responsable et le service informatique.
