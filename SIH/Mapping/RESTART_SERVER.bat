@echo off
echo ======================================================================
echo RESTARTING API SERVER
echo ======================================================================
echo.
echo This will restart the FastAPI server with the EMR 404 fix applied.
echo.
echo Press Ctrl+C to stop the server when needed.
echo.
echo ======================================================================
echo.

cd /d "%~dp0"
uvicorn api.server:app --reload
