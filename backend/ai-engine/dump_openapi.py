import json
from main import app
with open('openapi_schema.json', 'w') as f:
    json.dump(app.openapi(), f)
