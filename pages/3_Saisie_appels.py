import streamlit as st
import pandas as pd

from modules.github_data import read_data, add_row_safe, normalize_phone
from modules.kpi_quotas import compute_quota_kpis
from modules.recommendation import build_recommendation_message, recommend_panelists
from modules.quotas import get_quotas
from modules.mission import compute_daily_mission

# =========================
# 🔐 AUTH
# =========================
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📞 Saisie intelligente (PRO)")

# =========================
# 📥 DATA
# =========================
df, _ = read_data()

if df.empty:
    df = pd.DataFrame(columns=[
        "Date","Enqueteur","Telephone","Commune",
        "Status","Sexe","Age_group","Niveau_cat"
    ])

df["Telephone"] = df["Telephone"].apply(normalize_phone)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 📊 KPI
# =========================
quotas = get_quotas()
kpis = compute_quota_kpis(df, quotas)

st.subheader("🤖 Recommandation")
st.info(build_recommendation_message(kpis))

# =========================
# 📂 BASE PANEL
# =========================
df_pool = pd.read_excel("data/base_appels.xlsx")
df_pool["Telephone"] = df_pool["Telephone"].apply(normalize_phone)

communes = sorted(df_pool["Commune"].dropna().unique())

# =========================
# 📞 INPUT
# =========================
telephone = st.text_input("📞 Téléphone")
telephone_clean = normalize_phone(telephone)

paneliste = None

if telephone_clean:
    match = df_pool[df_pool["Telephone"] == telephone_clean]

    if not match.empty:
        paneliste = match.iloc[0]

        st.success("✅ Paneliste reconnu")
        st.write(paneliste)

    else:
        st.warning("⚠️ Numéro inconnu")

# =========================
# 📍 COMMUNE LOCK
# =========================
if paneliste is not None:
    commune = paneliste["Commune"]
    st.selectbox("Commune", [commune], disabled=True)
else:
    commune = st.selectbox("Commune", communes)

# =========================
# 📅 DATE
# =========================
date = st.date_input("Date")
current_date = pd.to_datetime(date)

# =========================
# 📊 RÈGLES
# =========================
df["Year"] = df["Date"].dt.isocalendar().year
df["Week"] = df["Date"].dt.isocalendar().week

calls_week = df[
    (df["Telephone"] == telephone_clean) &
    (df["Year"] == current_date.isocalendar().year) &
    (df["Week"] == current_date.isocalendar().week)
].shape[0]

already_today = df[
    (df["Telephone"] == telephone_clean) &
    (df["Date"].dt.date == current_date.date())
].shape[0]

st.write("DEBUG TEL:", telephone_clean)
st.write("DEBUG DF:", df["Telephone"].unique()[:5])

# =========================
# 🎯 FORM
# =========================
if paneliste is not None:
    sexe = paneliste["Sexe"]
    age = paneliste["Age_group"]
    niveau = paneliste["Niveau_cat"]

    st.selectbox("Sexe", [sexe], disabled=True)
    st.selectbox("Age", [age], disabled=True)
    st.selectbox("Niveau", [niveau], disabled=True)
else:
    sexe = st.selectbox("Sexe", ["Homme","Femme"])
    age = st.selectbox("Age", ["18-39","40-54","55+"])
    niveau = st.selectbox("Niveau", ["inferieur","superieur"])

status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])

# =========================
# 🚫 VALIDATION
# =========================
errors = []

if telephone_clean == "":
    errors.append("Numéro obligatoire")

if already_today > 0:
    errors.append("Déjà appelé aujourd’hui")

if calls_week >= 2:
    errors.append("Limite semaine atteinte")

for e in errors:
    st.error(e)

# =========================
# 💾 SAVE
# =========================
if st.button("💾 Enregistrer", disabled=len(errors) > 0):

    row = {
        "Date": current_date.strftime("%Y-%m-%d"),
        "Enqueteur": st.session_state["name"],
        "Telephone": telephone_clean,
        "Commune": commune,
        "Status": status,
        "Sexe": sexe,
        "Age_group": age,
        "Niveau_cat": niveau
    }

    if add_row_safe(row):
        st.success("✅ Enregistré")
        st.rerun()
    else:
        st.error("❌ Erreur sauvegarde")