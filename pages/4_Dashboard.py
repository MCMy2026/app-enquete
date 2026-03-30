import streamlit as st
import pandas as pd
from modules.github_data import read_data
from modules.export_pdf import generate_pdf



st.markdown("""
<style>
    .stMetric {
        background-color: #111;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG PAGE
# =========================
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

# =========================
# AUTH
# =========================
if not st.session_state.get("authentication_status"):
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📊 Dashboard Performance")

# =========================
# DATA
# =========================
df, _ = read_data()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# KPI (STYLE PRO)
# =========================
total = len(df)
repondus = len(df[df["Status"]=="Répondu"])
taux = (repondus / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("📞 Total appels", total)
col2.metric("✅ Répondus", repondus)
col3.metric("📊 Taux de réponse", f"{round(taux,1)} %")

st.divider()

# =========================
# SCORE INTELLIGENT
# =========================
df["week"] = df["Date"].dt.isocalendar().week

controle = df.groupby(["Enqueteur","Telephone","week"]).size().reset_index(name="nb")
violations = controle[controle["nb"] > 2]
penalite = violations.groupby("Enqueteur").size()

div = df.groupby("Enqueteur").agg(
    sexe_unique=("Sexe","nunique"),
    age_unique=("Age_group","nunique")
)

perf = df.groupby("Enqueteur").agg(
    appels=("Telephone", "count"),
    repondus=("Status", lambda x: (x == "Répondu").sum())
)

# conversion propre
perf = perf.apply(pd.to_numeric, errors="coerce").fillna(0)

# éviter division par 0
perf["appels"] = perf["appels"].replace(0, 1)

# calcul
perf["taux"] = (perf["repondus"] / perf["appels"] * 100).round(1)

#perf = df.groupby("Enqueteur").agg(
    #appels=("Telephone","count"),
    #repondus=("Status", lambda x: (x=="Répondu").sum())
#)

#perf["taux"] = perf["repondus"] / perf["appels"]
#perf = perf.join(div)

perf["penalite"] = perf.index.map(penalite).fillna(0)

perf["score"] = (
    (perf["appels"]/perf["appels"].max())*30 +
    perf["taux"]*40 +
    (perf["sexe_unique"]/2)*10 +
    (perf["age_unique"]/3)*10 +
    (1/(1+perf["penalite"]))*10
).round(2)

perf = perf.sort_values(by="score", ascending=False)

# =========================
# CLASSEMENT
# =========================
st.subheader("🏆 Classement des enquêteurs")

col1, col2 = st.columns([2,1])

with col1:
    st.dataframe(perf, use_container_width=True)

with col2:
    st.info(f"🥇 Top performer : {perf.index[0]}")

st.bar_chart(perf["score"])

st.divider()

# =========================
# VISU PRO
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Répartition des statuts")
    st.bar_chart(df["Status"].value_counts())

with col2:
    st.subheader("📍 Top communes")
    st.bar_chart(df["Commune"].value_counts().head(10))

st.subheader("📅 Activité dans le temps")
st.line_chart(df.groupby(df["Date"].dt.date).size())

st.divider()

# =========================
# EXPORT PRO
# =========================
st.subheader("📩 Export des données")

col1, col2 = st.columns(2)

# CSV
csv = df.to_csv(index=False).encode("utf-8")

with col1:
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name="export_appels.csv",
        mime="text/csv"
    )

# PDF
with col2:
    if st.button("📄 Générer PDF"):
        file = generate_pdf(perf.reset_index())

        with open(file, "rb") as f:
            st.download_button(
                "📥 Télécharger PDF",
                f,
                file_name="rapport.pdf"
            )