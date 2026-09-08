# -*- coding: utf-8 -*-
"""
Fusion : appels_export_2026-09-08.xlsx + Listing Emissions Encaissement (65) (1) (1).xlsx
Sortie: C:/Users/houno/Desktop/NSIA_assurance_projet/call_center_app/fusion_emissions_appels.xlsx
"""
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\houno\Downloads")
OUT = Path(r"C:\Users\houno\Desktop\NSIA_assurance_projet\call_center_app\fusion_emissions_appels.xlsx")

APPELS_PATH = BASE / "appels_export_2026-09-08.xlsx"
EMISSIONS_PATH = BASE / "Listing Emissions Encaissement (65) (1) (1).xlsx"

appels = pd.read_excel(APPELS_PATH, sheet_name="Call")
print(f"Appels shape: {appels.shape}")

emissions_raw = pd.read_excel(EMISSIONS_PATH, sheet_name="Listing Emissions Encaissement", header=None)
print(f"Emissions raw shape: {emissions_raw.shape}")

emissions = emissions_raw.iloc[10:].copy()
emissions.columns = [
    'blank1', 'Direction', 'blank2', 'blank3', 'Code_Point_Vente', 'Point_de_vente',
    'Code_Conseiller', 'Code_Gestionnaire', 'blank4', 'Code_branche', 'Produit', 'Code_Categorie',
    'N_Souscripteur', 'Telephone', 'NPolice', 'NAvenant', 'NQuittance', 'Code_Mouvement',
    'Date_Effet', 'Date_Expiration', 'Prime_Nette', 'Prime_Cedee', 'Accessoire', 'Accessoire_Compagnie',
    'Chiffre_Affaire', 'Accessoire_Gestionnaire', 'Accessoire_intermediaire', 'FGA',
    'Montant_Carte', 'Taxe', 'Prime_TTC', 'SATISFACTION', 'RECOMMANDATION', 'COMMENTAIRE',
    'DATES', 'TO', 'CAMPAGNE_ACTIVE'
]
emissions = emissions.reset_index(drop=True)
print(f"Emissions shape apres header: {emissions.shape}")
print(emissions.head(2).to_string(index=False))

appels['Police_norm'] = appels['Police'].astype(str).str.strip().str.upper()
emissions['Police_norm'] = emissions['NPolice'].astype(str).str.strip().str.upper()

appels['Tel_norm'] = appels['telephone'].astype(str).str.strip().str.replace(r'\s+', '', regex=True)
emissions['Tel_norm'] = emissions['Telephone'].astype(str).str.strip().str.replace(r'\s+', '', regex=True)

appels['Date_norm'] = pd.to_datetime(appels['Date'], errors='coerce').dt.date
emissions['Date_norm'] = pd.to_datetime(emissions['DATES'], errors='coerce').dt.date

merged = pd.merge(
    emissions,
    appels,
    on=['Police_norm', 'Tel_norm', 'Date_norm'],
    how='outer',
    indicator=True,
    suffixes=('_emission', '_appel')
)
print("Merge indicator:")
print(merged['_merge'].value_counts())

final = pd.DataFrame()

def pick(row, em_col, ap_col):
    v = row.get(em_col)
    if pd.notna(v) and str(v).strip() not in ('', 'nan', 'None'):
        return v
    return row.get(ap_col)

final['Police'] = merged.apply(lambda r: pick(r, 'NPolice', 'Police'), axis=1)
final['Telephone'] = merged.apply(lambda r: pick(r, 'Telephone', 'telephone'), axis=1)
final['TO'] = merged.apply(lambda r: pick(r, 'TO', 'TO'), axis=1)
final['Date'] = merged.apply(lambda r: pick(r, 'DATES', 'Date'), axis=1)
final['Point_de_vente'] = merged.apply(lambda r: pick(r, 'Point_de_vente', 'Point de vente'), axis=1)
final['Campagne'] = merged.apply(lambda r: pick(r, 'CAMPAGNE_ACTIVE', 'Campagne'), axis=1)
final['Satisfaction'] = merged.apply(lambda r: pick(r, 'SATISFACTION', 'Satisfaction'), axis=1)
final['Recommendation'] = merged.apply(lambda r: pick(r, 'RECOMMANDATION', 'Recommendation'), axis=1)

for c in ['Direction', 'Code_Point_Vente', 'Code_Conseiller', 'Code_Gestionnaire',
          'Code_branche', 'Produit', 'Code_Categorie', 'N_Souscripteur',
          'NAvenant', 'NQuittance', 'Code_Mouvement', 'Date_Effet', 'Date_Expiration',
          'Prime_Nette', 'Prime_Cedee', 'Accessoire', 'Accessoire_Compagnie',
          'Chiffre_Affaire', 'Accessoire_Gestionnaire', 'Accessoire_intermediaire',
          'FGA', 'Montant_Carte', 'Taxe', 'Prime_TTC', 'COMMENTAIRE']:
    final[c] = merged[c]

for c in ['Heure_appel', 'Nom du Client', 'Immatriculation', 'Reception', "Prise d'appel",
          'Produit existant', 'Produit proposé', 'CA', 'Statut', 'Feedback']:
    final[c] = merged[c]

final['SOURCE_FUSION'] = merged['_merge']

OUT.parent.mkdir(parents=True, exist_ok=True)
final.to_excel(OUT, index=False)
print(f"Fusion sauvegardee: {OUT}")
print(f"Shape finale: {final.shape}")
