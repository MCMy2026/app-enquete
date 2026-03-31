import streamlit as st
import pandas as pd
import os

from modules.github_data import read_data, add_row_safe, normalize_phone

# =========================
# 🔥 RESET CACHE
# =========================
st.cache_data.clear()

st.title("📞 Saisie Appels (Version Debug Ultime)")

# =========================
# 📥 DATA
# =========================
df, err = read_data()

if err:
    st.error(f"Erreur lecture: {err}")

# =========================
# 🔍 DEBUG GLOBAL
# =========================
st.subheader("🔍 DEBUG GLOBAL")

st.write("Fichier existe ?", os.path.exists("data/appels_saisis.csv"))
st.write("Chemin absolu:", os.path.abspath("data/appels_saisis.csv"))
st.write("Nb lignes:", len(df))
st.write("Colonnes:", df.columns.tolist())

# =========================
# 📞 INPUT
# =========================
telephone = st.text_input("📞 Téléphone")
telephone_clean = normalize_phone(telephone)

st.write("📱 Téléphone normalisé:", telephone_clean)

# =========================
# 📋 FORM
# =========================
commune = st.text_input("Commune")
sexe = st.selectbox("Sexe", ["Homme", "Femme"])
age = st.selectbox("Age", ["18-39", "40-54", "55+"])
niveau = st.selectbox("Niveau", ["inferieur", "superieur"])
status = st.selectbox("Statut", ["Répondu", "Occupé", "Absent"])

date = st.date_input("Date")
current_date = pd.to_datetime(date)

# =========================
# 🚫 VALIDATION
# =========================
errors = []

if telephone_clean == "":
    errors.append("Téléphone obligatoire")

for e in errors:
    st.error(e)

# =========================
# 💾 SAVE
# =========================
if st.button("💾 Enregistrer", disabled=len(errors) > 0):

    row = {
        "Date": current_date.strftime("%Y-%m-%d"),
        "Enqueteur": "debug_user",
        "Telephone": telephone_clean,
        "Commune": commune,
        "Status": status,
        "Sexe": sexe,
        "Age_group": age,
        "Niveau_cat": niveau
    }

    st.subheader("📤 DEBUG ENVOI")
    st.write(row)

    success = add_row_safe(row)

    st.subheader("📥 DEBUG RESULTAT")
    st.write("Succès ?", success)

    if success:
        st.success("✅ Enregistrement réussi")
        st.rerun()
    else:
        st.error("❌ Échec enregistrement (voir terminal)")