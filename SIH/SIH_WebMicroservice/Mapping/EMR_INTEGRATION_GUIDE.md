# 🏥 EMR Integration Guide

## Overview

This guide helps you connect your Traditional Medicine → ICD-11 Mapping System to open-source Electronic Medical Record (EMR) systems.

---

## 🎯 Recommended EMR: Bahmni

**Why Bahmni?**
- ✅ Developed for Indian healthcare
- ✅ Built on OpenMRS (proven platform)
- ✅ Native FHIR R4 support
- ✅ Used in 500+ hospitals globally
- ✅ Strong community support
- ✅ Perfect for traditional medicine

---

## 📦 Quick Setup Options

### Option 1: Bahmni (Recommended)

#### Installation

**Using Docker (Easiest):**
```bash
# Clone Bahmni
git clone https://github.com/Bahmni/bahmni-docker.git
cd bahmni-docker

# Start Bahmni
docker-compose up -d

# Access Bahmni
# URL: http://localhost:8050
# Username: admin
# Password: Admin123
```

**Manual Installation:**
```bash
# Follow official guide
https://bahmni.atlassian.net/wiki/spaces/BAH/pages/33128/Install+Bahmni+on+CentOS
```

#### Integration Code

```python
from emr_integration import BahmniIntegration

# Connect to Bahmni
bahmni = BahmniIntegration(
    base_url="http://localhost:8050",
    username="admin",
    password="Admin123"
)

# Send your FHIR Condition
result = bahmni.send_fhir_condition(your_fhir_resource)
```

---

### Option 2: OpenEMR

#### Installation

**Using Docker:**
```bash
docker run -d \
  --name openemr \
  -p 8080:80 \
  -p 8443:443 \
  openemr/openemr:latest

# Access OpenEMR
# URL: http://localhost:8080
# Setup wizard will guide you
```

#### Integration Code

```python
from emr_integration import OpenEMRIntegration

openemr = OpenEMRIntegration(
    base_url="http://localhost:8080",
    username="admin",
    password="your_password"
)

result = openemr.send_fhir_condition(your_fhir_resource)
```

---

### Option 3: OpenMRS

#### Installation

**Using Docker:**
```bash
docker run -d \
  --name openmrs \
  -p 8080:8080 \
  openmrs/openmrs-core:latest

# Access OpenMRS
# URL: http://localhost:8080/openmrs
```

---

## 🔗 Integration Workflow

### Step 1: Generate FHIR Resource

Your system already generates FHIR R4 Condition resources:

```javascript
// In your UI (script.js)
const fhirData = await fetch(`${API}/fhir/condition`, {
    method: 'POST',
    body: JSON.stringify({
        mapping_result: mappingResult,
        patient_id: "patient-123",
        encounter_id: "encounter-456"
    })
});
```

### Step 2: Send to EMR

Add this endpoint to your FastAPI server:

```python
# In api/server.py
from emr_integration import BahmniIntegration

@app.post("/emr/send-to-bahmni")
async def send_to_bahmni(
    fhir_resource: dict,
    bahmni_url: str,
    username: str,
    password: str
):
    """Send FHIR resource to Bahmni EMR"""
    try:
        bahmni = BahmniIntegration(bahmni_url, username, password)
        result = bahmni.send_fhir_condition(fhir_resource)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Step 3: Update UI

Add EMR configuration in your UI:

```javascript
// Add to script.js
async function sendToEMR(fhirData) {
    const emrConfig = {
        bahmni_url: "http://localhost:8050",
        username: "admin",
        password: "Admin123"
    };
    
    const response = await fetch(`${API}/emr/send-to-bahmni`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            fhir_resource: fhirData,
            ...emrConfig
        })
    });
    
    const result = await response.json();
    if (result.success) {
        alert('✅ Sent to EMR successfully!');
    } else {
        alert('❌ Failed to send to EMR');
    }
}
```

---

## 🎨 UI Enhancement: Add "Send to EMR" Button

Update your FHIR export modal to include EMR integration:

```javascript
function showFHIRModal(fhirData) {
    // ... existing modal code ...
    
    // Add EMR send button
    content.innerHTML += `
        <button class="btn btn-secondary" onclick="sendToEMR(${JSON.stringify(fhirData)})">
            <i class="fas fa-hospital"></i> Send to Bahmni EMR
        </button>
    `;
}
```

---

## 📊 Complete Integration Example

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure EMR Connection

Create `.env` file:
```env
# EMR Configuration
EMR_TYPE=bahmni
EMR_URL=http://localhost:8050
EMR_USERNAME=admin
EMR_PASSWORD=Admin123
```

### 3. Update Server

```python
# api/server.py
from emr_integration import BahmniIntegration
import os

