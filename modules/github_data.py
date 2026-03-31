import pandas as pd
import os

COLUMNS = [
    "Date","Enqueteur","Telephone","Commune",
    "Status","Sexe","Age_group","Niveau_cat"
]

FILE_PATH = "data/appels_saisis.csv"

# =========================
# READ
# =========================
def read_data():
    if not os.path.exists(FILE_PATH):
        return pd.DataFrame(columns=COLUMNS), None

    df = pd.read_csv(FILE_PATH, dtype=str)

    # sécuriser colonnes
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]

    # nettoyage
    df["Telephone"] = df["Telephone"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df, None

# =========================
# SAVE
# =========================
def save_data(df):

    df = df.copy()

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]

    df.to_csv(FILE_PATH, index=False)
    return True

# =========================
# ADD ROW SAFE
# =========================
def add_row_safe(row):

    df, _ = read_data()

    # convertir dict → DataFrame
    new_row = pd.DataFrame([row])

    # sécuriser colonnes
    for col in COLUMNS:
        if col not in new_row.columns:
            new_row[col] = ""

    new_row = new_row[COLUMNS]

    # nettoyage téléphone
    new_row["Telephone"] = new_row["Telephone"].astype(str).str.strip()

    # concat
    df = pd.concat([df, new_row], ignore_index=True)

    return save_data(df)