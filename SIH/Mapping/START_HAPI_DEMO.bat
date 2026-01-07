@echo off
echo ========================================
echo Starting HAPI FHIR Demo Environment
echo ========================================
echo.

echo Step 1: Checking HAPI FHIR...
docker ps | findstr hapi-fhir >nul 2>&1
if %errorlevel% neq 0 (
    echo HAPI FHIR not running. Starting...
    docker run -d -p 8090:8080 --name hapi-fhir hapiproject/hapi:latest
    echo Waiting 30 seconds for HAPI FHIR to start...
    timeout /t 30 /nobreak
) else (
    echo HAPI FHIR is already running!
)

echo.
echo Step 2: Testing HAPI FHIR connection...
python test_hapi_integration.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: HAPI FHIR test failed!
    echo Please wait a bit longer and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Environment Ready!
echo ========================================
echo.
echo HAPI FHIR: http://localhost:8090/fhir
echo.
echo Now starting the API server...
echo.
echo After server starts:
echo 1. Open: http://localhost:8000/ui/index.html
echo 2. Login: demo@example.com / demo123
echo 3. Map a term and send to EMR
echo 4. Copy the Resource ID
echo 5. Open: http://localhost:8090/fhir/Condition/{ID}
echo.
echo ========================================
echo.

python -m uvicorn api.server:app --reload --port 8000
