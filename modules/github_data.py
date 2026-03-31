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
# 📥 LECTURE CSV
# =========================
def read_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode()

        try:
            df = pd.read_csv(StringIO(content))
        except:
            df = pd.DataFrame()

        return df, data.get("sha")

    if r.status_code == 404:
        return pd.DataFrame(), None

    st.error(f"❌ Erreur lecture GitHub ({r.status_code})")
    return pd.DataFrame(), None


# =========================
# 💾 SAUVEGARDE ROBUSTE
# =========================
def save_data(df):

    required_cols = [
        "Date","Enqueteur","Telephone","Commune",
        "Status","Sexe","Age_group","Niveau_cat"
    ]

    for _ in range(5):

        current_df, sha = read_data()

        if current_df.empty:
            current_df = pd.DataFrame(columns=required_cols)

        # 🔧 Harmonisation
        for col in required_cols:
            if col not in current_df.columns:
                current_df[col] = ""
            if col not in df.columns:
                df[col] = ""

        current_df = current_df[required_cols]
        df = df[required_cols]

        merged = pd.concat([current_df, df], ignore_index=True)

        payload = {
            "message": "Update appels_saisis.csv",
            "content": base64.b64encode(
                merged.to_csv(index=False).encode()
            ).decode()
        }

        if sha:
            payload["sha"] = sha

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        r = requests.put(url, json=payload, headers=HEADERS)

        if r.status_code in (200, 201):
            return True

        if r.status_code == 409:
            time.sleep(1)
            continue

        st.error(f"❌ GitHub ERROR {r.status_code}")
        return False

    return False


# =========================
# ➕ AJOUT ULTRA SÉCURISÉ
# =========================
def add_row_safe(row):

    # =========================
    # 🔒 PROTECTION MAX
    # =========================
    if row is None:
        st.error("❌ row = None")
        return False

    if not isinstance(row, dict):
        st.error(f"❌ Mauvais format: {type(row)}")
        return False

    required_fields = ["Date", "Telephone"]

    for f in required_fields:
        if f not in row or row[f] in [None, ""]:
            st.error(f"❌ Champ invalide : {f}")
            return False

    # =========================
    # 🔧 NORMALISATION
    # =========================
    try:
        tel = str(row["Telephone"]).strip()
        date = pd.to_datetime(row["Date"], errors="coerce")
    except Exception as e:
        st.error(f"❌ Erreur conversion: {e}")
        return False

    if tel == "" or pd.isna(date):
        st.error("❌ Données invalides")
        return False

    row["Telephone"] = tel
    row["Date"] = date.strftime("%Y-%m-%d")

    # =========================
    # 📥 DATA EXISTANTE
    # =========================
    current_df, _ = read_data()

    if current_df.empty:
        return save_data(pd.DataFrame([row]))

    # nettoyage
    current_df["Telephone"] = current_df["Telephone"].astype(str).str.strip()
    current_df["Date"] = pd.to_datetime(current_df["Date"], errors="coerce")

    # =========================
    # 🔒 RÈGLE 1 : 1 / JOUR
    # =========================
    same_day = current_df[
        (current_df["Telephone"] == tel) &
        (current_df["Date"].dt.date == date.date())
    ]

    if not same_day.empty:
        st.warning("⚠️ Déjà appelé aujourd’hui")
        return False

    # =========================
    # 🔒 RÈGLE 2 : 2 / SEMAINE
    # =========================
    current_df["Year"] = current_df["Date"].dt.isocalendar().year
    current_df["Week"] = current_df["Date"].dt.isocalendar().week

    y = date.isocalendar().year
    w = date.isocalendar().week

    week_calls = current_df[
        (current_df["Telephone"] == tel) &
        (current_df["Year"] == y) &
        (current_df["Week"] == w)
    ]

    if len(week_calls) >= 2:
        st.warning("⚠️ Limite 2 appels / semaine atteinte")
        return False

    # =========================
    # 💾 SAVE
    # =========================
    return save_data(pd.DataFrame([row]))