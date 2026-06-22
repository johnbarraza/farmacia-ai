"""
Convierte el catálogo DIGEMID (xlsx) en un índice JSON liviano para búsqueda.
Corre una vez: python data/scripts/build_digemid_index.py
Output: data/digemid_index.json
"""

import pandas as pd
import json
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data" / "digemid_catalogo.xlsx"
OUT  = ROOT / "data" / "digemid_index.json"

def normalize(s: str) -> str:
    s = str(s).upper().strip()
    s = re.sub(r'\s+', ' ', s)
    return s

df = pd.read_excel(XLSX, sheet_name=0, header=6)
df = df[df["Situación"] == "ACT"].copy()

# Campos útiles
df = df[["Cod_Prod", "Nom_Prod", "Concent", "Nom_Form_Farm", "Nom_IFA", "Nom_Rubro"]].copy()
df = df.dropna(subset=["Nom_Prod"])

records = []
for _, row in df.iterrows():
    records.append({
        "id":      int(row["Cod_Prod"]) if pd.notna(row["Cod_Prod"]) else None,
        "nombre":  normalize(row["Nom_Prod"]),
        "concent": str(row["Concent"]).strip() if pd.notna(row["Concent"]) else "",
        "forma":   str(row["Nom_Form_Farm"]).strip() if pd.notna(row["Nom_Form_Farm"]) else "",
        "ifa":     normalize(row["Nom_IFA"]) if pd.notna(row["Nom_IFA"]) else "",
        "rubro":   str(row["Nom_Rubro"]).strip() if pd.notna(row["Nom_Rubro"]) else "",
    })

OUT.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
print(f"✅ {len(records)} productos guardados en {OUT}")
print(f"   Rubros: {df['Nom_Rubro'].value_counts().to_dict()}")
