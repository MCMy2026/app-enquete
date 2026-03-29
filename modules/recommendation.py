import pandas as pd

# 🎯 Message intelligent terrain
def build_recommendation_message(kpis):

    # 🔒 sécurité
    if kpis is None or kpis.empty:
        return "⚠️ Aucun KPI disponible"

    if "Statut" not in kpis.columns or "Critere" not in kpis.columns:
        return "⚠️ Structure KPI invalide"

    needs = kpis[kpis["Statut"] == "⚠️ Manque"]["Critere"].tolist()

    if not needs:
        return "✅ Tous les quotas sont équilibrés"

    # 🔥 message terrain optimisé
    return "🎯 Priorité : appeler " + " + ".join(needs)


# 🤖 Recommandation intelligente de panélistes
def recommend_panelists(df_pool, df_called, kpis):

    df = df_pool.copy()

    # 🔒 sécurité
    if df.empty:
        return df

    # ✅ 1. Limite 2 appels par téléphone
    if not df_called.empty:
        calls = df_called.groupby("Telephone").size().reset_index(name="nb")
        df = df.merge(calls, on="Telephone", how="left")
        df["nb"] = df["nb"].fillna(0)
    else:
        df["nb"] = 0

    df = df[df["nb"] < 2]

    # ❌ si plus personne dispo
    if df.empty:
        return df

    # 🎯 2. Priorisation selon KPI (intelligent)
    if kpis is not None and not kpis.empty and "Statut" in kpis.columns:

        needs = kpis[kpis["Statut"] == "⚠️ Manque"]["Critere"].tolist()

        for need in needs:

            if "Femme" in need:
                df = df[df["Sexe"] == "Femme"]

            if "Homme" in need:
                df = df[df["Sexe"] == "Homme"]

            if "18-39" in need:
                df = df[df["Age_group"] == "18-39"]

            if "40-54" in need:
                df = df[df["Age_group"] == "40-54"]

            if "55+" in need:
                df = df[df["Age_group"] == "55+"]

            if "superieur" in need:
                df = df[df["Niveau_cat"] == "superieur"]

            if "inferieur" in need:
                df = df[df["Niveau_cat"] == "inferieur"]

    # 🔄 fallback si filtre trop strict
    if df.empty:
        df = df_pool.copy()

    # 🎲 3. Sélection aléatoire contrôlée
    return df.sample(min(5, len(df)))