import pandas as pd
import io
from datetime import datetime

class GDOExcelReporter:
    """
    Enhanced Excel Reporter for GDO Reconciliation.
    Provides clearer sheets and better formatting than the original.
    """

    def generate_report(self, results):
        output = io.BytesIO()

        # We use XlsxWriter as engine for better formatting
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Formats
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
            money_fmt = workbook.add_format({'num_format': '#,##0.00 €'})
            date_fmt = workbook.add_format({'num_format': 'dd/mm/yyyy'})

            # 1. Summary Sheet
            summary_data = [
                ['Metric', 'Value'],
                ['Copertura Incassi', f"{results['stats']['debit_coverage_perc']:.1f}%"],
                ['Copertura Versamenti', f"{results['stats']['credit_coverage_perc']:.1f}%"],
                ['Totale Anomalie', results['stats']['total_anomalies']],
                ['Differenza Totale', results['stats']['total_difference'] / 100]
            ]
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Riepilogo', index=False, header=False)

            # 2. Matches Sheet
            flat_matches = []
            for m in results['matches']:
                flat_matches.append({
                    'Data Versamento': m['credit']['analysis_date'],
                    'Importo Versato': m['credit']['Credit'] / 100,
                    'Incassi Collegati': ", ".join([str(d['Debit']/100) for d in m['debits']]),
                    'Totale Incassi': sum(d['Debit'] for d in m['debits']) / 100,
                    'Differenza': m['difference'] / 100,
                    'Tipo Match': m['match_type']
                })

            df_matches = pd.DataFrame(flat_matches)
            df_matches.to_excel(writer, sheet_name='Quadrature', index=False)

            # 3. Unreconciled Sheets
            if results['unreconciled_debit']:
                df_u_debit = pd.DataFrame(results['unreconciled_debit'])
                df_u_debit['Importo'] = df_u_debit['Debit'] / 100
                df_u_debit[['Date', 'Importo']].to_excel(writer, sheet_name='Incassi Da Verificare', index=False)

            if results['unreconciled_credit']:
                df_u_credit = pd.DataFrame(results['unreconciled_credit'])
                df_u_credit['Importo'] = df_u_credit['Credit'] / 100
                df_u_credit[['Date', 'Importo']].to_excel(writer, sheet_name='Versamenti Da Verificare', index=False)

            # Apply formatting to all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:Z', 15)
                # Note: In a real implementation we would apply specific formats to columns here

        output.seek(0)
        return output
