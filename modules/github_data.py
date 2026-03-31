import requests
import pandas as pd
import base64
import time
import streamlit as st
from io import StringIO

# =========================
# ⚙️ CONFIG
# =========================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "MCMy2026/app-enquete"
FILE_PATH = "data/appels_saisis.csv"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

COLUMNS = [
    "Date","Enqueteur","Telephone","Commune",
    "Status","Sexe","Age_group","Niveau_cat"
]

# =========================
# 📥 LECTURE
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
            df = pd.DataFrame(columns=COLUMNS)

        return df, data.get("sha")

    if r.status_code == 404:
        return pd.DataFrame(columns=COLUMNS), None

    return pd.DataFrame(columns=COLUMNS), None


# =========================
# 🧹 NORMALISATION DATA
# =========================
def clean_df(df):
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]

    df["Telephone"] = df["Telephone"].astype(str).str.replace(" ", "").str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


# =========================
# 💾 SAVE
# =========================
def save_data(new_df):

    for _ in range(5):

        current_df, sha = read_data()
        current_df = clean_df(current_df)
        new_df = clean_df(new_df)

        merged = pd.concat([current_df, new_df], ignore_index=True)

        payload = {
            "message": "update data",
            "content": base64.b64encode(
                merged.to_csv(index=False).encode()
            ).decode()
        }

        if sha:
            payload["sha"] = sha

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        r = requests.put(url, json=payload, headers=HEADERS)

        if r.status_code in [200, 201]:
            return True

        if r.status_code == 409:
            time.sleep(1)
            continue

        return False

    return False


# =========================
# ➕ AJOUT SÉCURISÉ
# =========================
def add_row_safe(row):

    if not isinstance(row, dict):
        st.error("Format invalide")
        return False

    # =========================
    # NORMALISATION INPUT
    # =========================
    tel = str(row.get("Telephone", "")).replace(" ", "").strip()
    date = pd.to_datetime(row.get("Date"), errors="coerce")

    if tel == "" or pd.isna(date):
        st.error("Données invalides")
        return False

    row["Telephone"] = tel
    row["Date"] = date

    # =========================
    # DATA EXISTANTE
    # =========================
    df, _ = read_data()
    df = clean_df(df)

    # =========================
    # 🔒 RÈGLE JOUR
    # =========================
    same_day = df[
        (df["Telephone"] == tel) &
        (df["Date"].dt.date == date.date())
    ]

    if len(same_day) > 0:
        st.warning("Déjà appelé aujourd’hui")
        return False

    # =========================
    # 🔒 RÈGLE SEMAINE
    # =========================
    df["Year"] = df["Date"].dt.isocalendar().year
    df["Week"] = df["Date"].dt.isocalendar().week

    y = date.isocalendar().year
    w = date.isocalendar().week

    week_calls = df[
        (df["Telephone"] == tel) &
        (df["Year"] == y) &
        (df["Week"] == w)
    ]

    if len(week_calls) >= 2:
        st.warning("Limite 2 appels semaine atteinte")
        return False

    # =========================
    # SAVE
    # =========================
    return save_data(pd.DataFrame([row]))