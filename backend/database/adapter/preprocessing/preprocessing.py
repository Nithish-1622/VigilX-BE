from typing import Any, Dict, List, TYPE_CHECKING
try:
    import pandas as pd
except ImportError:
    pd = None
import io

class PreprocessingEngine:
    """
    Cleans raw data, handles missing values, and fixes encodings.
    """
    
    @staticmethod
    def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Removes nulls or standardizes missing values in a dict."""
        cleaned = {}
        for k, v in data.items():
            if v is None or v == "" or str(v).lower() in ("nan", "null"):
                cleaned[k] = None
            else:
                cleaned[k] = v
        return cleaned

    @staticmethod
    def clean_dataframe(df: "pd.DataFrame") -> "pd.DataFrame":
        """
        Cleans a pandas DataFrame (used for CSV/Excel).
        Handles duplicates, NaN values, and strips whitespace.
        """
        # Drop duplicates
        df = df.drop_duplicates()
        
        # Strip whitespace from string columns
        str_cols = df.select_dtypes(['object']).columns
        df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
        
        # Replace NaN/NaT with None
        df = df.where(pd.notnull(df), None)
        
        return df

    @staticmethod
    def decode_bytes(data: bytes) -> str:
        """
        Tries multiple encodings to decode bytes robustly.
        """
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        # Fallback to utf-8 ignore
        return data.decode('utf-8', errors='ignore')
