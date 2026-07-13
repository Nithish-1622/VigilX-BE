@echo off
echo ======================================================
echo Starting VigilX Backend Services (Django + AI Engine)
echo ======================================================

:: Start Django Server in a new window
echo Starting Django API Server on http://127.0.0.1:8000 ...
start "VigilX Django API Server" cmd /k "cd backend\django-api && ..\..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

:: Start FastAPI AI Engine Server in a new window
echo Starting FastAPI AI Engine Server on http://127.0.0.1:8001 ...
start "VigilX AI Engine" cmd /k "cd backend\ai-engine && ..\..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001"

echo Both servers have been launched in separate windows!
pause
