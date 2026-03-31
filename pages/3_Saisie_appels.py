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
    return str(phone).replace(" ", "").replace("-", "").replace(".0", "").strip()

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
telephone = st.text_input("📞 Téléphone")
telephone_clean = clean_phone(telephone)
paneliste = None

if telephone_clean:
    match = df_pool[df_pool["Telephone"] == telephone_clean]

    if not match.empty:
        paneliste = match.iloc[0]

        st.success("✅ Paneliste reconnu")

        col1, col2 = st.columns(2)
        col1.write(f"👤 {paneliste.get('Nom', 'N/A')}")
        col2.write(f"📍 {paneliste['Commune']}")

        col1.write(f"⚧ {paneliste['Sexe']}")
        col2.write(f"🎂 {paneliste['Age_group']}")

        st.write(f"🎓 Niveau : {paneliste['Niveau_cat']}")
    else:
        st.warning("⚠️ Numéro inconnu (saisie libre)")

# =========================
# 📍 COMMUNE
# =========================
if paneliste is not None:
    commune = paneliste["Commune"]
    st.selectbox("Commune", [commune], disabled=True)
    st.info(f"🔒 Commune verrouillée : {commune}")
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
# 📊 AUTO PANELISTE
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

# =========================
# 📊 STATUS
# =========================
status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])

# =========================
# 🧠 SCORE
# =========================
score = 100

if already_today > 0:
    score -= 80

if calls_week >= 2:
    score -= 50

st.subheader("🧠 Analyse appel")

if already_today > 0:
    st.error("🚫 Déjà appelé aujourd’hui")
elif calls_week >= 2:
    st.error("🚫 Limite semaine atteinte")
elif score >= 70:
    st.success("✅ Appel recommandé")
elif score >= 40:
    st.warning("⚠️ Appel possible")
else:
    st.error("❌ Appel déconseillé")

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
disable_button = len(errors) > 0

if st.button("💾 Enregistrer", disabled=disable_button):

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