EMR_URL = os.getenv("EMR_URL", "http://localhost:8050")
EMR_USERNAME = os.getenv("EMR_USERNAME", "admin")
EMR_PASSWORD = os.getenv("EMR_PASSWORD", "Admin123")

@app.post("/emr/send")
async def send_to_emr(fhir_resource: dict):
    """Send FHIR resource to configured EMR"""
    try:
        emr = BahmniIntegration(EMR_URL, EMR_USERNAME, EMR_PASSWORD)
        result = emr.send_fhir_condition(fhir_resource)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Secure Credentials**: Store in environment variables or secrets manager
3. **OAuth2**: Use OAuth2 for authentication (not basic auth)
4. **API Keys**: Use API keys instead of passwords
5. **Rate Limiting**: Implement rate limiting
6. **Audit Logs**: Log all EMR transactions

### Example Secure Configuration

```python
from cryptography.fernet import Fernet

# Encrypt credentials
def encrypt_credentials(username, password):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_user = f.encrypt(username.encode())
    encrypted_pass = f.encrypt(password.encode())
    return encrypted_user, encrypted_pass, key
```

---

## 🧪 Testing

### Test with Bahmni Demo

```python
# test_emr_integration.py
from emr_integration import BahmniIntegration

def test_bahmni_connection():
    bahmni = BahmniIntegration(
        base_url="https://demo.mybahmni.org",
        username="superman",
        password="Admin123"
    )
    
    # Test FHIR resource
    test_condition = {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-11",
                "code": "TEST001",
                "display": "Test Condition"
            }]
        },
        "subject": {
            "reference": "Patient/1"
        }
    }
    
    result = bahmni.send_fhir_condition(test_condition)
    print("Test Result:", result)

if __name__ == "__main__":
    test_bahmni_connection()
```

---

## 📚 Resources

### Bahmni
- **Website**: https://www.bahmni.org/
- **Documentation**: https://bahmni.atlassian.net/wiki/spaces/BAH/overview
- **Demo**: https://demo.mybahmni.org/
- **Community**: https://talk.openmrs.org/c/software/bahmni

### OpenEMR
- **Website**: https://www.open-emr.org/
- **Documentation**: https://www.open-emr.org/wiki/
- **Demo**: https://www.open-emr.org/demo/

### OpenMRS
- **Website**: https://openmrs.org/
- **Documentation**: https://wiki.openmrs.org/
- **FHIR Module**: https://wiki.openmrs.org/display/projects/OpenMRS+FHIR+Module

---

## 🎯 Next Steps

1. **Choose EMR**: Select Bahmni (recommended) or another EMR
2. **Install EMR**: Use Docker for quick setup
3. **Test Connection**: Run test script
4. **Integrate**: Add EMR endpoints to your API
5. **Update UI**: Add "Send to EMR" button
6. **Deploy**: Deploy both systems together

---

## 💡 Pro Tips

1. **Start with Docker**: Easiest way to test EMR systems
2. **Use Bahmni Demo**: Test without local installation
3. **FHIR Validation**: Validate FHIR resources before sending
4. **Error Handling**: Implement robust error handling
5. **Logging**: Log all EMR interactions for debugging
6. **Backup**: Always backup EMR data before testing

---

## 🆘 Troubleshooting

### Connection Issues
```python
# Test EMR connectivity
import requests

def test_emr_connection(url):
    try:
        response = requests.get(f"{url}/openmrs/ws/rest/v1/session")
        print(f"✅ EMR reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach EMR: {e}")

test_emr_connection("http://localhost:8050")
```

### Authentication Issues
- Check username/password
- Verify EMR is running
- Check firewall settings
- Review EMR logs

### FHIR Issues
- Validate FHIR resource structure
- Check FHIR version (R4)
- Verify required fields
- Test with minimal resource first

---

## ✅ Success Checklist

- [ ] EMR system installed and running
- [ ] Can access EMR web interface
- [ ] Authentication working
- [ ] FHIR endpoint accessible
- [ ] Test FHIR resource sent successfully
- [ ] Integration code added to your project
- [ ] UI updated with "Send to EMR" button
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Security measures in place

---

**Your Traditional Medicine Mapping System is now ready for real-world EMR integration!** 🎉
