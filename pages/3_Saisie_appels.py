import streamlit as st
import pandas as pd

from modules.github_data import read_data, add_row_safe
from modules.kpi_quotas import compute_quota_kpis
from modules.recommendation import build_recommendation_message, recommend_panelists
from modules.quotas import get_quotas
from modules.mission import compute_daily_mission

# 🔐 Auth
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📞 Saisie intelligente")

# SESSION
if "telephone" not in st.session_state:
    st.session_state.telephone = ""

if "reset" not in st.session_state:
    st.session_state.reset = False

if st.session_state.reset:
    st.session_state.telephone = ""
    st.session_state.reset = False

# UTIL
def clean_phone(phone):
    return str(phone).replace(" ", "").replace("-", "").strip()

# DATA
df, _ = read_data()

if df.empty:
    df = pd.DataFrame(columns=[
        "Date","Enqueteur","Telephone","Commune","Status",
        "Sexe","Age_group","Niveau_cat"
    ])

df["Telephone"] = df["Telephone"].astype(str).apply(clean_phone)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# KPI
quotas = get_quotas()
kpis = compute_quota_kpis(df, quotas)

st.subheader("🤖 Recommandation")
st.info(build_recommendation_message(kpis))

# BASE PANEL
df_pool = pd.read_excel("data/base_appels.xlsx")
df_pool["Telephone"] = df_pool["Telephone"].astype(str).apply(clean_phone)

communes = sorted(df_pool["Commune"].dropna().unique())

# INPUT
telephone = st.text_input("Téléphone", key="telephone")
telephone_clean = clean_phone(telephone)

paneliste = None

# AUTO REMPLISSAGE
if telephone_clean:
    match = df_pool[df_pool["Telephone"] == telephone_clean]

    if not match.empty:
        paneliste = match.iloc[0]
        st.success("✅ Paneliste reconnu")

        st.write("👤 Nom :", paneliste.get("Nom", "N/A"))
        st.write("📍 Commune :", paneliste["Commune"])
        st.write("⚧ Sexe :", paneliste["Sexe"])
        st.write("🎂 Age :", paneliste["Age_group"])
        st.write("🎓 Niveau :", paneliste["Niveau_cat"])
    else:
        st.warning("⚠️ Numéro inconnu")

# COMMUNE
if paneliste is not None and paneliste["Commune"] in communes:
    commune = st.selectbox("Commune", communes, index=communes.index(paneliste["Commune"]))
else:
    commune = st.selectbox("Commune", communes)

# DATE
date = st.date_input("Date")
current_date = pd.to_datetime(date)

# REGLE 2 APPELS
df["Year"] = df["Date"].dt.isocalendar().year
df["Week"] = df["Date"].dt.isocalendar().week

current_year = current_date.isocalendar().year
current_week = current_date.isocalendar().week

calls_week = df[
    (df["Telephone"] == telephone_clean) &
    (df["Year"] == current_year) &
    (df["Week"] == current_week)
].shape[0]

st.info(f"📊 Appels cette semaine : {calls_week}/2")

# MISSION
df_today = df[
    (df["Commune"] == commune) &
    (df["Date"] == current_date)
]

st.subheader("🎯 Mission du jour")
mission = compute_daily_mission(df_today, quotas)
st.dataframe(mission)

# SUGGESTIONS
df_pool_filtered = df_pool[df_pool["Commune"] == commune]
suggestions = recommend_panelists(df_pool_filtered, df, kpis)

st.subheader("📞 Suggestions")
st.dataframe(suggestions.head())

# FORM
sexe = st.selectbox("Sexe", ["Homme","Femme"])
age = st.selectbox("Age", ["18-39","40-54","55+"])
niveau = st.selectbox("Niveau", ["inferieur","superieur"])

enq = st.session_state["name"]
st.info(f"👤 Connecté : {enq}")

status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])

disable_button = calls_week >= 2

if disable_button:
    st.error("🚨 Limite atteinte : 2 appels/semaine")

# SAVE
if st.button("Enregistrer", disabled=disable_button):

    if not telephone_clean:
        st.error("Numéro obligatoire")
        st.stop()

    success = add_row_safe([
        str(current_date),
        enq,
        telephone_clean,
        commune,
        status,
        sexe,
        age,
        niveau
    ])

    if success:
        st.success("✅ Appel enregistré (sécurisé)")
        st.session_state.reset = True
        st.rerun()
    else:
        st.error("❌ Erreur lors de l'enregistrement")

# RESET
if st.button("🧹 Vider les champs"):
    st.session_state.reset = True
    st.rerun()