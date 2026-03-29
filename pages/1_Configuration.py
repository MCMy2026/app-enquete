import streamlit as st
import pandas as pd
import os
import datetime
import streamlit as st

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

from modules.loader import load_base_appels

st.title("⚙️ Configuration des données")

st.subheader("📂 Charger la base des panélistes")

uploaded_file = st.file_uploader("Importer base_appels.xlsx", type=["xlsx"])

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)
    df = df.drop_duplicates(subset=["Telephone"])

    main_file = "data/base_appels.xlsx"

    # 🔥 1. Sauvegarde historique (version unique)
    backup_file = f"data/base_appels_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(backup_file, index=False)

    # 🔥 2. Remplacement sécurisé du fichier principal
    try:
        if os.path.exists(main_file):
            os.remove(main_file)

        df.to_excel(main_file, index=False)

        st.success("✅ Base importée avec succès")
        st.info(f"📁 Sauvegarde créée : {backup_file}")

    except PermissionError:
        st.error("🚨 Fermez le fichier Excel 'base_appels.xlsx' avant d'importer")

    st.dataframe(df.head())