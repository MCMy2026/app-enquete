import requests
import pandas as pd
import base64
import time
import streamlit as st
from io import StringIO

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
            df = pd.read_csv(StringIO(content))
        except Exception:
            df = pd.DataFrame()

        return df, data["sha"]

    # fichier inexistant
    if r.status_code == 404:
        return pd.DataFrame(), None

    st.error(f"❌ Lecture GitHub impossible ({r.status_code})")
    return pd.DataFrame(), None


# =========================
# 💾 SAUVEGARDE ROBUSTE
# =========================
def save_data(df):

    max_attempts = 5

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

    for attempt in range(max_attempts):

        current_df, sha = read_data()

        # =========================
        # 🆕 INIT SI FICHIER ABSENT
        # =========================
        if sha is None:
            current_df = pd.DataFrame(columns=required_cols)
            sha = None

        # =========================
        # 🔧 NORMALISATION COLONNES
        # =========================
        if current_df.empty:
            current_df = pd.DataFrame(columns=required_cols)

        # Ajouter colonnes manquantes
        for col in required_cols:
            if col not in current_df.columns:
                current_df[col] = ""

        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

        # Forcer ordre
        current_df = current_df[required_cols]
        df = df[required_cols]

        # =========================
        # 📦 MERGE
        # =========================
        merged = pd.concat([current_df, df], ignore_index=True)

        # =========================
        # 🚀 PUSH GITHUB
        # =========================
        payload = {
            "message": "Update appels_saisis.csv",
            "content": base64.b64encode(
                merged.to_csv(index=False).encode()
            ).decode()
        }

        # ⚠️ sha seulement si fichier existe
        if sha:
            payload["sha"] = sha

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        r = requests.put(url, json=payload, headers=HEADERS)

        if r.status_code in (200, 201):
            return True

        # conflit → retry
        if r.status_code == 409:
            time.sleep(1)
            continue

        st.error(f"❌ GitHub ERROR {r.status_code}: {r.text}")
        return False

    return False


# =========================
# ➕ AJOUT LIGNE SÉCURISÉ
# =========================
def add_row_safe(row):

    # =========================
    # 🔒 VALIDATION INPUT
    # =========================
    if not isinstance(row, dict):
        st.error("❌ Format de données invalide")
        return False

    today = str(row.get("Date", "")).strip()
    tel = str(row.get("Telephone", "")).strip()

    if not today or not tel:
        st.error("❌ Date ou téléphone manquant")
        return False

    df_new = pd.DataFrame([row])

    current_df, _ = read_data()

    if not current_df.empty:

        # sécuriser colonnes
        if "Date" not in current_df.columns:
            current_df["Date"] = ""
        if "Telephone" not in current_df.columns:
            current_df["Telephone"] = ""

        # =========================
        # 🔒 RÈGLE 1 : DOUBLON JOUR
        # =========================
        doublon = current_df[
            (current_df["Date"] == today) &
            (current_df["Telephone"] == tel)
        ]

        if not doublon.empty:
            st.warning("⚠️ Numéro déjà appelé aujourd'hui")
            return False

        # =========================
        # 🔒 RÈGLE 2 : MAX 2 FOIS
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