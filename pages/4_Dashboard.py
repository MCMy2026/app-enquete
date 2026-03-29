import streamlit as st
import pandas as pd
import streamlit as st

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

# 🔐 Sécurité
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("🔒 Veuillez vous connecter")
    st.stop()

st.title("📊 Dashboard Performance")

file_path = "data/appels_saisis.csv"

# =========================
# 📂 LOAD DATA
# =========================
try:
    df = pd.read_csv(file_path)
except:
    st.error("Aucune donnée disponible")
    st.stop()

# 🔥 Nettoyage
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 🎯 FILTRES
# =========================
st.sidebar.header("Filtres")

enqueteurs = df["Enqueteur"].dropna().unique().tolist()
selected_enq = st.sidebar.multiselect("Enquêteur", enqueteurs, default=enqueteurs)

date_min = df["Date"].min()
date_max = df["Date"].max()

date_range = st.sidebar.date_input("Période", [date_min, date_max])

# =========================
# 📊 FILTRAGE
# =========================
df = df[df["Enqueteur"].isin(selected_enq)]

if len(date_range) == 2:
    df = df[(df["Date"] >= pd.to_datetime(date_range[0])) &
            (df["Date"] <= pd.to_datetime(date_range[1]))]

# =========================
# 📈 KPI GLOBAL
# =========================
st.subheader("📈 Indicateurs globaux")

total = len(df)
repondus = len(df[df["Status"] == "Répondu"])
taux = (repondus / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("📞 Total appels", total)
col2.metric("✅ Répondus", repondus)
col3.metric("📊 Taux de réponse (%)", round(taux, 1))

# =========================
# 👤 PERFORMANCE PAR ENQUETEUR
# =========================
st.subheader("👤 Performance par enquêteur")

perf = df.groupby("Enqueteur").agg(
    appels=("Telephone", "count"),
    repondus=("Status", lambda x: (x == "Répondu").sum())
).reset_index()

perf["taux"] = (perf["repondus"] / perf["appels"] * 100).round(1)

st.dataframe(perf)

# =========================
# 📊 GRAPHIQUE
# =========================
st.subheader("📊 Comparaison")

st.bar_chart(perf.set_index("Enqueteur")[["appels", "repondus"]])

# =========================
# 📅 EVOLUTION TEMPORELLE
# =========================
st.subheader("📅 Evolution des appels")

df_time = df.groupby(df["Date"].dt.date).size()

st.line_chart(df_time)

# =========================
# 🏆 TOP PERFORMANCE
# =========================
#st.subheader("🏆 Classement")

#top = perf.sort_values(by="taux", ascending=False)

#st.dataframe(top)

# =========================
# 🧠 SCORE INTELLIGENT
# =========================
st.subheader("🧠 Score intelligent")

# 📞 Volume
volume = df.groupby("Enqueteur")["Telephone"].count()

# ✅ Réponse
reponse = df[df["Status"] == "Répondu"].groupby("Enqueteur")["Telephone"].count()

perf = pd.DataFrame({
    "appels": volume,
    "repondus": reponse
}).fillna(0)

perf["taux"] = perf["repondus"] / perf["appels"]

# =========================
# ⚖️ REGLE 2 APPELS / SEMAINE
# =========================
df["semaine"] = df["Date"].dt.isocalendar().week

controle = df.groupby(["Enqueteur", "Telephone", "semaine"]).size().reset_index(name="nb")

violations = controle[controle["nb"] > 2]

penalite = violations.groupby("Enqueteur").size()

perf["penalite"] = perf.index.map(penalite).fillna(0)

# Score respect (moins de pénalité = mieux)
perf["respect"] = 1 / (1 + perf["penalite"])

# =========================
# 🎯 NORMALISATION
# =========================
perf["volume_norm"] = perf["appels"] / perf["appels"].max()

# =========================
# 🧮 SCORE FINAL
# =========================
perf["score"] = (
    perf["volume_norm"] * 40 +
    perf["taux"] * 40 +
    perf["respect"] * 20
)

perf["score"] = perf["score"].round(1)

# =========================
# 🏆 AFFICHAGE
# =========================
perf = perf.sort_values(by="score", ascending=False)

st.dataframe(perf)

# =========================
# 🥇 TOP ENQUETEUR
# =========================
top1 = perf.index[0]
st.success(f"🥇 Meilleur enquêteur : {top1} (Score {perf.iloc[0]['score']})")

# =========================
# 📊 GRAPH SCORE
# =========================
st.bar_chart(perf["score"])

st.write("🔎 Détail des pénalités")
st.dataframe(violations)

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# =========================
# 📩 EXPORT PDF
# =========================
st.subheader("📩 Export PDF")

def generate_pdf(perf):
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("📊 RAPPORT DE PERFORMANCE", styles["Title"]))
    elements.append(Spacer(1, 10))

    # Tableau
    data = [["Enquêteur", "Appels", "Répondus", "Taux (%)", "Score"]]

    for idx, row in perf.iterrows():
        data.append([
            idx,
            int(row["appels"]),
            int(row["repondus"]),
            round(row["taux"] * 100, 1),
            row["score"]
        ])

    table = Table(data)

    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ])

    elements.append(table)

    # Création fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_file.name)
    doc.build(elements)

    return temp_file.name


# =========================
# 📥 BOUTON DOWNLOAD
# =========================
if st.button("📄 Générer rapport PDF"):

    pdf_file = generate_pdf(perf)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="⬇️ Télécharger le PDF",
            data=f,
            file_name="rapport_performance.pdf",
            mime="application/pdf"
        )