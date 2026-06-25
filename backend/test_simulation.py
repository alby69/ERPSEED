import json
import pandas as pd
from backend.services.gdo_reconciliation_service import GDOReconciliationService

def simulate_reconciliation():
    # Load simulation data
    df = pd.read_csv("simulation_data.csv", sep=";")

    # Configure
    config = {
        "algorithm": "progressive_balance",
        "tolerance": 0.5,
        "days_window": 5,
        "column_mapping": {
            "Date": "Date",
            "Debit": "Debit",
            "Credit": "Credit",
            "Data Valuta": "Data Valuta"
        }
    }

    # Run Service
    service = GDOReconciliationService()
    results = service.process_data(df, config)

    # Verify Stats
    stats = results["stats"]
    print(f"Coverage Debit: {stats['debit_coverage_perc']:.1f}%")
    print(f"Coverage Credit: {stats['credit_coverage_perc']:.1f}%")
    print(f"Total Matches: {len(results['matches'])}")
    print(f"Total Anomalies: {stats['total_anomalies']}")

if __name__ == "__main__":
    simulate_reconciliation()
