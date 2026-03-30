import requests
import base64
import pandas as pd
import streamlit as st
from io import StringIO
import time

TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]

# ⚠️ Vérifie ce chemin selon ton repo
FILE_PATH = "data/appels_saisis.csv"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 📥 LECTURE
def read_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        st.error(f"❌ GitHub erreur {r.status_code}")
        st.write(r.json())
        st.stop()

    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    df = pd.read_csv(StringIO(content))

    return df, data["sha"]

# 💾 SAUVEGARDE
def save_data(df, sha, max_retries=3):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    for _ in range(max_retries):
        content = df.to_csv(index=False)
        content_encoded = base64.b64encode(content.encode()).decode()

        payload = {
            "message": "Update data",
            "content": content_encoded,
            "sha": sha
        }

        r = requests.put(url, json=payload, headers=HEADERS)

        if r.status_code in [200, 201]:
            return True

        elif r.status_code == 409:
            time.sleep(1)
            df, sha = read_data()

        else:
            st.error(f"❌ GitHub save error {r.status_code}")
            st.write(r.json())
            return False

    return False

# ➕ AJOUT LIGNE (CORRIGÉ)
def add_row_safe(row):
    df, sha = read_data()

    # convertir en DataFrame
    new_row = pd.DataFrame([row])

    # garantir colonnes
    required_cols = [
        "Date","Enqueteur","Telephone","Commune",
        "Status","Sexe","Age_group","Niveau_cat"
    ]

    for col in required_cols:
        if col not in new_row.columns:
            new_row[col] = None

    # aligner colonnes
    df = pd.concat([df, new_row], ignore_index=True)

    return save_data(df, sha)