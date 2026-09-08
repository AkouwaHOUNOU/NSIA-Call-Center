# Schéma SharePoint attendu

Les noms ci-dessous sont les **noms affichés**. L'application détecte elle-même
les noms internes SharePoint, notamment `Title` lorsque cette colonne a été
renommée en `Nom du Client` ou en `Valeur`.

## Liste `APPELS_CALL_CENTER`

| Nom affiché | Type recommandé |
|---|---|
| Nom du Client | Une ligne de texte ; colonne `Title` renommée ; non obligatoire si les appels sans nom sont autorisés |
| Date Appel | Date et heure, affichage date uniquement |
| TO | Une ligne de texte |
| Numero de telephone | Une ligne de texte |
| Immatriculation | Une ligne de texte |
| Police | Une ligne de texte |
| Campagne | Une ligne de texte |
| Reception | Une ligne de texte |
| Prise Appel | Une ligne de texte |
| Produit Existant | Une ligne de texte |
| Produit Propose | Une ligne de texte |
| Produit Souhaite | Une ligne de texte |
| Point de Vente | Une ligne de texte |
| Heure Appel | Une ligne de texte, format `HH:MM` |
| Statut | Une ligne de texte |
| Motif Non Reponse | Une ligne de texte |
| Satisfaction | Une ligne de texte |
| Recommendation | Une ligne de texte |
| Feedback | Une ligne de texte |
| Commentaire | Plusieurs lignes de texte |
| CA | Nombre ou devise, sans valeur négative |

## Liste `REFERENCES_CALL_CENTER`

| Nom affiché | Type recommandé |
|---|---|
| Valeur | Une ligne de texte ; colonne `Title` renommée |
| TypeReference | Une ligne de texte |
| Actif | Oui/Non, valeur par défaut Oui |
| Ordre | Nombre entier, facultatif |

Types de référence reconnus par l'application : `CAMPAGNE`, `TO`, `PRODUIT`,
`RECEPTION`, `PRISE_APPEL`, `RESEAU`, `FEEDBACK` et `POINT_DE_VENTE`.

La page **Paramètres** contient un bouton de test qui vérifie la présence des
deux listes et de toutes ces colonnes sans afficher les données clientes.
