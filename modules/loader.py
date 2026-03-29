import pandas as pd

def load_base_appels(path="data/base_appels.xlsx"):
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        print("Erreur chargement base_appels :", e)
        return pd.DataFrame()


def load_appels_saisis(path="data/appels_saisis.csv"):
    try:
        df = pd.read_csv(path)
        return df
    except:
        return pd.DataFrame(columns=[
            "Date","Enqueteur","Telephone","Commune","Status",
            "Sexe","Age_group","Niveau_cat"
        ])