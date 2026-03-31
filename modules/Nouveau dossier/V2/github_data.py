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

    # enlever indicatif pays
    if x.startswith("225"):
        x = x[3:]

    return x


# =========================
# 📥 READ DATA
# =========================
def read_data():
    try:
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(FILE_PATH):
            print("⚠️ Fichier inexistant -> création")
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(FILE_PATH, index=False)
            return df, None

        df = pd.read_csv(FILE_PATH, dtype=str)

        # sécuriser colonnes
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""

        df = df[COLUMNS]

        # nettoyage
        df["Telephone"] = df["Telephone"].apply(normalize_phone)

        return df, None

    except Exception as e:
        print("❌ ERREUR READ:", e)
        return pd.DataFrame(columns=COLUMNS), str(e)


# =========================
# 💾 SAVE DATA
# =========================
def save_data(df):
    try:
        os.makedirs("data", exist_ok=True)

        df = df.copy()

        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""

        df = df[COLUMNS]

        df.to_csv(FILE_PATH, index=False)

        print("✅ SAVE OK ->", FILE_PATH)
        return True

    except Exception as e:
        print("❌ ERREUR SAVE:", e)
        return False


# =========================
# ➕ ADD ROW SAFE
# =========================
def add_row_safe(row):
    try:
        print("📥 AJOUT LIGNE:", row)

        df, err = read_data()

        if err:
            print("❌ ERREUR READ:", err)
            return False

        new_row = pd.DataFrame([row])

        for col in COLUMNS:
            if col not in new_row.columns:
                new_row[col] = ""

        new_row = new_row[COLUMNS]

        new_row["Telephone"] = new_row["Telephone"].apply(normalize_phone)

        df = pd.concat([df, new_row], ignore_index=True)

        print("📊 DF APRÈS AJOUT:")
        print(df.tail())

        return save_data(df)

    except Exception as e:
        print("❌ ERREUR ADD:", e)
        return False
    
    