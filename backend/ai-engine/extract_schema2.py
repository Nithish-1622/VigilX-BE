import json
schema = json.load(open('openapi_schema.json'))
components = schema.get('components', {}).get('schemas', {})

print("--- AskRequest ---")
print(json.dumps(components.get('AskRequest', {}), indent=2))
print("\n--- InvestigationResponse ---")
print(json.dumps(components.get('InvestigationResponse', {}), indent=2))
print("\n--- Any other relevant? ---")
print(components.keys())
