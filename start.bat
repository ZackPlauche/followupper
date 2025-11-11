@echo off
echo ========================================
echo   Followupper - Starting Application
echo ========================================
echo.

echo Starting backend server...
cd backend
start /B uv run python manage.py runserver 127.0.0.1:8001
cd ..

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend server...
cd frontend
start /B npm run dev
cd ..

echo.
echo ========================================
echo   Both servers are starting...
echo   Backend: http://localhost:8001
echo   Frontend: http://localhost:4000
echo ========================================
echo.
echo Press any key to exit this window (servers will continue running)...
pause >nul

