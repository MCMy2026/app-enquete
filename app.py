import streamlit as st
from modules.auth import load_auth

# =========================
# ⚙️ CONFIG APP
# =========================
st.set_page_config(
    page_title="Application Enquête",
    layout="wide"
)

# =========================
# 🔐 AUTHENTIFICATION
# =========================
authenticator, config = load_auth()

# ✅ Nouveau login (version récente)
authenticator.login()

# ✅ Récupération session
name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# =========================
# 🔐 CONTROLE ACCES
# =========================
if authentication_status is False:
    st.error("❌ Identifiants incorrects")
    st.stop()

elif authentication_status is None:
    st.warning("⚠️ Veuillez entrer vos identifiants")
    st.stop()

# =========================
# ✅ UTILISATEUR CONNECTÉ
# =========================
if authentication_status:

    # 🔓 Bouton logout
    authenticator.logout("🚪 Déconnexion", "sidebar")

    # 👤 Infos user
    st.sidebar.success(f"👤 Connecté : {name}")

    # 🔐 Sauvegarde session globale
    st.session_state["username"] = username
    st.session_state["name"] = name
    st.session_state["authentication_status"] = authentication_status

    # =========================
    # 🏠 PAGE PRINCIPALE
    # =========================
    st.title("🏠 Application Enquête")

    st.markdown("---")

    st.subheader("Bienvenue 👋")
    st.write(f"Utilisateur : **{name}**")

    st.markdown("""
    ### 🎯 Fonctionnalités disponibles :

    - 📞 Saisie des appels  
    - 📊 Dashboard de performance  
    - 🧠 Score intelligent  
    - 📩 Export PDF  
    - ⚙️ Gestion des utilisateurs (admin)  

    """)

    st.info("👉 Utilisez le menu à gauche pour naviguer dans l'application")