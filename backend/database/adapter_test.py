import asyncio
import os
from adapter.registry.registry import ConnectorRegistry
from adapter.core.models import SearchQuery
from adapter.registry.detector import SourceDetector

async def main():
    print("--- Universal Database Adapter Initialization Test ---")
    
    # 1. Test Registry loading
    print(f"\nRegistered Connectors: {list(ConnectorRegistry.list_connectors().keys())}")
    
    # 2. Test auto-detection
    test_sources = [
        "postgres://user:pass@localhost:5432/mydb",
        "mongodb://localhost:27017/data",
        "dummy.csv",
        "report.pdf"
    ]
    
    for src in test_sources:
        try:
            detected = SourceDetector.detect_source_type(src)
            print(f"Auto-detected '{src}' -> {detected}")
        except Exception as e:
            print(f"Error detecting '{src}': {e}")
            
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
