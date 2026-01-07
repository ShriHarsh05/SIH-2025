@echo off
echo ========================================
echo Setting up HAPI FHIR Server
echo ========================================
echo.
echo This will start a FHIR server on port 8090
echo that will actually store and retrieve conditions!
echo.
echo Starting HAPI FHIR Server...
docker run -d -p 8090:8080 --name hapi-fhir hapiproject/hapi:latest

echo.
echo ========================================
echo HAPI FHIR Server Starting!
echo ========================================
echo.
echo Wait 30 seconds for initialization...
timeout /t 30 /nobreak
echo.
echo HAPI FHIR is ready!
echo.
echo Access at: http://localhost:8090/fhir
echo.
echo Next steps:
echo 1. Update your EMR URL to: http://localhost:8090/fhir
echo 2. Remove authentication (HAPI is open by default)
echo 3. Test sending conditions
echo.
echo Press any key to exit...
pause > nul
