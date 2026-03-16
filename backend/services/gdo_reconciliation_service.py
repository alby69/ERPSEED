import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base import BaseService
from .file_processing_service import FileProcessingService

class GDOReconciliationService(BaseService):
    """
    Service for GDO Cash Reconciliation.
    Ports and enhances logic from riconcilia_casse.
    """

    def __init__(self, db=None):
        super().__init__(db)
        self.tolerance = 50  # cents
        self.days_window = 5
        self.algorithm = "progressive_balance"

    def process_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for "on-the-fly" processing.
        """
        # Apply config
        tolerance = config.get("tolerance", 0.5)
        days_window = config.get("days_window", 5)
        algorithm = config.get("algorithm", "progressive_balance")

        # Internal cent conversion
        self.tolerance = int(tolerance * 100)
        self.days_window = days_window

        # Clean and Prepare using generic FileProcessingService
        mapping = config.get("column_mapping", {})
        df = FileProcessingService.apply_mapping(df, mapping)

        # Ensure Date
        date_col = "Date" if "Date" in df.columns else df.columns[0]
        df = FileProcessingService.standardize_dates(df, [date_col, "Data Valuta"])

        # Ensure Dare/Avere (to cents)
        debit_col = "Debit" if "Debit" in df.columns else "Dare"
        credit_col = "Credit" if "Credit" in df.columns else "Avere"
        df = FileProcessingService.clean_numeric(df, [debit_col, credit_col], to_cents=True)

        df["orig_index"] = df.index

        # Separate
        debit_df, credit_df = self._separate_movements(df)

        # Run Algorithm
        matches = []
        if algorithm == "progressive_balance":
            matches = self._reconcile_progressive_balance(debit_df, credit_df)
        elif algorithm == "subset_sum":
            matches = self._reconcile_subset_sum(debit_df, credit_df)

        # Stats
        stats = self._calculate_stats(debit_df, credit_df, matches)

        return {
            "matches": matches,
            "stats": stats,
            "unreconciled_debit": debit_df[~debit_df["used"]].to_dict("records"),
            "unreconciled_credit": credit_df[~credit_df["used"]].to_dict("records")
        }

    def _reconcile_subset_sum(self, debit_df, credit_df):
        """
        Variation of matching: look for subsets of debits that sum up exactly
        to a credit, prioritizing smaller subsets.
        """
        matches = []
        used_debit_indices = set()

        debit_rows = debit_df.to_dict("records")
        credit_rows = credit_df.to_dict("records")

        debit_col = "Debit" if "Debit" in debit_df.columns else "Dare"
        credit_col = "Credit" if "Credit" in credit_df.columns else "Avere"

        for c_idx, c_row in enumerate(credit_rows):
            target = c_row[credit_col]
            credit_date = c_row["analysis_date"]

            if pd.isna(credit_date): continue

            min_date = credit_date - pd.Timedelta(days=self.days_window)
            max_date = credit_date + pd.Timedelta(days=self.days_window)

            # Candidates in window
            candidates = [d for d in debit_rows if d["orig_index"] not in used_debit_indices
                          and not pd.isna(d["analysis_date"])
                          and min_date <= d["analysis_date"] <= max_date]

            # Simple greedy subset sum for now (can be improved to real subset sum if needed)
            # but more strict than progressive balance
            current_match_debits = []
            running_sum = 0

            # Sort candidates by amount to try and find exact matches with few movements
            candidates.sort(key=lambda x: x[debit_col], reverse=True)

            for d in candidates:
                if d["orig_index"] in used_debit_indices: continue

                if running_sum + d[debit_col] <= target + self.tolerance:
                    running_sum += d[debit_col]
                    current_match_debits.append(d)

                    if abs(target - running_sum) <= self.tolerance:
                        break

            if current_match_debits and abs(target - running_sum) <= self.tolerance:
                credit_rows[c_idx]["used"] = True
                for d in current_match_debits:
                    used_debit_indices.add(d["orig_index"])

                matches.append({
                    "credit": c_row,
                    "debits": current_match_debits,
                    "difference": target - running_sum,
                    "match_type": "SubsetSum-Greedy"
                })

        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        credit_df["used"] = [r["used"] for r in credit_rows]
        return matches

    def _separate_movements(self, df: pd.DataFrame):
        # We assume clean_numeric renamed or we use the resolved names
        debit_col = "Debit" if "Debit" in df.columns else "Dare"
        credit_col = "Credit" if "Credit" in df.columns else "Avere"

        debit_df = df[df[debit_col] > 0].copy()
        credit_df = df[df[credit_col] > 0].copy()

        debit_df["used"] = False
        credit_df["used"] = False

        # Data Valuta handling
        if "Data Valuta" in credit_df.columns:
             credit_df["analysis_date"] = credit_df["Data Valuta"].combine_first(credit_df["Date"])
        else:
             credit_df["analysis_date"] = credit_df["Date"]

        debit_df["analysis_date"] = debit_df["Date"]

        return debit_df.sort_values("analysis_date"), credit_df.sort_values("analysis_date")

    def _reconcile_progressive_balance(self, debit_df, credit_df):
        matches = []
        used_debit_indices = set()

        debit_rows = debit_df.to_dict("records")
        credit_rows = credit_df.to_dict("records")

        debit_col = "Debit" if "Debit" in debit_df.columns else "Dare"
        credit_col = "Credit" if "Credit" in credit_df.columns else "Avere"

        for c_idx, c_row in enumerate(credit_rows):
            credit_amount = c_row[credit_col]
            credit_date = c_row["analysis_date"]

            if pd.isna(credit_date):
                continue

            min_date = credit_date - pd.Timedelta(days=self.days_window)
            max_date = credit_date + pd.Timedelta(days=self.days_window)

            current_match_debits = []
            remaining_credit = credit_amount

            # Find candidate debits
            for d_idx, d_row in enumerate(debit_rows):
                if d_row["orig_index"] in used_debit_indices:
                    continue

                if not pd.isna(d_row["analysis_date"]) and min_date <= d_row["analysis_date"] <= max_date:
                    d_amount = d_row[debit_col]

                    if d_amount <= remaining_credit + self.tolerance:
                        current_match_debits.append(d_row)
                        used_debit_indices.add(d_row["orig_index"])
                        remaining_credit -= d_amount
                        debit_rows[d_idx]["used"] = True

                        if abs(remaining_credit) <= self.tolerance:
                            break

            if current_match_debits:
                credit_rows[c_idx]["used"] = True
                match = {
                    "credit": c_row,
                    "debits": current_match_debits,
                    "difference": remaining_credit,
                    "match_type": "Progressive"
                }
                matches.append(match)

        # Update original DFs
        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        credit_df["used"] = [r["used"] for r in credit_rows]

        return matches

    def save_results(self, project_id: int, company_id: Optional[int], results: Dict[str, Any]) -> int:
        """
        Persist reconciliation results (Session and Matches) to dynamic tables.
        """
        from ..utils import get_table_object
        from sqlalchemy import insert
        import json

        schema_name = f"project_{project_id}"
        session_table = get_table_object("gdo_session", schema=schema_name)
        match_table = get_table_object("gdo_match", schema=schema_name)
        movement_table = get_table_object("gdo_movement", schema=schema_name)

        # 1. Ensure Company exists or fallback
        if not company_id:
            company_table = get_table_object("gdo_company", schema=schema_name)
            first_company = self.db.session.execute(select(company_table.c.id)).first()
            if first_company:
                company_id = first_company.id
            else:
                # Create a default company
                stmt_c = insert(company_table).values({"name": "Azienda Default"}).returning(company_table.c.id)
                company_id = self.db.session.execute(stmt_c).scalar()

        # Ensure Store exists
        store_table = get_table_object("gdo_store", schema=schema_name)
        first_store = self.db.session.execute(select(store_table.c.id)).first()
        if first_store:
            store_id = first_store.id
        else:
            stmt_s = insert(store_table).values({
                "company_id": company_id,
                "name": "Punto Vendita 1",
                "code": "PV01"
            }).returning(store_table.c.id)
            store_id = self.db.session.execute(stmt_s).scalar()

        # 1. Create Session
        session_data = {
            "company_id": company_id,
            "date": datetime.now(),
            "algorithm": self.algorithm,
            "params": json.dumps({"tolerance": self.tolerance, "days_window": self.days_window}),
            "stats": json.dumps(results.get("stats", {}))
        }

        stmt = insert(session_table).values(session_data).returning(session_table.c.id)
        session_id = self.db.session.execute(stmt).scalar()

        # 2. Create Matches and Link Movements
        for m in results.get("matches", []):
            match_data = {
                "session_id": session_id,
                "match_type": m.get("match_type", "Standard"),
                "difference": float(m.get("difference", 0)) / 100,
                "notes": f"Match with {len(m.get('debits', []))} movements"
            }
            stmt_match = insert(match_table).values(match_data).returning(match_table.c.id)
            match_id = self.db.session.execute(stmt_match).scalar()

            # Link Credit Movement
            credit = m["credit"]
            credit_data = {
                "session_id": session_id,
                "match_id": match_id,
                "date": pd.to_datetime(credit["Date"]).to_pydatetime() if "Date" in credit else None,
                "credit": float(credit.get("Credit", 0)) / 100,
                "valuta_date": pd.to_datetime(credit["Data Valuta"]).to_pydatetime() if "Data Valuta" in credit and not pd.isna(credit["Data Valuta"]) else None,
                "description": credit.get("Descrizione", "Versamento")
            }
            # We use the store_id resolved above
            credit_data["store_id"] = store_id
            self.db.session.execute(insert(movement_table).values(credit_data))

            # Link Debit Movements
            for d in m.get("debits", []):
                debit_data = {
                    "session_id": session_id,
                    "match_id": match_id,
                    "date": pd.to_datetime(d["Date"]).to_pydatetime() if "Date" in d else None,
                    "debit": float(d.get("Debit", 0)) / 100,
                    "description": d.get("Descrizione", "Incasso"),
                    "store_id": store_id
                }
                self.db.session.execute(insert(movement_table).values(debit_data))

        self.db.session.commit()
        return session_id

    def _calculate_stats(self, debit_df, credit_df, matches):
        debit_col = "Debit" if "Debit" in debit_df.columns else "Dare"
        credit_col = "Credit" if "Credit" in credit_df.columns else "Avere"

        tot_debit = debit_df[debit_col].sum()
        used_debit = debit_df[debit_df["used"]][debit_col].sum()

        tot_credit = credit_df[credit_col].sum()
        used_credit = credit_df[credit_df["used"]][credit_col].sum()

        # Monthly trend
        monthly_trend = []
        if not debit_df.empty or not credit_df.empty:
            debit_df['month'] = debit_df['Date'].dt.to_period('M').astype(str)
            monthly_debit = debit_df.groupby('month')[debit_col].sum()

            credit_df['month'] = credit_df['Date'].dt.to_period('M').astype(str)
            monthly_credit = credit_df.groupby('month')[credit_col].sum()

            all_months = sorted(list(set(monthly_debit.index) | set(monthly_credit.index)))
            for m in all_months:
                monthly_trend.append({
                    'month': m,
                    'debit': int(monthly_debit.get(m, 0)) / 100,
                    'credit': int(monthly_credit.get(m, 0)) / 100
                })

        return {
            "debit_coverage_perc": (used_debit / tot_debit * 100) if tot_debit > 0 else 0,
            "credit_coverage_perc": (used_credit / tot_credit * 100) if tot_credit > 0 else 0,
            "total_anomalies": sum(1 for m in matches if abs(m["difference"]) > self.tolerance),
            "total_difference": (used_debit - used_credit) / 100,
            "monthly_trend": monthly_trend
        }
