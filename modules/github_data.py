import pandas as pd
import os

FILE_PATH = "data/appels_saisis.csv"

COLUMNS = [
    "Date","Enqueteur","Telephone","Commune",
    "Status","Sexe","Age_group","Niveau_cat"
]

# =========================
# 🔥 NORMALISATION ULTRA ROBUSTE
# =========================
def normalize_phone(x):
    if pd.isna(x):
        return ""

    x = str(x)

    # garder uniquement les chiffres
    x = "".join(c for c in x if c.isdigit())

    # supprimer indicatif pays (225)
    if x.startswith("225"):
        x = x[3:]

    # corriger longueur
    if len(x) > 10 and x.startswith("0"):
        x = x[1:]

    return x


# =========================
# 📥 READ DATA
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
    df["Telephone"] = df["Telephone"].apply(normalize_phone)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df, None


# =========================
# 💾 SAVE DATA
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
# ➕ ADD ROW SAFE
# =========================
def add_row_safe(row):

    df, _ = read_data()

    new_row = pd.DataFrame([row])

    for col in COLUMNS:
        if col not in new_row.columns:
            new_row[col] = ""

    new_row = new_row[COLUMNS]

    # normalisation critique
    new_row["Telephone"] = new_row["Telephone"].apply(normalize_phone)

    df = pd.concat([df, new_row], ignore_index=True)

    return save_data(df)