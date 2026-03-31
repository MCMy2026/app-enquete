import streamlit as st
import pandas as pd
import os

from modules.db import init_db, read_data, add_row, normalize_phone

st.title("📞 Saisie appels")

# =========================
# INIT
# =========================
init_db()
df = read_data()

# =========================
# BASE PANEL
# =========================
if not os.path.exists("data/base_appels_clean.xlsx"):
    st.error("Base panel manquante")
    st.stop()

df_pool = pd.read_excel("data/base_appels_clean.xlsx")
df_pool["Telephone"] = df_pool["Telephone"].apply(normalize_phone)

# =========================
# INPUT
# =========================
telephone = st.text_input("Téléphone")
telephone_clean = normalize_phone(telephone)

paneliste = None

if telephone_clean:
    match = df_pool[df_pool["Telephone"] == telephone_clean]
    if not match.empty:
        paneliste = match.iloc[0]
    else:
        st.warning("Numéro non reconnu")

# =========================
# AUTO REMPLISSAGE
# =========================
if paneliste is not None:
    commune = paneliste["Commune"]
    sexe = paneliste["Sexe"]
    age = paneliste["Age_group"]
    niveau = paneliste["Niveau_cat"]

    st.text_input("Commune", commune, disabled=True)
    st.text_input("Sexe", sexe, disabled=True)
    st.text_input("Age", age, disabled=True)
    st.text_input("Niveau", niveau, disabled=True)

else:
    commune = st.text_input("Commune")
    sexe = st.selectbox("Sexe", ["Homme","Femme"])
    age = st.selectbox("Age", ["18-39","40-54","55+"])
    niveau = st.selectbox("Niveau", ["inferieur","superieur"])

# =========================
# DATE
# =========================
date = st.date_input("Date")
current_date = pd.to_datetime(date)
current_day = current_date.date()

# =========================
# HISTORIQUE
# =========================
historique = df[df["Telephone"] == telephone_clean]

already_today = historique[
    historique["Date_only"] == current_day
].shape[0]

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

if not telephone_clean:
    errors.append("Téléphone obligatoire")

if paneliste is None:
    errors.append("Numéro invalide")

if already_today >= 1:
    errors.append("Déjà appelé aujourd’hui")

if calls_week >= 2:
    errors.append("Quota hebdomadaire atteint")

# =========================
# SAVE
# =========================
if st.button("Enregistrer"):

    if errors:
        for e in errors:
            st.error(e)
    else:
        row = {
            "Date": current_date.strftime("%Y-%m-%d"),
            "Enqueteur": st.session_state.get("name", "agent"),
            "Telephone": telephone_clean,
            "Commune": commune,
            "Status": "Répondu",
            "Sexe": sexe,
            "Age_group": age,
            "Niveau_cat": niveau
        }

        success = add_row(row)

        if success:
            st.success("Enregistrement effectué")
            st.rerun()
        else:
            st.error("Doublon détecté")