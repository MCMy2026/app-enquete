import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

from modules.loader import load_base_appels

st.title("📅 Planification des appels")

df = load_base_appels()

if df.empty:
    st.warning("⚠️ Charger d'abord la base dans Configuration")
    st.stop()

st.success(f"✔ {len(df)} panélistes chargés")

nb_days = st.slider("Nombre de jours", 1, 28, 7)

if st.button("🚀 Générer planning"):

    planning = []

    start_date = datetime.today()

    for i in range(nb_days):

        day = start_date + timedelta(days=i)

        for commune in df["Commune"].unique():

            dfc = df[df["Commune"] == commune]

            sample = dfc.sample(min(15, len(dfc)))

            sample = sample.copy()
            sample["Date"] = day

            planning.append(sample)

    df_plan = pd.concat(planning)

    df_plan.to_excel("data/planning.xlsx", index=False)

    st.success("✅ Planning généré")

    st.dataframe(df_plan.head())

    st.download_button(
        "📥 Télécharger planning",
        df_plan.to_csv(index=False),
        "planning.csv"
    )