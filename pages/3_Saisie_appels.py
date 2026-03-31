import streamlit as st
import pandas as pd
import os

from modules.db import init_db, read_data, add_row, normalize_phone

st.title("📞 Saisie appels (FINAL STABLE)")

# =========================
# INIT DB
# =========================
init_db()

# =========================
# DATA
# =========================
df = read_data()

# =========================
# BASE PANEL
# =========================
if os.path.exists("data/base_appels_clean.xlsx"):
    df_pool = pd.read_excel("data/base_appels_clean.xlsx")
else:
    st.error("❌ base_appels_clean.xlsx manquant")
    st.stop()

df_pool["Telephone"] = df_pool["Telephone"].apply(normalize_phone)

# =========================
# INPUT
# =========================
telephone = st.text_input("📞 Téléphone")
telephone_clean = normalize_phone(telephone)

paneliste = None

if telephone_clean != "":
    match = df_pool[df_pool["Telephone"] == telephone_clean]

    if not match.empty:
        paneliste = match.iloc[0]
        st.success("✅ Paneliste reconnu")
    else:
        st.error("❌ Numéro inconnu")

# =========================
# COMMUNE AUTO
# =========================
if paneliste is not None:
    commune = paneliste["Commune"]
    st.text_input("Commune", value=commune, disabled=True)
else:
    commune = st.text_input("Commune")

# =========================
# INFOS
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
# DATE
# =========================
date = st.date_input("Date")
current_date = pd.to_datetime(date)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Date_only"] = df["Date"].dt.date

current_day = current_date.date()

# =========================
# HISTORIQUE
# =========================
historique = df[df["Telephone"] == telephone_clean]

st.write("📋 Historique :", historique)

# =========================
# CHECK TODAY
# =========================
already_today = historique[
    historique["Date_only"] == current_day
].shape[0]

# =========================
# CHECK WEEK
# =========================
df["Year"] = df["Date"].dt.isocalendar().year
df["Week"] = df["Date"].dt.isocalendar().week

current_year = current_date.isocalendar().year
current_week = current_date.isocalendar().week

calls_week = historique[
    (historique["Year"] == current_year) &
    (historique["Week"] == current_week)
].shape[0]

# =========================
# VALIDATION
# =========================
errors = []

if telephone_clean == "":
    errors.append("Téléphone obligatoire")

if paneliste is None:
    errors.append("Numéro non reconnu")

if already_today >= 1:
    errors.append("Déjà appelé aujourd’hui")

if calls_week >= 2:
    errors.append("Limite hebdomadaire atteinte")

for e in errors:
    st.warning(e)

# =========================
# SAVE
# =========================
if st.button("💾 Enregistrer"):

    if len(errors) > 0:
        st.error("❌ Corrige les erreurs")
    else:
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

        success = add_row(row)

        if success:
            st.success("✅ Enregistré")
            st.rerun()
        else:
            st.error("❌ Doublon ou erreur DB")