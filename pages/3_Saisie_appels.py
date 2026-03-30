import streamlit as st
import pandas as pd

from modules.github_data import read_data, add_row_safe

# AUTH
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📞 Saisie intelligente")

def clean_phone(phone):
    return str(phone).replace(" ", "").replace("-", "")

df, _ = read_data()
df["Telephone"] = df["Telephone"].astype(str).apply(clean_phone)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

telephone = st.text_input("Téléphone")
telephone_clean = clean_phone(telephone)

commune = st.text_input("Commune")
date = st.date_input("Date")

status = st.selectbox("Statut", ["Répondu","Occupé","Absent"])
sexe = st.selectbox("Sexe", ["Homme","Femme"])
age = st.selectbox("Age", ["18-39","40-54","55+"])
niveau = st.selectbox("Niveau", ["inferieur","superieur"])

# REGLE 2 APPELS
df["week"] = df["Date"].dt.isocalendar().week
calls = df[
    (df["Telephone"] == telephone_clean) &
    (df["week"] == pd.to_datetime(date).isocalendar().week)
].shape[0]

st.info(f"{calls}/2 appels cette semaine")

if calls >= 2:
    st.error("🚨 Limite atteinte")

if st.button("Enregistrer", disabled=calls >= 2):

    success = add_row_safe([
        str(date),
        st.session_state["name"],
        telephone_clean,
        commune,
        status,
        sexe,
        age,
        niveau
    ])

    if success:
        st.success("✅ Enregistré")
        st.rerun()
    else:
        st.error("Erreur GitHub")