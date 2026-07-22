from typing import Dict, Any, List

class SchemaEngine:
    """
    Infers schema for dynamic/unstructured sources.
    For structured sources (SQL), connectors use database introspection.
    """
    
    @staticmethod
    def infer_type(value: Any) -> str:
        """Heuristically infers the type of a value."""
        if value is None:
            return "unknown"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            # Very basic check for UUID
            if len(value) == 36 and value.count('-') == 4:
                return "uuid"
            # Date/time
            import re
            if re.match(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', value):
                return "datetime"
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return "date"
            if "@" in value and "." in value.split("@")[-1]:
                return "email"
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "unknown"

    @classmethod
    def infer_schema_from_records(cls, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Samples records to infer a schema for the collection/table.
        """
        schema = {}
        # Sample up to 100 records
        for record in records[:100]:
            for key, val in record.items():
                if key not in schema or schema[key] == "unknown":
                    inferred = cls.infer_type(val)
                    if inferred != "unknown":
                        schema[key] = inferred
        return schema
