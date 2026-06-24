@echo off
echo Starting Claude Desktop...

:: Use explicit Python 3.12 path
set PYTHON=C:\Users\mycena\AppData\Local\Programs\Python\Python312\python.exe

:: Start Python backend
start "Claude Backend" cmd /k "cd /d %~dp0backend && "%PYTHON%" main.py"

:: Wait 2 seconds then start Angular frontend
timeout /t 2 /nobreak >nul
start "Claude Frontend" cmd /k "cd /d %~dp0frontend && ng serve --proxy-config proxy.conf.json --open"

echo.
echo Backend:  http://localhost:8765
echo Frontend: http://localhost:4200
echo.
echo Both windows started. Close them to stop.
