import pandas as pd
import os

FILE_PATH = "data/appels_saisis.csv"

COLUMNS = [
    "Date","Enqueteur","Telephone","Commune",
    "Status","Sexe","Age_group","Niveau_cat"
]

# =========================
# 🔥 NORMALISATION TELEPHONE
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
# 📥 READ
# =========================
def read_data():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE_PATH, index=False)
        return df, None

    df = pd.read_csv(FILE_PATH, dtype=str)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNS]
    df["Telephone"] = df["Telephone"].apply(normalize_phone)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df, None


# =========================
# 💾 SAVE
# =========================
def save_data(df):
    try:
        df.to_csv(FILE_PATH, index=False)
        return True
    except Exception as e:
        print("❌ SAVE ERROR:", e)
        return False


# =========================
# ➕ ADD
# =========================
def add_row_safe(row):
    df, _ = read_data()

    new_row = pd.DataFrame([row])

    for col in COLUMNS:
        if col not in new_row.columns:
            new_row[col] = ""

    new_row = new_row[COLUMNS]

    new_row["Telephone"] = new_row["Telephone"].apply(normalize_phone)

    df = pd.concat([df, new_row], ignore_index=True)

    return save_data(df)