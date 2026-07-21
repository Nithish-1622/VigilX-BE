from typing import List, Dict, Any

class MetadataEngine:
    """
    Generates dataset-level metadata profiles.
    """

    @staticmethod
    def generate_profile(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Profiles a dataset to return stats like row count, null %, etc.
        """
        row_count = len(records)
        if row_count == 0:
            return {"row_count": 0, "status": "empty"}

        # Gather keys across all records
        all_keys = set()
        for r in records:
            all_keys.update(r.keys())

        profile = {
            "row_count": row_count,
            "column_count": len(all_keys),
            "columns": {}
        }

        for key in all_keys:
            null_count = sum(1 for r in records if r.get(key) is None)
            unique_vals = set(r.get(key) for r in records if r.get(key) is not None)
            # Cannot do full uniqueness check on unhashable types (like dicts/lists),
            # but this works for basic profiling.
            
            profile["columns"][key] = {
                "null_percentage": (null_count / row_count) * 100 if row_count > 0 else 0,
                "unique_values_count": len(unique_vals),
                "is_mostly_unique": len(unique_vals) > (row_count * 0.9)
            }

        return profile
