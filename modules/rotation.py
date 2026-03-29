import pandas as pd

def apply_rotation(df, historique, date):

    if historique.empty:
        return df

    yesterday = pd.to_datetime(date) - pd.Timedelta(days=1)
    last = historique[historique["Date"] == yesterday]["Telephone"]

    df = df[~df["Telephone"].isin(last)]

    return df