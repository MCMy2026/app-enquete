import requests
import base64
import pandas as pd
from io import StringIO
import streamlit as st
import time

TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = "data/appels_saisis.csv"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ✅ Lecture toujours à jour
def read_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        st.error(f"Erreur lecture GitHub {r.status_code}")
        return pd.DataFrame(), None
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return pd.read_csv(StringIO(content)), data["sha"]

# ✅ Sauvegarde robuste avec mise à jour SHA
def save_data(df):
    max_attempts = 5

    for attempt in range(max_attempts):
        # Lire dernière version + SHA
        current_df, sha = read_data()
        if sha is None:
            time.sleep(1)
            continue

        # Fusionner l'ancien avec le nouveau
        df = df[current_df.columns]
        merged = pd.concat([current_df, df], ignore_index=True)
        

        payload = {
            "message": "Update appels_saisis.csv",
            "content": base64.b64encode(merged.to_csv(index=False).encode()).decode(),
            "sha": sha,
        }

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        r = requests.put(url, json=payload, headers=HEADERS)

        # ✅ Succès
        if r.status_code in (200, 201):
            return True

        # ⚠️ Conflit SHA → attendre et réessayer
        if r.status_code == 409:
            time.sleep(1)
            continue

        st.error(f"GitHub ERROR {r.status_code}: {r.json()}")
        return False

    return False

# ✅ Ajout ligne qui ne peut PAS échouer (rejoue automatiquement)
def add_row_safe(row):
    df = pd.DataFrame([{
        "Date": row[0],
        "Enqueteur": row[1],
        "Telephone": row[2],
        "Commune": row[3],
        "Status": row[4],
        "Sexe": row[5],
        "Age_group": row[6],
        "Niveau_cat": row[7]
    }])

    return save_data(df)
