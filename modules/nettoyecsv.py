import pandas as pd
import os

# 📂 chemin automatique vers data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "appels_saisis.csv")

df = pd.read_csv(file_path)

# =========================
# 🧹 NETTOYAGE TELEPHONE
# =========================
def clean_phone(x):
    try:
        return str(int(float(x)))
    except:
        return str(x).replace(" ", "").replace(".0", "").strip()

df["Telephone"] = df["Telephone"].apply(clean_phone)

# =========================
# 🧹 DATE
# =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 💾 SAVE
# =========================
output_path = os.path.join(BASE_DIR, "data", "appels_saisis_clean.csv")
df.to_csv(output_path, index=False)

print("✅ Nettoyage terminé :", output_path)