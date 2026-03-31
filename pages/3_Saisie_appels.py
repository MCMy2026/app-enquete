import streamlit as st
import pandas as pd

from modules.github_data import read_data, add_row_safe, normalize_phone

st.cache_data.clear()

st.title("📞 Saisie appels - VERSION CORRIGÉE")

# =========================
# 📥 DATA HISTORIQUE
# =========================
df, _ = read_data()
df["Telephone"] = df["Telephone"].apply(normalize_phone)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 📂 BASE PANELISTES
# =========================
df_pool = pd.read_excel("data/base_appels_clean.xlsx")

# 🔥 NORMALISATION CRITIQUE
df_pool["Telephone"] = df_pool["Telephone"].apply(normalize_phone)

# =========================
# 📞 INPUT
# =========================
telephone = st.text_input("📞 Téléphone")
telephone_clean = normalize_phone(telephone)

# =========================
# 🔍 MATCH PANELISTE (CORRIGÉ)
# =========================
paneliste = None

if telephone_clean != "":
    match = df_pool[df_pool["Telephone"] == telephone_clean]

    if not match.empty:
        paneliste = match.iloc[0]
        st.success("✅ Paneliste reconnu")
    else:
        st.warning("⚠️ Numéro non trouvé dans la base")

# =========================
# 📍 COMMUNE AUTO (FIX)
# =========================
if paneliste is not None:
    commune = paneliste["Commune"]
    st.text_input("Commune", value=commune, disabled=True)
else:
    commune = st.text_input("Commune")

# =========================
# 👤 INFOS AUTO
# =========================
if paneliste is not None:
    sexe = paneliste["Sexe"]
    age = paneliste["Age_group"]
    niveau = paneliste["Niveau_cat"]

    st.text_input("Sexe", value=sexe, disabled=True)
    st.text_input("Age", value=age, disabled=True)
    st.text_input("Niveau", value=niveau, disabled=True)
else:
    sexe = st.selectbox("Sexe", ["Homme","Femme"])
    age = st.selectbox("Age", ["18-39","40-54","55+"])
    niveau = st.selectbox("Niveau", ["inferieur","superieur"])

# =========================
# 📅 DATE
# =========================
date = st.date_input("Date")
current_date = pd.to_datetime(date)

# =========================
# 📊 RÈGLES (CORRIGÉES)
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

# =========================
# 🚫 VALIDATION BLOQUANTE
# =========================
errors = []

if telephone_clean == "":
    errors.append("Téléphone obligatoire")

if paneliste is None:
    errors.append("Numéro non reconnu (base panel)")

if already_today > 0:
    errors.append("❌ Déjà appelé aujourd’hui")

if calls_week >= 2:
    errors.append("❌ Limite hebdomadaire atteinte")

for e in errors:
    st.error(e)

# =========================
# 📊 DEBUG (IMPORTANT)
# =========================
st.write("📊 Appels semaine:", calls_week)
st.write("📊 Appels aujourd’hui:", already_today)

# =========================
# 💾 SAVE (BLOQUÉ SI ERREUR)
# =========================
if st.button("💾 Enregistrer", disabled=len(errors) > 0):

    row = {
        "Date": current_date.strftime("%Y-%m-%d"),
        "Enqueteur": st.session_state.get("name", "user"),
        "Telephone": telephone_clean,
        "Commune": commune,
        "Status": "Répondu",
        "Sexe": sexe,
        "Age_group": age,
        "Niveau_cat": niveau
    }

    success = add_row_safe(row)

    if success:
        st.success("✅ Enregistré")
        st.rerun()
    else:
        st.error("❌ Erreur enregistrement")

       