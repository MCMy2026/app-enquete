import pandas as pd

def compute_daily_mission(df, quotas):

    if len(df) >= 15:
        return pd.DataFrame([{"Mission": "OK"}])

    def remaining(col, val, target):
        return target - len(df[df[col] == val])

    data = [
        ("Hommes", remaining("Sexe","Homme",quotas["genre"]["hommes"])),
        ("Femmes", remaining("Sexe","Femme",quotas["genre"]["femmes"])),
        ("18-39", remaining("Age_group","18-39",quotas["age"]["jeunes"])),
        ("40-54", remaining("Age_group","40-54",quotas["age"]["moyen"])),
        ("55+", remaining("Age_group","55+",quotas["age"]["senior"])),
    ]

    dfm = pd.DataFrame(data, columns=["Critere","Restant"])
    return dfm[dfm["Restant"] > 0]