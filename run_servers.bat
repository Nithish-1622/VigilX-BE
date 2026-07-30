@echo off
echo ======================================================
echo Starting VigilX Backend Services (Django + AI Engine)
echo ======================================================

echo Select your Redis environment:
echo 1. WSL (Windows Subsystem for Linux)
echo 2. Docker
echo 3. Skip (Redis is already running)
set /p choice="Enter your choice (1-3) [Default: 1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo Starting Redis Server via WSL...
    wsl sudo service redis-server start
) else if "%choice%"=="2" (
    echo Starting Redis Server via Docker...
    docker start redis 2>NUL || docker run -d --name redis -p 6379:6379 redis
) else (
    echo Skipping Redis startup...
)

:: Start Django Server in a new window (This will automatically spawn FastAPI AI Engine on port 8001)
echo Starting Django API Server on http://127.0.0.1:8000 ...
start "VigilX Backend Server" cmd /k "cd backend\django-api && ..\..\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

:: Start ML Studio Server on Port 8002
echo Starting ML Studio Server on http://127.0.0.1:8002 ...
start "VigilX ML Studio" cmd /k "cd backend && ..\.venv\Scripts\uvicorn.exe ml_studio.main:app --port 8002 --reload --reload-dir ml_studio"

echo All backend services (Django :8000, AI Engine :8001, ML Studio :8002) launched!
pause

