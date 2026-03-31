import pandas as pd
import os

# =========================
# 📂 CHEMIN
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(BASE_DIR, "data", "appels_saisis.csv")
output_path = os.path.join(BASE_DIR, "data", "appels_saisis_clean.csv")

# =========================
# 🔥 NORMALISATION TELEPHONE (FORMAT 225XXXXXXXXX)
# =========================
def normalize_phone(x):
    if pd.isna(x):
        return ""

    x = str(x)

    # garder uniquement chiffres
    x = "".join(c for c in x if c.isdigit())

    # enlever indicatif existant
    if x.startswith("225"):
        x = x[3:]

    # enlever 0 initial
    if x.startswith("0"):
        x = x[1:]

    # vérifier longueur minimale
    if len(x) < 8:
        return ""

    return "225" + x


# =========================
# 🚀 LOAD
# =========================
if not os.path.exists(input_path):
    print("❌ Fichier introuvable :", input_path)
    exit()

df = pd.read_csv(input_path, dtype=str)

print("✅ Fichier chargé")
print("📊 Lignes avant nettoyage :", len(df))

# =========================
# 🧹 TELEPHONE
# =========================
if "Telephone" not in df.columns:
    print("❌ Colonne Telephone absente")
    exit()

df["Telephone"] = df["Telephone"].apply(normalize_phone)

# supprimer numéros invalides
df = df[df["Telephone"] != ""]

# =========================
# 🧹 DATE
# =========================
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 🧹 SUPPRIMER DOUBLONS
# =========================
df = df.drop_duplicates(subset=["Telephone", "Date"])

print("📊 Lignes après nettoyage :", len(df))

# =========================
# 💾 SAVE
# =========================
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
df.to_csv(output_path, index=False)

print("✅ Nettoyage terminé :", output_path)