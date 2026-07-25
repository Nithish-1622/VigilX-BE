import json
schema = json.load(open('openapi_schema.json'))

endpoints = [
    ('/ai/v2/ask', 'post'),
    ('/ai/v2/registry', 'get'),
    ('/ai/graph/visualize', 'get'),
    ('/ai/graph/geography', 'get'),
    ('/adapter-test', 'get')
]

for path, method in endpoints:
    print(f"\n--- {method.upper()} {path} ---")
    data = schema.get('paths', {}).get(path, {}).get(method, {})
    
    # Request Body
    req_body = data.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
    if req_body:
        print("Request Schema:")
        print(json.dumps(req_body, indent=2))
        
    # Response
    responses = data.get('responses', {})
    success_resp = responses.get('200', {}).get('content', {}).get('application/json', {}).get('schema', {})
    if success_resp:
        print("Response Schema (200 OK):")
        print(json.dumps(success_resp, indent=2))
