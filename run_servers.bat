@echo off
echo ======================================================
echo Starting VigilX Backend Services (Django + AI Engine)
echo ======================================================

:: Start Redis Server via WSL (Will prompt for Ubuntu password if needed)
echo Starting Redis Server via WSL...
wsl sudo service redis-server start

:: Start Django Server in a new window (This will automatically spawn FastAPI on port 8001)
echo Starting Django API Server on http://127.0.0.1:8000 ...
start "VigilX Backend Server" cmd /k "cd backend\django-api && ..\..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

echo Both servers have been launched!
pause
