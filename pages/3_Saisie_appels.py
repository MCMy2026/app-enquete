import streamlit as st
from datetime import date
from modules.github_data import add_row_safe

# =========================
# 🔐 SESSION
# =========================
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.error("❌ Accès refusé")
    st.stop()

username = st.session_state.get("username", "unknown")

# =========================
# 🏠 UI
# =========================
st.title("📞 Saisie des appels")

st.markdown("---")

# =========================
# 📥 FORMULAIRE
# =========================
with st.form("form_appel"):

    col1, col2 = st.columns(2)

    with col1:
        date_appel = st.date_input("📅 Date", value=date.today())
        telephone = st.text_input("📞 Téléphone")
        commune = st.text_input("🏙️ Commune")

    with col2:
        status = st.selectbox("📊 Statut", ["Répondu", "Non Répondu"])
        sexe = st.selectbox("👤 Sexe", ["Homme", "Femme"])
        age_group = st.selectbox("🎂 Tranche d'âge", ["Jeune", "Moyen", "Senior"])
        niveau = st.selectbox("🎓 Niveau", ["Inférieur", "Supérieur"])

    submit = st.form_submit_button("💾 Enregistrer")

# =========================
# 🚀 TRAITEMENT
# =========================
if submit:

    # =========================
    # 🔒 VALIDATIONS
    # =========================
    if not telephone.strip():
        st.warning("⚠️ Téléphone obligatoire")
        st.stop()

    if not telephone.isdigit():
        st.warning("⚠️ Téléphone invalide (chiffres uniquement)")
        st.stop()

    # =========================
    # 📦 CONSTRUCTION SAFE ROW
    # =========================
    row = {
        "Date": str(date_appel),
        "Enqueteur": username,
        "Telephone": telephone.strip(),
        "Commune": commune.strip(),
        "Status": status,
        "Sexe": sexe,
        "Age_group": age_group,
        "Niveau_cat": niveau
    }

    # DEBUG (tu peux enlever après test)
    # st.write(row)

    # =========================
    # 💾 SAUVEGARDE
    # =========================
    success = add_row_safe(row)

    if success:
        st.success("✅ Appel enregistré avec succès")
    else:
        st.error("❌ Échec de l'enregistrement")