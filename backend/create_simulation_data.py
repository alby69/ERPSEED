import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_simulation_data():
    base_date = datetime(2024, 1, 1)

    # Cash movements (Debits)
    debits = []
    for i in range(30):
        # 3 movements per day
        date = base_date + timedelta(days=i//3)
        debits.append({
            "Date": date.strftime("%d/%m/%Y"),
            "Debit": np.random.randint(500, 2000) + 0.50,
            "Credit": 0,
            "Note": f"Incasso Pos {i}"
        })

    # Bank transfers (Credits)
    credits = []
    # Every 2 days we have a cumulative transfer
    for i in range(0, 30, 6):
        date = base_date + timedelta(days=i//3 + 2)
        # Sum of previous 6 debits
        total_debit = sum(d["Debit"] for d in debits[i:i+6])
        credits.append({
            "Date": date.strftime("%d/%m/%Y"),
            "Data Valuta": (date + timedelta(days=1)).strftime("%d/%m/%Y"),
            "Debit": 0,
            "Credit": total_debit,
            "Note": f"Versamento Bancario {i//6}"
        })

    df_debits = pd.DataFrame(debits)
    df_credits = pd.DataFrame(credits)
    df_full = pd.concat([df_debits, df_credits], ignore_index=True)

    df_full.to_csv("simulation_data.csv", index=False, sep=";")
    print("Created simulation_data.csv")

if __name__ == "__main__":
    create_simulation_data()
