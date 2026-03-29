import pandas as pd

def compute_quota_kpis(df, quotas):

    if df.empty:
        return pd.DataFrame()

    results = []

    def count(col, val):
        return len(df[df[col] == val])

    mapping = [
        ("Hommes", count("Sexe","Homme"), quotas["genre"]["hommes"]),
        ("Femmes", count("Sexe","Femme"), quotas["genre"]["femmes"]),
        ("18-39", count("Age_group","18-39"), quotas["age"]["jeunes"]),
        ("40-54", count("Age_group","40-54"), quotas["age"]["moyen"]),
        ("55+", count("Age_group","55+"), quotas["age"]["senior"]),
        ("Niveau inférieur", count("Niveau_cat","inferieur"), quotas["niveau"]["inferieur"]),
        ("Niveau supérieur", count("Niveau_cat","superieur"), quotas["niveau"]["superieur"]),
    ]

    for name, real, target in mapping:
        status = "✅ OK" if real == target else ("⚠️ Manque" if real < target else "❌ Dépassé")

        results.append({
            "Critere": name,
            "Attendu": target,
            "Realisé": real,
            "Statut": status
        })

    return pd.DataFrame(results)