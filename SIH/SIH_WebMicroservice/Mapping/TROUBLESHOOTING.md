# Troubleshooting Guide

## Common Issues

### 1. API Server Not Starting
**Problem:** Server fails to start or crashes

**Solutions:**
- Check if port 8000 is already in use
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### 2. HAPI FHIR Connection Failed
**Problem:** Cannot connect to HAPI FHIR on port 8090

**Solutions:**
```bash
# Start HAPI FHIR with Docker
docker run -p 8090:8080 hapiproject/hapi:latest

# Verify it's running
curl http://localhost:8090/fhir/metadata
```

### 3. Search Returns No Results
**Problem:** Search doesn't find any Traditional Medicine codes

**Solutions:**
```bash
# Rebuild search indexes
python build_indexes/build_indexes_icd.py

# Verify data files exist
dir data\*.json
```

### 4. Entity IDs Not Appearing
**Problem:** FHIR resources missing WHO Entity IDs

**Solutions:**
- Check `.env` file has WHO API credentials
- Verify internet connection
- Test: `python test_icd11_pipeline.py`
- System continues without Entity IDs if lookup fails

### 5. Login Fails
**Problem:** Cannot login to UI

**Solutions:**
- Verify API server is running
- Use credentials: `demo@example.com` / `demo123`
- Clear browser cache (Ctrl+F5)
- Check browser console for errors (F12)

### 6. EMR Send Fails
**Problem:** Error when sending to EMR

**Solutions:**
- Ensure HAPI FHIR is running on port 8090
- Verify patient exists (auto-created if missing)
- Check server logs for detailed error
- Run diagnostic: `python diagnose_emr.py`

## Diagnostic Tools

### System Check
```bash
python diagnose_emr.py
```

### View Stored Conditions
```bash
python view_emr_conditions.py
```

### Test Entity ID Lookup
```bash
python test_icd11_pipeline.py
```

## Getting Help

1. Check server logs in terminal
2. Check browser console (F12)
3. Run `python diagnose_emr.py`
4. Review error messages carefully
