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
        self.search_direction = "past_only"
        self.enable_best_fit = True
        self.valuta_date_column = "Data Valuta"

    def process_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for "on-the-fly" processing.
        """
        # Apply config
        tolerance = config.get("tolerance", 0.5)
        self.days_window = config.get("days_window", 5)
        self.algorithm = config.get("algorithm", "progressive_balance")
        self.search_direction = config.get("search_direction", "past_only")
        self.enable_best_fit = config.get("enable_best_fit", True)
        self.valuta_date_column = config.get("valuta_date_column", "Data Valuta")

        # Internal cent conversion
        self.tolerance = int(tolerance * 100)

        # Clean and Prepare using generic FileProcessingService
        # Mapping: Rename source columns (e.g., 'Data') to internal names ('Date')
        mapping = config.get("column_mapping", {})
        # Flip mapping for pandas rename if needed, but let's assume config is {source: target}
        # Based on review, config was {internal: source}, so we invert it:
        inverted_mapping = {v: k for k, v in mapping.items()}
        df = FileProcessingService.apply_mapping(df, inverted_mapping)

        # Ensure Date
        date_col = "Date"
        df = FileProcessingService.standardize_dates(df, [date_col, self.valuta_date_column])

        # Ensure Dare/Avere (to cents)
        debit_col = "Debit"
        credit_col = "Credit"
        df = FileProcessingService.clean_numeric(df, [debit_col, credit_col], to_cents=True)

        df["orig_index"] = df.index

        # Separate
        debit_df, credit_df = self._separate_movements(df)

        # Run Algorithm
        matches = []
        if self.algorithm == "progressive_balance":
            matches = self._reconcile_progressive_balance(debit_df, credit_df)
        elif self.algorithm == "subset_sum":
            matches = self._reconcile_subset_sum(debit_df, credit_df)
        elif self.algorithm == "greedy_amount_first":
            matches = self._reconcile_greedy_amount_first(debit_df, credit_df)

        # Residual Recovery
        if config.get("enable_residual_recovery", True):
            matches = self._reconcile_residual_recovery(matches, debit_df, credit_df)

        # Stats
        stats = self._calculate_stats(debit_df, credit_df, matches)

        # Convert all timestamps to strings for JSON serialization
        def sanitize(obj):
            if isinstance(obj, list): return [sanitize(x) for x in obj]
            if isinstance(obj, dict): return {k: sanitize(v) for k, v in obj.items()}
            if hasattr(obj, 'isoformat'): return obj.isoformat()
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if pd.isna(obj): return None
            return obj

        return sanitize({
            "matches": matches,
            "stats": stats,
            "unreconciled_debit": debit_df[~debit_df["used"]].to_dict("records"),
            "unreconciled_credit": credit_df[~credit_df["used"]].to_dict("records")
        })

    def _reconcile_subset_sum(self, debit_df, credit_df):
        """
        Many-to-one matching using subset sum strategy.
        Supports Past/Future search and Best Fit (splitting).
        """
        matches = []
        used_debit_indices = set()

        debit_rows = debit_df.to_dict("records")
        credit_rows = credit_df.to_dict("records")

        debit_col = "Debit"
        credit_col = "Credit"

        for c_idx, c_row in enumerate(credit_rows):
            target = c_row[credit_col]
            ref_date = c_row["effective_date"]

            if pd.isna(ref_date): continue

            # Direction logic
            if self.search_direction == "past_only":
                min_date = ref_date - pd.Timedelta(days=self.days_window)
                max_date = ref_date
            elif self.search_direction == "future_only":
                min_date = ref_date
                max_date = ref_date + pd.Timedelta(days=self.days_window)
            else: # both
                min_date = ref_date - pd.Timedelta(days=self.days_window)
                max_date = ref_date + pd.Timedelta(days=self.days_window)

            # Candidates in window (filtered by month/year for December valuta logic)
            candidates = []
            for d in debit_rows:
                if d["orig_index"] in used_debit_indices: continue
                d_date = d["analysis_date"]
                if pd.isna(d_date): continue

                # December valuta logic: don't match Jan debits with Dec valuta
                if ref_date.month == 12 and d_date.year > ref_date.year: continue

                if min_date <= d_date <= max_date:
                    candidates.append(d)

            # Subset Sum Logic
            current_match_debits = []
            running_sum = 0

            # Sort candidates by amount
            candidates.sort(key=lambda x: x[debit_col], reverse=True)

            for d in candidates:
                if d["orig_index"] in used_debit_indices: continue

                if running_sum + d[debit_col] <= target + self.tolerance:
                    running_sum += d[debit_col]
                    current_match_debits.append(d)

                    if abs(target - running_sum) <= self.tolerance:
                        break

            # Best Fit logic (if enabled and no exact match found)
            if not (current_match_debits and abs(target - running_sum) <= self.tolerance) and self.enable_best_fit:
                # We already have a "best greedy fit" in current_match_debits
                pass

            if current_match_debits:
                is_exact = abs(target - running_sum) <= self.tolerance
                if is_exact or self.enable_best_fit:
                    credit_rows[c_idx]["used"] = True
                    for d in current_match_debits:
                        used_debit_indices.add(d["orig_index"])

                    matches.append({
                        "credit": c_row,
                        "debits": current_match_debits,
                        "difference": target - running_sum,
                        "match_type": "SubsetSum-Greedy" + (" (Best Fit)" if not is_exact else "")
                    })

        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        credit_df["used"] = [r["used"] for r in credit_rows]
        return matches

    def _reconcile_greedy_amount_first(self, debit_df, credit_df):
        """
        Greedy algorithm: match largest items first, regardless of sequential order.
        """
        matches = []
        used_debit_indices = set()
        used_credit_indices = set()

        debit_rows = sorted(debit_df.to_dict("records"), key=lambda x: x["Debit"], reverse=True)
        credit_rows = sorted(credit_df.to_dict("records"), key=lambda x: x["Credit"], reverse=True)

        for c_row in credit_rows:
            target = c_row["Credit"]
            ref_date = c_row["effective_date"]

            # Simple 1-to-1 greedy
            best_d = None
            best_diff = self.tolerance + 1

            min_date = ref_date - pd.Timedelta(days=self.days_window)
            max_date = ref_date + pd.Timedelta(days=self.days_window)

            for d_row in debit_rows:
                if d_row["orig_index"] in used_debit_indices: continue
                if not (min_date <= d_row["Date"] <= max_date): continue

                diff = abs(target - d_row["Debit"])
                if diff <= self.tolerance and diff < best_diff:
                    best_d = d_row
                    best_diff = diff

            if best_d:
                used_debit_indices.add(best_d["orig_index"])
                used_credit_indices.add(c_row["orig_index"])
                matches.append({
                    "credit": c_row,
                    "debits": [best_d],
                    "difference": target - best_d["Debit"],
                    "match_type": "Greedy-1to1"
                })

        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        credit_df["used"] = credit_df["orig_index"].isin(used_credit_indices)
        return matches

    def _reconcile_residual_recovery(self, matches, debit_df, credit_df):
        """
        Try to match differences from forced blocks with unused movements.
        """
        used_debit_indices = set(debit_df[debit_df["used"]]["orig_index"])
        used_credit_indices = set(credit_df[credit_df["used"]]["orig_index"])

        unused_debits = debit_df[~debit_df["used"]].to_dict("records")

        for m in matches:
            if m.get("is_forced") and m["difference"] > self.tolerance:
                # Try to find an unused debit that matches the difference
                target = m["difference"]
                for d in unused_debits:
                    if d["orig_index"] in used_debit_indices: continue
                    if abs(d["Debit"] - target) <= self.tolerance:
                        m["debits"].append(d)
                        m["difference"] -= d["Debit"]
                        m["match_type"] += " (Recovered)"
                        m["is_forced"] = False
                        used_debit_indices.add(d["orig_index"])
                        break

        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        return matches

    def _separate_movements(self, df: pd.DataFrame):
        debit_col = "Debit"
        credit_col = "Credit"

        debit_df = df[df[debit_col] > 0].copy()
        credit_df = df[df[credit_col] > 0].copy()

        debit_df["used"] = False
        credit_df["used"] = False

        # effective_date for Credits (Data Valuta)
        valuta_col = self.valuta_date_column
        if valuta_col in credit_df.columns:
             credit_df["effective_date"] = credit_df[valuta_col].combine_first(credit_df["Date"])
        else:
             credit_df["effective_date"] = credit_df["Date"]

        # analysis_date for sorting
        credit_df["analysis_date"] = credit_df["effective_date"]
        debit_df["analysis_date"] = debit_df["Date"]

        return debit_df.sort_values("analysis_date"), credit_df.sort_values("analysis_date")

    def _reconcile_progressive_balance(self, debit_df, credit_df):
        matches = []
        used_debit_indices = set()

        debit_rows = debit_df.to_dict("records")
        credit_rows = credit_df.to_dict("records")

        debit_col = "Debit"
        credit_col = "Credit"

        for c_idx, c_row in enumerate(credit_rows):
            credit_amount = c_row[credit_col]
            credit_date = c_row["analysis_date"]

            if pd.isna(credit_date): continue

            min_date = credit_date - pd.Timedelta(days=self.days_window)
            max_date = credit_date + pd.Timedelta(days=self.days_window)

            # Period skip logic (from riconcilia_casse)
            # Find all available debits in window to check month compatibility
            candidates_in_window = [d for d in debit_rows if d["orig_index"] not in used_debit_indices
                                    and not pd.isna(d["analysis_date"])
                                    and min_date <= d["analysis_date"] <= max_date]

            if candidates_in_window:
                first_d_date = candidates_in_window[0]["analysis_date"]
                if credit_date.year < first_d_date.year or (credit_date.year == first_d_date.year and credit_date.month < first_d_date.month):
                    # Skip: credit is from previous month compared to available debits
                    matches.append({
                        "credit": c_row,
                        "debits": [],
                        "difference": credit_amount,
                        "match_type": "VERSAMENTO MESE PRECEDENTE",
                        "is_forced": True
                    })
                    credit_rows[c_idx]["used"] = True
                    continue
            elif not candidates_in_window:
                 # No debits at all in window
                 matches.append({
                        "credit": c_row,
                        "debits": [],
                        "difference": credit_amount,
                        "match_type": "VERSAMENTO SENZA INCASSI",
                        "is_forced": True
                    })
                 credit_rows[c_idx]["used"] = True
                 continue

            current_match_debits = []
            remaining_credit = credit_amount

            for d in candidates_in_window:
                d_amount = d[debit_col]
                # In progressive balance we take what we find until balance or end of window
                current_match_debits.append(d)
                used_debit_indices.add(d["orig_index"])
                remaining_credit -= d_amount

                if abs(remaining_credit) <= self.tolerance:
                    break

            if current_match_debits:
                credit_rows[c_idx]["used"] = True
                matches.append({
                    "credit": c_row,
                    "debits": current_match_debits,
                    "difference": remaining_credit,
                    "match_type": "Progressive"
                })

        # Update original DFs
        debit_df["used"] = debit_df["orig_index"].isin(used_debit_indices)
        credit_df["used"] = [r["used"] for r in credit_rows]

        return matches

    def save_results(self, project_id: int, company_id: Optional[int], results: Dict[str, Any]) -> int:
        """
        Persist reconciliation results (Session and Matches) to dynamic tables.
        """
        from ..utils import get_table_object
        from sqlalchemy import insert, select
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
        debit_col = "Debit"
        credit_col = "Credit"

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
