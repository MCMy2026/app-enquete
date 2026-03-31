import sqlite3
import os
import pandas as pd

DB_PATH = "data/appels.db"

COLUMNS = [
    "Date","Enqueteur","Telephone","Commune",
    "Status","Sexe","Age_group","Niveau_cat"
]

# =========================
# 📞 NORMALISATION TELEPHONE
# =========================
def normalize_phone(x):
    if pd.isna(x):
        return ""

    x = str(x)
    x = "".join(c for c in x if c.isdigit())

    if x.startswith("225"):
        x = x[3:]
    if x.startswith("0"):
        x = x[1:]

    return "225" + x


# =========================
# INIT DB
# =========================
def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Enqueteur TEXT,
            Telephone TEXT,
            Commune TEXT,
            Status TEXT,
            Sexe TEXT,
            Age_group TEXT,
            Niveau_cat TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# READ
# =========================
def read_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM appels", conn)
    conn.close()

    if df.empty:
        df = pd.DataFrame(columns=COLUMNS)

    df["Telephone"] = df["Telephone"].apply(normalize_phone)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Date_only"] = df["Date"].dt.date
    df["Year"] = df["Date"].dt.isocalendar().year
    df["Week"] = df["Date"].dt.isocalendar().week

    return df


# =========================
# INSERT
# =========================
def add_row(row):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appels (
            Date, Enqueteur, Telephone, Commune,
            Status, Sexe, Age_group, Niveau_cat
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Date"],
        row["Enqueteur"],
        row["Telephone"],
        row["Commune"],
        row["Status"],
        row["Sexe"],
        row["Age_group"],
        row["Niveau_cat"]
    ))

    conn.commit()
    conn.close()


# =========================
# UPDATE (clé du mode terrain)
# =========================
def update_today_call(row):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appels
        SET Enqueteur=?, Commune=?, Status=?, Sexe=?, Age_group=?, Niveau_cat=?
        WHERE Telephone=? AND Date=?
    """, (
        row["Enqueteur"],
        row["Commune"],
        row["Status"],
        row["Sexe"],
        row["Age_group"],
        row["Niveau_cat"],
        row["Telephone"],
        row["Date"]
    ))

    conn.commit()
    conn.close()