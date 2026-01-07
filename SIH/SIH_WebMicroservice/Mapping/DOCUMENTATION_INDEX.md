# Documentation Index

## Essential Documentation Files

This project has been cleaned up to include only essential documentation. All files are in the root `SIH/Mapping/` directory.

### 1. README.md
**Main project documentation**
- Project overview and features
- Quick start guide
- Architecture diagram
- API endpoints
- Configuration
- Development guide

**Start here if you're new to the project.**

### 2. SETUP_GUIDE.md
**Installation and setup instructions**
- Prerequisites
- Step-by-step installation
- Building search indexes
- Starting servers
- Initial configuration

**Use this for first-time setup.**

### 3. EMR_INTEGRATION_GUIDE.md
**HAPI FHIR EMR integration**
- HAPI FHIR server setup
- Patient management
- Sending conditions to EMR
- Viewing stored data
- EMR viewer usage

**Reference this for EMR integration.**

### 4. FHIR_INTEGRATION_GUIDE.md
**FHIR R4 resource details**
- FHIR Condition structure
- Coding systems
- Extensions
- Validation
- Examples

**Use this for FHIR implementation details.**

### 5. ICD11_FHIR_PIPELINE_GUIDE.md
**WHO ICD-11 Entity ID integration**
- WHO API setup
- OAuth2 authentication
- Entity ID lookup
- FHIR CodeSystem generation
- Troubleshooting API issues

**Reference this for Entity ID setup.**

### 6. TROUBLESHOOTING.md
**Common problems and solutions**
- Server issues
- Search problems
- EMR connection errors
- Entity ID lookup failures
- Diagnostic tools

**Check this when you encounter issues.**

## Quick Reference

### Getting Started
1. Read **README.md** for overview
2. Follow **SETUP_GUIDE.md** for installation
3. Use **TROUBLESHOOTING.md** if issues arise

### Integration
- **EMR_INTEGRATION_GUIDE.md** - Connect to HAPI FHIR
- **FHIR_INTEGRATION_GUIDE.md** - Understand FHIR resources
- **ICD11_FHIR_PIPELINE_GUIDE.md** - Enable Entity IDs

## Additional Resources

### Configuration Files
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies

### Scripts
- `start_server.bat` / `start_server.sh` - Start API server
- `diagnose_emr.py` - System diagnostic
- `view_emr_conditions.py` - View stored conditions

### Test Scripts
- `test_icd11_pipeline.py` - Test Entity ID lookup
- `test_fhir_with_entities.py` - Test FHIR generation
- `test_hapi_integration.py` - Test EMR integration

## Documentation Maintenance

All excess documentation files have been removed. The remaining files provide:
- Complete project understanding
- Setup and configuration
- Integration guides
- Troubleshooting help

**Do not create additional documentation files unless absolutely necessary.**

## Getting Help

1. Check relevant documentation file above
2. Run diagnostic: `python diagnose_emr.py`
3. Review server logs
4. Check browser console (F12)

## File Sizes

- README.md: ~8.5 KB
- SETUP_GUIDE.md: ~4.2 KB
- EMR_INTEGRATION_GUIDE.md: ~9.4 KB
- FHIR_INTEGRATION_GUIDE.md: ~10.7 KB
- ICD11_FHIR_PIPELINE_GUIDE.md: ~5.9 KB
- TROUBLESHOOTING.md: ~1.9 KB

**Total: ~40 KB of essential documentation**
