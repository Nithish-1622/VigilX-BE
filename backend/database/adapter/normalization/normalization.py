import re
from typing import Any, Dict
from datetime import datetime

class NormalizationEngine:
    """
    Normalizes raw source data into a standardized format.
    """
    
    @staticmethod
    def normalize_key(key: str) -> str:
        """
        Converts keys to snake_case.
        E.g., 'CrimeType', 'CRIME TYPE', 'crime-type' -> 'crime_type'
        """
        # Replace non-alphanumeric chars (except underscores/spaces) with space
        clean_key = re.sub(r'[^a-zA-Z0-9_\s]', ' ', key)
        # Convert CamelCase to snake_case
        clean_key = re.sub(r'(?<!^)(?=[A-Z])', '_', clean_key)
        # Replace spaces and repeated underscores with single underscore
        clean_key = re.sub(r'[\s_]+', '_', clean_key)
        return clean_key.lower().strip('_')

    @staticmethod
    def normalize_value(value: Any) -> Any:
        """
        Normalizes values: trims strings, standardizes dates, etc.
        """
        if isinstance(value, str):
            val = value.strip()
            # Attempt to parse common date formats if it looks like a date
            if re.match(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', val):
                try:
                    return datetime.fromisoformat(val.replace(' ', 'T')).isoformat()
                except ValueError:
                    pass
            return val
        
        # Booleans represented as strings
        if isinstance(value, str) and value.lower() in ('true', 'false', 'yes', 'no'):
            return value.lower() in ('true', 'yes')
            
        return value

    @classmethod
    def normalize_record(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a full dictionary record.
        """
        normalized = {}
        for k, v in raw_data.items():
            norm_k = cls.normalize_key(k)
            norm_v = cls.normalize_value(v)
            normalized[norm_k] = norm_v
        return normalized
