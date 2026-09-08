# Accès à NSIA Call Center depuis Microsoft Teams

## Solution recommandée avec l'authentification Microsoft

L'authentification intégrée de Streamlit n'est pas officiellement prise en
charge dans une application affichée à l'intérieur d'une iframe. Pour éviter
les boucles de connexion :

1. ouvrir le canal Teams **Application call center** ;
2. publier un message épinglé nommé **Ouvrir NSIA Call Center** ;
3. ajouter l'adresse `https://VOTRE-APPLICATION.streamlit.app` ;
4. demander aux utilisateurs d'ouvrir le lien dans leur navigateur ;
5. se connecter avec le compte professionnel Microsoft NSIA.

Cette méthode fonctionne depuis différents ordinateurs et ne dépend d'aucun PC
resté allumé.

## Onglet Teams facultatif

Un onglet « Site web » peut être essayé si la politique Teams de NSIA le
permet. Si la connexion Microsoft ne s'affiche pas correctement, conserver
l'onglet comme page d'information contenant un bouton d'ouverture dans le
navigateur. Ne pas désactiver l'authentification pour forcer l'intégration.

## Mise en veille

Si Streamlit indique que l'application dort, cliquer sur le bouton proposé pour
la réveiller, puis attendre son redémarrage. SharePoint conserve les appels déjà
validés pendant toute la période de veille.
