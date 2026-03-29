import streamlit as st
import streamlit_authenticator as stauth
import streamlit as st

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

from modules.auth import load_auth, save_users

# 🔐 Sécurité
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

authenticator, config = load_auth()

# 🔐 Vérifier rôle admin
username = st.session_state["username"]
user_data = config["credentials"]["usernames"][username]

if user_data.get("role") != "admin":
    st.error("⛔ Accès réservé à l'admin")
    st.stop()

st.title("⚙️ Gestion des utilisateurs")

# =========================
# ➕ AJOUT UTILISATEUR
# =========================
st.subheader("➕ Ajouter un utilisateur")

new_username = st.text_input("Identifiant")
new_name = st.text_input("Nom")
new_password = st.text_input("Mot de passe", type="password")
role = st.selectbox("Rôle", ["user", "admin"])

if st.button("Créer utilisateur"):

    if new_username in config["credentials"]["usernames"]:
        st.error("❌ Utilisateur existe déjà")

    elif new_username == "" or new_password == "":
        st.error("❌ Champs obligatoires")

    else:
        hashed = stauth.Hasher().hash_list([new_password])[0]

        config["credentials"]["usernames"][new_username] = {
            "name": new_name,
            "password": hashed,
            "role": role
        }

        save_users(config)

        st.success("✅ Utilisateur créé avec succès")
        st.rerun()

# =========================
# 👥 LISTE UTILISATEURS
# =========================
st.subheader("👥 Utilisateurs existants")

for user, data in config["credentials"]["usernames"].items():
    col1, col2, col3 = st.columns(3)

    col1.write(user)
    col2.write(data.get("role", "user"))

    if col3.button(f"Supprimer {user}"):
        del config["credentials"]["usernames"][user]
        save_users(config)
        st.rerun()