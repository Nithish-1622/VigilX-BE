import os
import sys
from pathlib import Path

# Fix module imports across backend subfolders
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
django_dir = backend_dir / "django-api"
ai_engine_dir = backend_dir / "ai-engine"

for path_str in [str(root_dir), str(backend_dir), str(django_dir), str(ai_engine_dir)]:
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if __name__ == "__main__":
    import uvicorn
    
    # Zoho Catalyst AppSail injects X_ZOHO_CATALYST_LISTEN_PORT or PORT at runtime
    port_env = os.getenv("X_ZOHO_CATALYST_LISTEN_PORT") or os.getenv("PORT") or "9000"
    port = int(port_env)
    
    print(f"[INFO] Starting VigilX Unified Server on 0.0.0.0:{port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
