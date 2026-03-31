import pandas as pd

def normalize_phone(x):
    if pd.isna(x):
        return ""

    x = str(x)
    x = "".join(c for c in x if c.isdigit())

    if x.startswith("225"):
        x = x[3:]

    return x


def clean_base():

    df = pd.read_excel("data/base_appels.xlsx")

    print("Colonnes avant:", df.columns.tolist())

    # 🔥 RENOMMER COLONNES
    df = df.rename(columns={
        "telephone": "Telephone",
        "tel": "Telephone",
        "COMMUNE": "Commune",
        "commune": "Commune",
        "age": "Age_group",
        "niveau": "Niveau_cat",
        "sexe": "Sexe"
    })

    # 🔥 NETTOYAGE TEXTE
    for col in ["Commune", "Sexe", "Age_group", "Niveau_cat"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 🔥 NORMALISATION TELEPHONE
    df["Telephone"] = df["Telephone"].apply(normalize_phone)

    # 🔥 SUPPRIMER DOUBLONS
    df = df.drop_duplicates(subset=["Telephone"])

    print("Nb après nettoyage:", len(df))

    # 💾 SAVE
    df.to_excel("data/base_appels_clean.xlsx", index=False)

    print("✅ Base nettoyée sauvegardée")