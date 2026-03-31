import pandas as pd
import os

# =========================
# 🔥 NORMALISATION TELEPHONE (FORMAT 225XXXXXXXXX)
# =========================
def normalize_phone(x):
    if pd.isna(x):
        return ""

    x = str(x)
    x = "".join(c for c in x if c.isdigit())

    # enlever indicatif existant
    if x.startswith("225"):
        x = x[3:]

    # enlever 0 initial
    if x.startswith("0"):
        x = x[1:]

    # ajouter indicatif
    return "225" + x


# =========================
# 🚀 NETTOYAGE BASE
# =========================
def clean_base():

    input_file = "data/base_appels.xlsx"
    output_file = "data/base_appels_clean.xlsx"

    if not os.path.exists(input_file):
        print("❌ Fichier introuvable :", input_file)
        return

    df = pd.read_excel(input_file)

    print("✅ Fichier chargé")
    print("Colonnes avant:", df.columns.tolist())

    # =========================
    # 🔥 NORMALISER COLONNES
    # =========================
    df = df.rename(columns={
        "telephone": "Telephone",
        "tel": "Telephone",
        "COMMUNE": "Commune",
        "commune": "Commune",
        "sexe": "Sexe",
        "age": "Age_group",
        "niveau": "Niveau_cat"
    })

    # =========================
    # 🔥 NETTOYAGE TEXTE
    # =========================
    for col in ["Commune", "Sexe", "Age_group", "Niveau_cat"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # =========================
    # 🔥 TELEPHONE
    # =========================
    if "Telephone" not in df.columns:
        print("❌ Colonne Telephone absente")
        return

    df["Telephone"] = df["Telephone"].apply(normalize_phone)

    # =========================
    # 🔥 SUPPRIMER DOUBLONS
    # =========================
    df = df.drop_duplicates(subset=["Telephone"])

    print("📊 Nb lignes après clean:", len(df))

    # =========================
    # 💾 SAVE
    # =========================
    os.makedirs("data", exist_ok=True)
    df.to_excel(output_file, index=False)

    print("✅ Base nettoyée créée :", output_file)


if __name__ == "__main__":
    clean_base()