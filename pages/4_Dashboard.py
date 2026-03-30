import streamlit as st
import pandas as pd

from modules.github_data import read_data

st.markdown("""
<style>
.metric-container {
    background-color: #111;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# 🔐 Auth
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

# 🎨 CONFIG PAGE
st.set_page_config(page_title="Dashboard Pro", layout="wide")

st.title("📊 Dashboard Performance")

# 📥 DATA
df, _ = read_data()

if df.empty:
    st.error("Aucune donnée disponible")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# 🎛️ FILTRES
st.sidebar.header("🎯 Filtres")

enqueteurs = df["Enqueteur"].dropna().unique().tolist()
selected_enq = st.sidebar.multiselect("👤 Enquêteur", enqueteurs, default=enqueteurs)

date_range = st.sidebar.date_input(
    "📅 Période",
    [df["Date"].min(), df["Date"].max()]
)

df = df[df["Enqueteur"].isin(selected_enq)]

if len(date_range) == 2:
    df = df[
        (df["Date"] >= pd.to_datetime(date_range[0])) &
        (df["Date"] <= pd.to_datetime(date_range[1]))
    ]

# 📊 KPI GLOBAL
total = len(df)
repondus = len(df[df["Status"] == "Répondu"])
taux = (repondus / total * 100) if total > 0 else 0

st.markdown("## 📈 Indicateurs clés")

col1, col2, col3 = st.columns(3)

col1.metric("📞 Total appels", total)
col2.metric("✅ Répondus", repondus)
col3.metric("📊 Taux (%)", round(taux, 1))

# 📊 PERFORMANCE PAR ENQUETEUR
perf = df.groupby("Enqueteur").agg(
    appels=("Telephone", "count"),
    repondus=("Status", lambda x: (x == "Répondu").sum())
).reset_index()

# sécurisation
perf["appels"] = pd.to_numeric(perf["appels"], errors="coerce").fillna(0)
perf["repondus"] = pd.to_numeric(perf["repondus"], errors="coerce").fillna(0)

perf["taux"] = perf.apply(
    lambda x: round((x["repondus"] / x["appels"] * 100), 1) if x["appels"] > 0 else 0,
    axis=1
)

st.markdown("## 📊 Performance par enquêteur")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(perf, use_container_width=True)

with col2:
    st.bar_chart(perf.set_index("Enqueteur")[["appels", "repondus"]])

# 🧠 SCORE INTELLIGENT
df["week"] = df["Date"].dt.isocalendar().week

controle = df.groupby(["Enqueteur", "Telephone", "week"]).size().reset_index(name="nb")
violations = controle[controle["nb"] > 2]

penalite = violations.groupby("Enqueteur").size()

perf = perf.set_index("Enqueteur")
perf["penalite"] = perf.index.map(penalite).fillna(0)
perf["respect"] = 1 / (1 + perf["penalite"])
perf["volume_norm"] = perf["appels"] / perf["appels"].max()

perf["score"] = (
    perf["volume_norm"] * 40 +
    (perf["taux"] / 100) * 40 +
    perf["respect"] * 20
).round(1)

perf = perf.sort_values(by="score", ascending=False)

# 🏆 CLASSEMENT
st.markdown("## 🏆 Classement")

top1 = perf.index[0]
st.success(f"🥇 Meilleur enquêteur : {top1}")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(perf, use_container_width=True)

with col2:
    st.bar_chart(perf["score"])

# 📥 EXPORT PRO
st.markdown("## 📥 Export des données")
st.caption("Télécharge les données filtrées")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Télécharger CSV",
    data=csv,
    file_name="export_appels.csv",
    mime="text/csv"
)