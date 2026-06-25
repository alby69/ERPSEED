import pandas as pd
import io
from typing import Dict, Any, Optional, List
import logging

class FileProcessingService:
    """
    Service for generic file processing (CSV, Excel).
    Provides methods for reading, cleaning, and standardizing data.
    """

    @staticmethod
    def read_file(file_content: bytes, filename: str, **kwargs) -> pd.DataFrame:
        """
        Reads a file (CSV or Excel) into a pandas DataFrame.
        """
        if filename.endswith('.csv'):
            return FileProcessingService.read_csv(io.BytesIO(file_content), **kwargs)
        elif filename.endswith(('.xls', '.xlsx')):
            return FileProcessingService.read_excel(io.BytesIO(file_content), **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    @staticmethod
    def read_csv(stream, **kwargs) -> pd.DataFrame:
        """Helper for CSV with Italian defaults."""
        try:
            # Try semicolon with comma decimal first (standard Italian)
            return pd.read_csv(stream, sep=';', decimal=',', **kwargs)
        except:
            stream.seek(0)
            return pd.read_csv(stream, decimal=',', thousands='.', **kwargs)

    @staticmethod
    def read_excel(stream, **kwargs) -> pd.DataFrame:
        """Helper for Excel."""
        return pd.read_excel(stream, **kwargs)

    @staticmethod
    def clean_numeric(df: pd.DataFrame, columns: List[str], to_cents: bool = False) -> pd.DataFrame:
        """
        Cleans numeric columns from strings with Italian/European formatting.
        """
        df = df.copy()
        for col in columns:
            if col in df.columns:
                # Check if already numeric (float/int) - no processing needed
                if df[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                    # Already numeric - just convert to float if needed
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    # Convert to string first to handle mixed types
                    series = df[col].astype(str)
                    # Remove thousands separator (dot) and replace decimal separator (comma) with dot
                    series = series.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(series, errors='coerce').fillna(0)

                if to_cents:
                    df[col] = (df[col] * 100).round().astype(int)
        return df

    @staticmethod
    def standardize_dates(df: pd.DataFrame, columns: List[str], dayfirst: bool = True) -> pd.DataFrame:
        """
        Standardizes date columns to datetime objects.
        """
        df = df.copy()
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=dayfirst)
        return df

    @staticmethod
    def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Renames columns based on a mapping dictionary.
        """
        return df.rename(columns=mapping)

    @staticmethod
    def export_to_excel(data_dict: Dict[str, pd.DataFrame], output_path: Optional[str] = None) -> io.BytesIO:
        """
        Exports multiple DataFrames to a single Excel file with multiple sheets.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        output.seek(0)
        return output
