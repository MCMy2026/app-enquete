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
# 📥 LECTURE ULTRA SAFE
# =========================
def read_data():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(FILE_PATH):
        print("🆕 Création fichier CSV propre")
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE_PATH, index=False, encoding="utf-8-sig")
        return df, None

    try:
        df = pd.read_csv(FILE_PATH, dtype=str, encoding="utf-8-sig")
        print("✅ CSV chargé :", len(df), "lignes")
    except Exception as e:
        print("💥 ERREUR LECTURE CSV :", e)
        df = pd.DataFrame(columns=COLUMNS)

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
# 💾 ÉCRITURE ULTRA SAFE
# =========================
def save_data(df):
    try:
        temp_path = FILE_PATH + ".tmp"

        # écrire dans fichier temporaire
        df.to_csv(temp_path, index=False, encoding="utf-8-sig")

        # remplacer original (safe)
        os.replace(temp_path, FILE_PATH)

        print("✅ CSV sauvegardé :", len(df), "lignes")
        return True

    except Exception as e:
        print("💥 ERREUR SAVE :", e)
        return False


# =========================
# ➕ AJOUT ULTRA ROBUSTE
# =========================
def add_row_safe(row):
    print("📥 Ajout en cours...")

    df, _ = read_data()

    new_row = pd.DataFrame([row])

    # compléter colonnes
    for col in COLUMNS:
        if col not in new_row.columns:
            new_row[col] = ""

    new_row = new_row[COLUMNS]

    # normalisation
    new_row["Telephone"] = new_row["Telephone"].apply(normalize_phone)

    print("📦 Nouvelle ligne :", new_row.to_dict(orient="records"))

    # concat
    df = pd.concat([df, new_row], ignore_index=True)

    print("📊 Total lignes après ajout :", len(df))

    return save_data(df)