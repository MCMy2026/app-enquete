import streamlit as st
import pandas as pd
from io import BytesIO
from modules.github_data import read_data
from modules.export_pdf import generate_pdf



# Configuration de la page
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

# Authentification
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📊 Dashboard Performance")

# Chargement des données
df, _ = read_data()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# KPIs
total = len(df)
repondus = len(df[df["Status"] == "Répondu"])
taux = (repondus / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("📞 Total appels", total)
col2.metric("✅ Répondus", repondus)
col3.metric("📊 Taux de réponse", f"{round(taux, 1)} %")

st.divider()

# Score intelligent
df["week"] = df["Date"].dt.isocalendar().week

controle = df.groupby(["Enqueteur", "Telephone", "week"]).size().reset_index

import streamlit as st
import pandas as pd
from io import BytesIO
from modules.github_data import read_data
from modules.export_pdf import generate_pdf

# Configuration de la page
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

# Authentification
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📊 Dashboard Performance")

# Chargement des données
df, _ = read_data()
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# KPIs
total = len(df)
repondus = len(df[df["Status"] == "Répondu"])
taux = (repondus / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("📞 Total appels", total)
col2.metric("✅ Répondus", repondus)
col3.metric("📊 Taux de réponse", f"{round(taux, 1)} %")

st.divider()

# Score intelligent
df["week"] = df["Date"].dt.isocalendar().week

controle = df.groupby(["Enqueteur", "Telephone", "week"]).size().reset_index