import os
import subprocess
import sys
from django.contrib.staticfiles.management.commands.runserver import Command as StaticfilesRunserverCommand

class Command(StaticfilesRunserverCommand):
    help = "Starts the Django development server and automatically spawns the FastAPI AI Engine."

    def inner_run(self, *args, **options):
        # We only start the FastAPI subprocess in the worker thread (when RUN_MAIN is 'true'),
        # or when the reloader is disabled entirely.
        use_reloader = options.get('use_reloader', True)
        is_reloader_parent = use_reloader and os.environ.get('RUN_MAIN') != 'true'
        
        fastapi_proc = None
        if not is_reloader_parent:
            self.stdout.write(self.style.SUCCESS("Django starting up... launching FastAPI AI Engine server in background..."))
            try:
                # Resolve paths
                # Current file is in: backend/django-api/apps/common/management/commands/runserver.py
                # Root workspace directory: d:/VigilX-BE
                # django-api directory: backend/django-api
                # ai-engine directory: backend/ai-engine
                current_dir = os.path.dirname(os.path.abspath(__file__))
                django_api_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
                workspace_dir = os.path.dirname(django_api_dir)
                ai_engine_dir = os.path.join(django_api_dir, "..", "ai-engine")
                ai_engine_dir = os.path.abspath(ai_engine_dir)
                
                # Check virtual environment python executable
                venv_python = os.path.join(workspace_dir, ".venv", "Scripts", "python.exe")
                if not os.path.exists(venv_python):
                    venv_python = sys.executable  # Fallback to current python interpreter
                
                cmd = [
                    venv_python, "-m", "uvicorn", "main:app",
                    "--host", "127.0.0.1",
                    "--port", "8001"
                ]
                
                self.stdout.write(f"Executing: {' '.join(cmd)}")
                self.stdout.write(f"Working Directory: {ai_engine_dir}")
                
                fastapi_proc = subprocess.Popen(
                    cmd,
                    cwd=ai_engine_dir,
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                self.stdout.write(self.style.SUCCESS(f"FastAPI server launched successfully (PID: {fastapi_proc.pid}) at http://127.0.0.1:8001"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to launch FastAPI server: {e}"))
        
        try:
            super().inner_run(*args, **options)
        finally:
            if fastapi_proc is not None:
                self.stdout.write(self.style.WARNING("Stopping background FastAPI AI Engine server..."))
                fastapi_proc.terminate()
                try:
                    fastapi_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    fastapi_proc.kill()
                self.stdout.write(self.style.SUCCESS("FastAPI server stopped successfully."))
