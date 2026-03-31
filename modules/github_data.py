import requests
import pandas as pd
import base64
import time
import streamlit as st

# =========================
# ⚙️ CONFIG GITHUB
# =========================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "MCMy2026/app-enquete"
FILE_PATH = "data/appels_saisis.csv"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# =========================
# 📥 LECTURE CSV GITHUB
# =========================
def read_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode()

        try:
            df = pd.read_csv(pd.io.common.StringIO(content))
        except:
            df = pd.DataFrame()

        return df, data["sha"]

    return pd.DataFrame(), None


# =========================
# 💾 SAUVEGARDE ROBUSTE
# =========================
def save_data(df):

    max_attempts = 5

    for attempt in range(max_attempts):

        current_df, sha = read_data()

        if sha is None:
            time.sleep(1)
            continue

        # =========================
        # 🔥 STRUCTURE STANDARD
        # =========================
        required_cols = [
            "Date",
            "Enqueteur",
            "Telephone",
            "Commune",
            "Status",
            "Sexe",
            "Age_group",
            "Niveau_cat"
        ]

        # 👉 Si fichier vide
        if current_df.empty:
            current_df = pd.DataFrame(columns=required_cols)

        # 👉 Ajouter colonnes manquantes côté GitHub
        for col in required_cols:
            if col not in current_df.columns:
                current_df[col] = ""

        # 👉 Ajouter colonnes manquantes côté app
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

        # 👉 Forcer ordre propre
        current_df = current_df[required_cols]
        df = df[required_cols]

        # =========================
        # 📦 MERGE DATA
        # =========================
        merged = pd.concat([current_df, df], ignore_index=True)

        # =========================
        # 🚀 PUSH GITHUB
        # =========================
        payload = {
            "message": "Update appels_saisis.csv",
            "content": base64.b64encode(
                merged.to_csv(index=False).encode()
            ).decode(),
            "sha": sha,
        }

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        r = requests.put(url, json=payload, headers=HEADERS)

        if r.status_code in (200, 201):
            return True

        # 👉 conflit GitHub → retry
        if r.status_code == 409:
            time.sleep(1)
            continue

        st.error(f"❌ GitHub ERROR {r.status_code}: {r.json()}")
        return False

    return False


# =========================
# ➕ AJOUT LIGNE SÉCURISÉ
# =========================
def add_row_safe(row):

    df_new = pd.DataFrame([row])

    current_df, _ = read_data()

    if not current_df.empty:

        # =========================
        # 🔒 ANTI DOUBLON JOUR
        # =========================
        today = row["Date"]
        tel = row["Telephone"]

        doublon = current_df[
            (current_df["Date"] == today) &
            (current_df["Telephone"] == tel)
        ]

        if not doublon.empty:
            st.warning("⚠️ Numéro déjà appelé aujourd'hui")
            return False

        # =========================
        # 🔒 LIMITE 2 FOIS / SEMAINE
        # =========================
        nb = current_df[
            current_df["Telephone"] == tel
        ].shape[0]

        if nb >= 2:
            st.warning("⚠️ Numéro déjà appelé 2 fois")
            return False

    # =========================
    # 💾 SAUVEGARDE
    # =========================
    return save_data(df_new)