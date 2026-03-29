import pandas as pd

def compute_performance(df):

    if df.empty:
        return pd.DataFrame()

    results = []

    for enq in df["Enqueteur"].unique():

        sub = df[df["Enqueteur"] == enq]

        total = len(sub)
        success = len(sub[sub["Status"] == "Répondu"])

        taux = success / total if total else 0
        fail = total - success

        penalite = fail / total if total else 0

        score = (taux * 0.6) + ((1 - penalite) * 0.2) + (total / 100 * 0.2)

        results.append({
            "Enqueteur": enq,
            "Appels": total,
            "Réussis": success,
            "Taux (%)": round(taux*100,1),
            "Score": round(score*100,1)
        })

    return pd.DataFrame(results).sort_values(by="Score", ascending=False)