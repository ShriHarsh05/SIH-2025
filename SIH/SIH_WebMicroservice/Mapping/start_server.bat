@echo off
echo ========================================
echo Starting Traditional Medicine API Server
echo ========================================
echo.
echo Server will start on http://localhost:8000
echo UI available at http://localhost:8000/ui/index.html
echo EMR Viewer at http://localhost:8000/ui/emr_viewer.html
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
