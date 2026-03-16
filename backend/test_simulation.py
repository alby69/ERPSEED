import json
import pandas as pd
from backend.services.gdo_reconciliation_service import GDOReconciliationService

def simulate_reconciliation():
    # Load simulation data
    df = pd.read_csv("simulation_data.csv", sep=";")

    # Configure with Italian headers mapping
    config = {
        "algorithm": "progressive_balance",
        "tolerance": 0.5,
        "days_window": 5,
        "column_mapping": {
            "Date": "Data",
            "Debit": "Dare",
            "Credit": "Avere",
            "Data Valuta": "Data Valuta"
        }
    }

    # Run Service - Progressive
    service = GDOReconciliationService()
    results = service.process_data(df, config)

    # Run Service - Subset Sum
    config["algorithm"] = "subset_sum"
    results_ss = service.process_data(df, config)

    # Verify Stats
    stats = results["stats"]
    print(f"Coverage Debit: {stats['debit_coverage_perc']:.1f}%")
    print(f"Coverage Credit: {stats['credit_coverage_perc']:.1f}%")
    print(f"Total Matches: {len(results['matches'])}")
    print(f"Total Anomalies: {stats['total_anomalies']}")
    print(f"Subset Sum Coverage: {results_ss['stats']['debit_coverage_perc']:.1f}%")

if __name__ == "__main__":
    simulate_reconciliation()
