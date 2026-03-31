import streamlit as st
import pandas as pd

from modules.github_data import read_data, add_row_safe
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
# 🧠 UTILS
# =========================
def clean_phone(phone):
    phone = str(phone)
    phone = phone.replace(" ", "").replace("-", "")
    return phone.strip()

# =========================
# 📥 DATA
# =========================
df, _ = read_data()

if df.empty:
    df = pd.DataFrame(columns=[
        "Date","Enqueteur","Telephone","Commune",
        "Status","Sexe","Age_group","Niveau_cat"
    ])

df["Telephone"] = df["Telephone"].astype(str).apply(clean_phone)
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
df_pool["Telephone"] = df_pool["Telephone"].astype(str).apply(clean_phone)

communes = sorted(df_pool["Commune"].dropna().unique())

# =========================
# 📞 INPUT TEL
# =========================
telephone = st.text_input("Téléphone")
telephone_clean = clean_phone(telephone)
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

# =========================
# 📍 COMMUNE
# =========================
if paneliste is not None and paneliste["Commune"] in communes:
    commune = st.selectbox("Commune", communes, index=communes.index(paneliste["Commune"]))
else:
    commune = st.selectbox("Commune", communes)

# =========================
# 📅 DATE
# =========================
date_input = st.date_input("Date")
current_date = pd.to_datetime(date_input)

# =========================
# 📊 RÈGLE SEMAINE
# =========================
df["Year"] = df["Date"].dt.isocalendar().year
df["Week"] = df["Date"].dt.isocalendar().week

calls_week = df[
    (df["Telephone"] == telephone_clean) &
    (df["Year"] == current_date.isocalendar().year) &
    (df["Week"] == current_date.isocalendar().week)
].shape[0]

st.info(f"📊 Appels semaine : {calls_week}/2")

# =========================
# 🎯 MISSION
# =========================
df_today = df[
    (df["Commune"] == commune) &
    (df["Date"].dt.date == current_date.date())
]

st.subheader("🎯 Mission du jour")
st.dataframe(compute_daily_mission(df_today, quotas))

# =========================
# 🤖 SUGGESTIONS
# =========================
suggestions = recommend_panelists(
    df_pool[df_pool["Commune"] == commune],
    df,
    kpis
)

st.subheader("📞 Suggestions")
st.dataframe(suggestions)

# =========================
# 🧾 FORM
# =========================
sexe = st.selectbox("Sexe", ["Homme","Femme"])
age = st.selectbox("Age", ["18-39","40-54","55+"])
niveau = st.selectbox("Niveau", ["inferieur","superieur"])
status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])

enq = st.session_state["name"]

# =========================
# 🧠 SCORE
# =========================
score = 100

already_today = df[
    (df["Telephone"] == telephone_clean) &
    (df["Date"].dt.date == current_date.date())
].shape[0]

if already_today > 0:
    score -= 80

if calls_week >= 2:
    score -= 50

st.subheader("🧠 Score appel")

if score >= 70:
    st.success(f"Score {score} → recommandé")
elif score >= 40:
    st.warning(f"Score {score} → moyen")
else:
    st.error(f"Score {score} → déconseillé")

# =========================
# 🚫 VALIDATIONS
# =========================
errors = []

if telephone_clean == "":
    errors.append("Numéro obligatoire")

if not telephone_clean.isdigit():
    errors.append("Numéro invalide")

if paneliste is None:
    errors.append("Numéro non reconnu")

if calls_week >= 2:
    errors.append("Limite semaine atteinte")

if already_today > 0:
    errors.append("Déjà appelé aujourd’hui")

for e in errors:
    st.error(e)

# =========================
# 💾 SAVE (CORRIGÉ)
# =========================
disable_button = len(errors) > 0 or score < 40

if st.button("Enregistrer", disabled=disable_button):

    row = {
        "Date": current_date.strftime("%Y-%m-%d"),
        "Enqueteur": str(enq),
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
        st.error("❌ Erreur GitHub")