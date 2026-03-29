import streamlit as st
import pandas as pd

import streamlit as st
import streamlit as st

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

from modules.kpi_quotas import compute_quota_kpis
from modules.recommendation import build_recommendation_message, recommend_panelists
from modules.quotas import get_quotas
from modules.mission import compute_daily_mission

st.title("📞 Saisie intelligente")

file_path = "data/appels_saisis.csv"

# ==============================
# 🔄 SESSION STATE (SAFE)
# ==============================
if "telephone" not in st.session_state:
    st.session_state.telephone = ""

if "reset" not in st.session_state:
    st.session_state.reset = False

# 🔥 RESET AVANT WIDGET (IMPORTANT)
if st.session_state.reset:
    st.session_state.telephone = ""
    st.session_state.reset = False

# ==============================
# 🔧 UTIL
# ==============================
def clean_phone(phone):
    return str(phone).replace(" ", "").replace("-", "").strip()

# ==============================
# 📂 DATA
# ==============================
try:
    df = pd.read_csv(file_path)
except:
    df = pd.DataFrame(columns=[
        "Date","Enqueteur","Telephone","Commune","Status",
        "Sexe","Age_group","Niveau_cat"
    ])

df["Telephone"] = df["Telephone"].astype(str).apply(clean_phone)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ==============================
# 📊 KPI
# ==============================
quotas = get_quotas()
kpis = compute_quota_kpis(df, quotas)

st.subheader("🤖 Recommandation")
st.info(build_recommendation_message(kpis))

# ==============================
# 📂 BASE PANEL
# ==============================
df_pool = pd.read_excel("data/base_appels.xlsx")
df_pool["Telephone"] = df_pool["Telephone"].astype(str).apply(clean_phone)

communes = sorted(df_pool["Commune"].dropna().unique())

# ==============================
# 📞 INPUT TELEPHONE
# ==============================
telephone = st.text_input("Téléphone", key="telephone")
telephone_clean = clean_phone(telephone)

# ==============================
# 🔍 AUTO-REMPLISSAGE
# ==============================
paneliste = None

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

# ==============================
# 📍 COMMUNE
# ==============================
if paneliste is not None and paneliste["Commune"] in communes:
    commune = st.selectbox("Commune", communes, index=communes.index(paneliste["Commune"]))
else:
    commune = st.selectbox("Commune", communes)

# ==============================
# 📅 DATE
# ==============================
date = st.date_input("Date")
current_date = pd.to_datetime(date)

# ==============================
# 📊 REGLE 2 APPELS / SEMAINE
# ==============================
df["Year"] = df["Date"].dt.isocalendar().year
df["Week"] = df["Date"].dt.isocalendar().week

current_year = current_date.isocalendar().year
current_week = current_date.isocalendar().week

df_week = df[
    (df["Telephone"] == telephone_clean) &
    (df["Year"] == current_year) &
    (df["Week"] == current_week)
]

df_day = df[
    (df["Telephone"] == telephone_clean) &
    (df["Date"] == current_date)
]

calls_week = len(df_week)
already_today = not df_day.empty

st.info(f"📊 Appels cette semaine : {calls_week}/2")

if already_today:
    st.warning("⚠️ Déjà appelé aujourd’hui")

# ==============================
# 🎯 MISSION
# ==============================
df_today = df[
    (df["Commune"] == commune) &
    (df["Date"] == current_date)
]

st.subheader("🎯 Mission du jour")
mission = compute_daily_mission(df_today, quotas)
st.dataframe(mission)

# ==============================
# 🤖 SUGGESTIONS
# ==============================
df_pool_filtered = df_pool[df_pool["Commune"] == commune]
suggestions = recommend_panelists(df_pool_filtered, df, kpis)

st.subheader("📞 Suggestions")
st.dataframe(suggestions.head())

# ==============================
# 🎯 AUTO VALUES
# ==============================
default_sexe = paneliste["Sexe"] if paneliste is not None else None
default_age = paneliste["Age_group"] if paneliste is not None else None
default_niveau = paneliste["Niveau_cat"] if paneliste is not None else None

# ==============================
# 📋 FORM
# ==============================
sexe = st.selectbox("Sexe", ["Homme","Femme"],
    index=["Homme","Femme"].index(default_sexe) if default_sexe in ["Homme","Femme"] else 0)

age = st.selectbox("Age", ["18-39","40-54","55+"],
    index=["18-39","40-54","55+"].index(default_age) if default_age in ["18-39","40-54","55+"] else 0)

niveau = st.selectbox("Niveau", ["inferieur","superieur"],
    index=["inferieur","superieur"].index(default_niveau) if default_niveau in ["inferieur","superieur"] else 0)

enq = st.session_state["name"]
st.info(f"👤 Connecté : {enq}")
status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])

# ==============================
# 🚫 VERROUILLAGE
# ==============================
disable_button = False

if calls_week >= 2:
    st.error("🚨 Limite atteinte : 2 appels/semaine")
    disable_button = True

# ==============================
# 💾 SAVE
# ==============================
if st.button("Enregistrer", disabled=disable_button):

    if not telephone_clean:
        st.error("Numéro obligatoire")
        st.stop()

    new_row = pd.DataFrame([{
        "Date": current_date,
        "Enqueteur": enq,
        "Telephone": telephone_clean,
        "Commune": commune,
        "Status": status,
        "Sexe": sexe,
        "Age_group": age,
        "Niveau_cat": niveau
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df = df.drop(columns=["Year","Week"], errors="ignore")
    df.to_csv(file_path, index=False)

    st.success("✅ Appel enregistré avec succès")

    # ✅ RESET PRO (sans bug)
    st.session_state.reset = True
    st.rerun()

# ==============================
# 🧹 RESET MANUEL
# ==============================
if st.button("🧹 Vider les champs"):
    st.session_state.reset = True
    st.rerun()