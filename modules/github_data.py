import requests
import base64
import pandas as pd
import streamlit as st
from io import StringIO
import time

# 🔐 Secrets Streamlit
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]

# 📁 Chemin du CSV dans ton dépôt
FILE_PATH = "data/appels_saisis.csv"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ✅ LECTURE DU CSV DE GITHUB
def read_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        st.error(f"❌ GitHub read error {r.status_code}")
        st.write(r.json())
        st.stop()

    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    df = pd.read_csv(StringIO(content))
    return df, data["sha"]


# ✅ SAUVEGARDE AVEC GESTION SHA & RETRY
def save_data(df, sha, max_retries=3):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    for _ in range(max_retries):
        content = df.to_csv(index=False)
        content_encoded = base64.b64encode(content.encode()).decode()

        payload = {
            "message": "Update appels_saisis.csv",
            "content": content_encoded,
            "sha": sha
        }

        r = requests.put(url, json=payload, headers=HEADERS)

        # ✅ Sauvegarde OK
        if r.status_code in [200, 201]:
            return True

        # 🔁 SHA mismatch → récupérer la nouvelle version et recommencer
        elif r.status_code == 409:
            time.sleep(1)
            df, sha = read_data()

        else:
            st.error(f"❌ GitHub save error {r.status_code}")
            st.write(r.json())
            return False

    return False


# ✅ AJOUT LIGNE AVEC VRAIES COLONNES
def add_row_safe(row):
    df, sha = read_data()

    # ✅ Colonnes dans le bon ordre !
    required_cols = [
        "Date", "Enqueteur", "Telephone", "Commune",
        "Status", "Sexe", "Age_group", "Niveau_cat"
    ]

    new_row = pd.DataFrame([{
        "Date": row[0],
        "Enqueteur": row[1],
        "Telephone": row[2],
        "Commune": row[3],
        "Status": row[4],
        "Sexe": row[5],
        "Age_group": row[6],
        "Niveau_cat": row[7]
    }])

    # ✅ Concat propre
    df = pd.concat([df, new_row], ignore_index=True)

    return save_data(df, sha)