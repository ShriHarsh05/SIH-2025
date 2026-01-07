const API = window.location.origin;

let currentSystem = "siddha";
let authToken = null;

// ===== AUTHENTICATION =====

window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
        authToken = tokenFromUrl;
        localStorage.setItem('authToken', tokenFromUrl);
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        authToken = localStorage.getItem('authToken');
    }
    
    if (authToken) {
        verifyToken();
    } else {
        showLogin();
    }
});

async function verifyToken() {
    try {
        const response = await fetch(`${API}/auth/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const user = await response.json();
            showMainApp(user);
        } else {
            showLogin();
        }
    } catch (error) {
        console.error('Token verification failed:', error);
        showLogin();
    }
}

function showLogin() {
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('mainApp').style.display = 'none';
}

function showMainApp(user) {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    document.getElementById('userName').textContent = user.full_name || user.email;
    
    // Set initial theme
    document.body.className = 'theme-siddha';
}

async function loginWithCredentials(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    console.log('Attempting login with:', email);
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        console.log('Sending request to:', `${API}/auth/token`);
        
        const response = await fetch(`${API}/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Login successful, token received');
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            verifyToken();
        } else {
            const errorData = await response.text();
            console.error('Login failed:', errorData);
            alert('Invalid credentials. Try demo@example.com / demo123');
        }
    } catch (error) {
        console.error('Login failed:', error);
        alert('Login failed. Please try again.');
    }
}

function loginWithGoogle() {
    window.location.href = `${API}/auth/google/login`;
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showLogin();
}

// ===== SYSTEM SELECTION =====

function selectSystem(system) {
    currentSystem = system;
    document.getElementById(system).checked = true;
    
    const systemName = system.charAt(0).toUpperCase() + system.slice(1);
    document.getElementById('systemLabel').textContent = systemName;
    
    // Change theme based on system
    document.body.className = `theme-${system}`;
    
    clearResults();
}

function clearResults() {
    document.getElementById('mappingInput').value = '';
    document.getElementById('mappingResults').innerHTML = '';
    document.getElementById('icdResults').innerHTML = '';
}

// ===== FULL MAPPING =====

async function runMapping() {
    const query = document.getElementById('mappingInput').value.trim();
    
    if (!query) {
        alert('Please enter a query');
        return;
    }

    const resultsDiv = document.getElementById('mappingResults');
    resultsDiv.innerHTML = '<div class="result-card"><i class="fas fa-spinner fa-spin"></i> Mapping to ICD-11...</div>';

    try {
        const res = await fetch(`${API}/map`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
            },
            body: JSON.stringify({ query, system: currentSystem })
        });

        const data = await res.json();

        const systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
        const candidatesKey = `${currentSystem}_candidates`;
        
        let candidatesHTML = `
            <div class="result-card">
                <h3><i class="fas fa-hand-pointer"></i> ${systemName} Candidates (Click to map to ICD-11)</h3>
        `;
        
        if (data[candidatesKey] && data[candidatesKey].length > 0) {
            data[candidatesKey].forEach((candidate) => {
                const displayTerm = candidate.english || candidate.term;
                const originalTerm = candidate.term || '';
                const definition = candidate.definition || 'No description available';
                
                candidatesHTML += `
                    <div class="tm-candidate" onclick="mapToICD('${candidate.code}', '${displayTerm.replace(/'/g, "\\'")}')">
                        <div style="font-size: 18px; font-weight: 600; color: var(--primary-color); margin-bottom: 6px;">
                            ${candidate.code} — ${displayTerm}
                        </div>
                        ${originalTerm && originalTerm !== displayTerm ? 
                            `<div style="font-size: 14px; color: var(--gray); margin-bottom: 6px;">
                                <i class="fas fa-language"></i> Original: ${originalTerm}
                            </div>` : ''}
                        <div style="font-size: 14px; color: var(--dark); line-height: 1.6; margin-bottom: 6px;">
                            ${definition.slice(0, 200)}${definition.length > 200 ? '...' : ''}
                        </div>
                        <div style="font-size: 13px; color: var(--gray);">
                            <i class="fas fa-chart-line"></i> Score: ${candidate.score.toFixed(4)}
                        </div>
                    </div>
                `;
            });
        } else {
            candidatesHTML += '<p>No candidates found</p>';
        }
        
        candidatesHTML += '</div>';
        resultsDiv.innerHTML = candidatesHTML;
        document.getElementById('icdResults').innerHTML = '';
    } catch (error) {
        console.error('Mapping error:', error);
        resultsDiv.innerHTML = '<div class="result-card" style="color: var(--danger-color);"><i class="fas fa-exclamation-triangle"></i> Error performing mapping</div>';
    }
}

// ===== MAP TO ICD =====

async function mapToICD(code, term) {
    const systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
    const icdDiv = document.getElementById('icdResults');
    
    icdDiv.innerHTML = '<div class="result-card"><i class="fas fa-spinner fa-spin"></i> Mapping to ICD-11 Standard and TM2...</div>';

    try {
        const res = await fetch(`${API}/map/${currentSystem}-code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
            },
            body: JSON.stringify({ code, term })
        });

        const data = await res.json();

        window.currentMappingResult = data;
        window.selectedTMCandidate = { system: currentSystem, code, term, data };
        window.selectedICD11Standard = null;
        window.selectedICD11TM2 = null;
        
        let icdHTML = `
            <div class="result-card">
                <h3><i class="fas fa-check-circle"></i> Selected ${systemName}: ${code} — ${term}</h3>
                <p style="color: var(--gray); margin-top: 10px;">
                    <i class="fas fa-info-circle"></i> Click on ICD-11 codes below to select them for FHIR export
                </p>
                <div id="selectionStatus" style="margin-top: 15px; padding: 15px; background: var(--light-gray); border-radius: 8px; display: none;">
                    <strong><i class="fas fa-clipboard-check"></i> Selected for FHIR Export:</strong>
                    <div id="selectedCodes" style="margin-top: 10px;"></div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;">
                    <button class="btn btn-secondary" onclick="exportFHIR()" id="exportBtn" disabled>
                        <i class="fas fa-file-export"></i> Export as FHIR JSON
                    </button>
                    <button class="btn btn-primary" onclick="sendToEMR()" id="emrBtn" disabled>
                        <i class="fas fa-hospital"></i> Send to EMR
                    </button>
                </div>
            </div>
            
            <div class="icd-grid">
                <div class="result-card">
                    <h3><i class="fas fa-hospital"></i> ICD-11 Standard</h3>
                    ${formatICDResults(data.icd11_standard_candidates, 'standard')}
                </div>
                
                <div class="result-card">
                    <h3><i class="fas fa-spa"></i> ICD-11 TM2</h3>
                    ${formatICDResults(data.icd11_tm2_candidates, 'tm2')}
                </div>
            </div>
        `;
        
        icdDiv.innerHTML = icdHTML;
    } catch (error) {
        console.error('ICD mapping error:', error);
        icdDiv.innerHTML = '<div class="result-card" style="color: var(--danger-color);"><i class="fas fa-exclamation-triangle"></i> Error mapping to ICD-11</div>';
    }
}

function formatICDResults(candidates, type) {
    if (!candidates || candidates.length === 0) {
        return '<p style="color: var(--gray); padding: 15px;">No results found</p>';
    }
    
    let html = '<div style="margin-top: 15px;">';
    
    candidates.forEach((candidate, index) => {
        const definition = candidate.definition || 'No description available';
        const candidateJson = JSON.stringify(candidate).replace(/"/g, '&quot;');
        
        html += `
            <div class="icd-item icd-selectable" 
                 onclick="selectICDCode('${type}', ${index}, this)" 
                 data-candidate='${candidateJson}'
                 id="icd-${type}-${index}">
                <div style="font-size: 16px; font-weight: 600; color: var(--dark); margin-bottom: 6px;">
                    ${index + 1}. ${candidate.code}
                </div>
                <div style="font-size: 15px; font-weight: 500; color: var(--primary-color); margin-bottom: 8px;">
                    ${candidate.title}
                </div>
                <div style="font-size: 14px; color: var(--gray); line-height: 1.6; margin-bottom: 8px;">
                    ${definition.slice(0, 200)}${definition.length > 200 ? '...' : ''}
                </div>
                <div style="font-size: 13px; color: var(--gray);">
                    <i class="fas fa-chart-line"></i> Score: ${candidate.score.toFixed(4)}
                </div>
                <div class="selection-indicator"><i class="fas fa-check"></i> Selected</div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function selectICDCode(type, index, element) {
    const candidate = JSON.parse(element.getAttribute('data-candidate'));
    
    if (type === 'standard') {
        document.querySelectorAll('.icd-item[id^="icd-standard-"]').forEach(el => {
            el.classList.remove('selected');
        });
        element.classList.add('selected');
        window.selectedICD11Standard = candidate;
    } else if (type === 'tm2') {
        document.querySelectorAll('.icd-item[id^="icd-tm2-"]').forEach(el => {
            el.classList.remove('selected');
        });
        element.classList.add('selected');
        window.selectedICD11TM2 = candidate;
    }
    
    updateSelectionStatus();
}

function updateSelectionStatus() {
    const statusDiv = document.getElementById('selectionStatus');
    const selectedCodesDiv = document.getElementById('selectedCodes');
    const exportBtn = document.getElementById('exportBtn');
    
    let selectedCodes = [];
    
    if (window.selectedTMCandidate) {
        const systemName = window.selectedTMCandidate.system.charAt(0).toUpperCase() + 
                          window.selectedTMCandidate.system.slice(1);
        selectedCodes.push(`<i class="fas fa-check-circle"></i> ${systemName}: ${window.selectedTMCandidate.code}`);
    }
    
    if (window.selectedICD11Standard) {
        selectedCodes.push(`<i class="fas fa-check-circle"></i> ICD-11 Standard: ${window.selectedICD11Standard.code}`);
    }
    
    if (window.selectedICD11TM2) {
        selectedCodes.push(`<i class="fas fa-check-circle"></i> ICD-11 TM2: ${window.selectedICD11TM2.code}`);
    }
    
    if (selectedCodes.length > 1) {
        statusDiv.style.display = 'block';
        selectedCodesDiv.innerHTML = selectedCodes.map(code => 
            `<div style="padding: 6px 0; font-size: 14px;">${code}</div>`
        ).join('');
        exportBtn.disabled = false;
        exportBtn.style.opacity = '1';
        exportBtn.style.cursor = 'pointer';
        
        const emrBtn = document.getElementById('emrBtn');
        if (emrBtn) {
            emrBtn.disabled = false;
            emrBtn.style.opacity = '1';
            emrBtn.style.cursor = 'pointer';
        }
    } else {
        statusDiv.style.display = 'none';
        exportBtn.disabled = true;
        exportBtn.style.opacity = '0.5';
        exportBtn.style.cursor = 'not-allowed';
        
        const emrBtn = document.getElementById('emrBtn');
        if (emrBtn) {
            emrBtn.disabled = true;
            emrBtn.style.opacity = '0.5';
            emrBtn.style.cursor = 'not-allowed';
        }
    }
}

// ===== FHIR EXPORT =====

async function exportFHIR() {
    if (!window.selectedTMCandidate || (!window.selectedICD11Standard && !window.selectedICD11TM2)) {
        alert('Please select at least one ICD-11 code');
        return;
    }
    
    try {
        const customMappingResult = {
            system: window.selectedTMCandidate.system,
            input: window.currentMappingResult.input || "",
            [`${window.selectedTMCandidate.system}_candidates`]: [window.selectedTMCandidate.data],
            icd11_standard_candidates: window.selectedICD11Standard ? [window.selectedICD11Standard] : [],
            icd11_tm2_candidates: window.selectedICD11TM2 ? [window.selectedICD11TM2] : []
        };
        
        const res = await fetch(`${API}/fhir/condition`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
            },
            body: JSON.stringify({
                mapping_result: customMappingResult,
                patient_id: "patient-" + Date.now(),
                encounter_id: "encounter-" + Date.now(),
                practitioner_id: "practitioner-001"
            })
        });
        
        const fhirData = await res.json();
        
        if (fhirData.error) {
            throw new Error(fhirData.error);
        }
        
        const dataStr = JSON.stringify(fhirData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `fhir-condition-${window.selectedTMCandidate.code}-${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showFHIRModal(fhirData);
        
    } catch (error) {
        console.error('FHIR export error:', error);
        alert('Error generating FHIR JSON: ' + error.message);
    }
}

function showFHIRModal(fhirData) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    
    const content = document.createElement('div');
    content.className = 'modal-content';
    content.style.maxWidth = '900px';
    content.style.maxHeight = '80vh';
    content.style.overflow = 'auto';
    
    content.innerHTML = `
        <div style="background: linear-gradient(135deg, var(--secondary-color) 0%, #059669 100%); color: white; padding: 25px; border-radius: 12px 12px 0 0;">
            <h2><i class="fas fa-file-medical"></i> FHIR Condition Resource</h2>
            <p style="margin-top: 10px; opacity: 0.95;">Bahmni EMR Compatible (FHIR R4)</p>
        </div>
        <div style="padding: 25px;">
            <pre style="background: var(--light-gray); padding: 20px; border-radius: 8px; overflow: auto; max-height: 400px; font-size: 13px; line-height: 1.6;">${JSON.stringify(fhirData, null, 2)}</pre>
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i> Close
                </button>
                <button class="btn btn-secondary" onclick="copyToClipboard(\`${JSON.stringify(fhirData).replace(/`/g, '\\`')}\`)">
                    <i class="fas fa-copy"></i> Copy JSON
                </button>
            </div>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = JSON.stringify(JSON.parse(text), null, 2);
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    alert('Copied to clipboard!');
}

// ===== SEND TO EMR (BAHMNI) =====

async function sendToEMR() {
    if (!window.selectedTMCandidate || (!window.selectedICD11Standard && !window.selectedICD11TM2)) {
        alert('Please select at least one ICD-11 code');
        return;
    }
    
    // Show loading modal
    const loadingModal = document.createElement('div');
    loadingModal.className = 'modal';
    loadingModal.innerHTML = `
        <div class="modal-content" style="max-width: 500px; text-align: center;">
            <h2><i class="fas fa-spinner fa-spin"></i> Sending to EMR...</h2>
            <p style="color: var(--gray); margin-top: 15px;">Please wait while we send the FHIR Condition to your EMR system.</p>
        </div>
    `;
    document.body.appendChild(loadingModal);
    
    try {
        // First, generate FHIR Condition
        // Create TM candidate with code and term from selectedTMCandidate
        const tmCandidate = {
            code: window.selectedTMCandidate.code,
            term: window.selectedTMCandidate.term,
            score: 1.0
        };
        
        const customMappingResult = {
            system: window.selectedTMCandidate.system,
            input: window.currentMappingResult.input || "",
            [`${window.selectedTMCandidate.system}_candidates`]: [tmCandidate],
            icd11_standard_candidates: window.selectedICD11Standard ? [window.selectedICD11Standard] : [],
            icd11_tm2_candidates: window.selectedICD11TM2 ? [window.selectedICD11TM2] : []
        };
        
        const fhirRes = await fetch(`${API}/fhir/condition`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
            },
            body: JSON.stringify({
                mapping_result: customMappingResult,
                patient_id: "b4f7d426-7471-4e9d-a204-64441b18a147",  // Patient UUID from Bahmni
                encounter_id: null,
                practitioner_id: null
            })
        });
        
        const fhirData = await fhirRes.json();
        
        console.log('FHIR Response:', fhirData);
        
        if (fhirData.error) {
            throw new Error(fhirData.error);
        }
        
        if (!fhirRes.ok) {
            throw new Error(`FHIR generation failed: ${JSON.stringify(fhirData)}`);
        }
        
        // Now send to EMR
        const emrRes = await fetch(`${API}/emr/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
            },
            body: JSON.stringify({
                fhir_condition: fhirData,
                emr_url: "http://localhost:8090/fhir",
                username: "",  // HAPI FHIR doesn't need authentication
                password: ""
            })
        });
        
        const emrResult = await emrRes.json();
        
        // Remove loading modal
        loadingModal.remove();
        
        if (emrResult.success) {
            // Show success modal
            showEMRSuccessModal(emrResult, fhirData);
        } else {
            throw new Error(emrResult.error || 'Failed to send to EMR');
        }
        
    } catch (error) {
        console.error('EMR send error:', error);
        loadingModal.remove();
        
        // Show error modal
        const errorModal = document.createElement('div');
        errorModal.className = 'modal';
        errorModal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <h2 style="color: var(--danger-color);"><i class="fas fa-exclamation-triangle"></i> Failed to Send to EMR</h2>
                <p style="color: var(--gray); margin-top: 15px;">${error.message}</p>
                <div style="margin-top: 20px; padding: 15px; background: var(--light-gray); border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 200px; overflow-y: auto;">
                    ${error.stack || error.message}
                </div>
                <div style="margin-top: 20px;">
                    <strong>Troubleshooting:</strong>
                    <ul style="text-align: left; margin-top: 10px; color: var(--gray);">
                        <li>Make sure EMR is running: <code>docker compose ps</code></li>
                        <li>Check if OpenMRS is fully initialized (wait 5-10 minutes)</li>
                        <li>Verify credentials: superman / Admin123</li>
                        <li>Check EMR URL: http://localhost</li>
                    </ul>
                </div>
                <button class="btn btn-primary" onclick="this.closest('.modal').remove()" style="margin-top: 20px;">
                    <i class="fas fa-times"></i> Close
                </button>
            </div>
        `;
        document.body.appendChild(errorModal);
        
        errorModal.onclick = (e) => {
            if (e.target === errorModal) {
                errorModal.remove();
            }
        };
    }
}

function showEMRSuccessModal(emrResult, fhirData) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    const content = document.createElement('div');
    content.className = 'modal-content';
    content.style.maxWidth = '700px';
    
    // Extract all codes from FHIR resource
    let tmCode = '';
    let icd11StandardCode = '';
    let icd11TM2Code = '';
    
    try {
        const resource = emrResult.resource || fhirData;
        if (resource && resource.code && resource.code.coding) {
            const codings = resource.code.coding;
            
            // Separate Traditional Medicine and ICD-11 codes
            codings.forEach(coding => {
                const system = coding.system || '';
                const code = coding.code || 'N/A';
                const display = coding.display || '';
                
                if (system.includes('/siddha') || system.includes('/ayurveda') || system.includes('/unani')) {
                    // Traditional Medicine code
                    tmCode = `${code} - ${display}`;
                } else if (system.includes('/mms')) {
                    // ICD-11 Standard (MMS)
                    icd11StandardCode = `${code} - ${display}`;
                } else if (system.includes('/tm2')) {
                    // ICD-11 TM2
                    icd11TM2Code = `${code} - ${display}`;
                }
            });
        }
    } catch (e) {
        console.log('Could not extract codes:', e);
    }
    
    content.innerHTML = `
        <h2 style="color: var(--success-color);"><i class="fas fa-check-circle"></i> Successfully Sent to EMR!</h2>
        
        <div style="margin-top: 20px; padding: 20px; background: var(--light-gray); border-radius: 8px;">
            <div style="margin-bottom: 15px;">
                <strong><i class="fas fa-id-card"></i> Resource ID:</strong>
                <div style="font-family: monospace; margin-top: 5px; color: var(--primary-color);">
                    ${emrResult.resource_id || 'N/A'}
                </div>
            </div>
            
            ${tmCode ? `
                <div style="margin-bottom: 15px;">
                    <strong><i class="fas fa-leaf"></i> Traditional Medicine:</strong>
                    <div style="margin-top: 5px; padding: 10px; background: #d4edda; border-radius: 4px; font-weight: 500;">
                        ${tmCode}
                    </div>
                </div>
            ` : ''}
            
            ${icd11StandardCode ? `
                <div style="margin-bottom: 15px;">
                    <strong><i class="fas fa-hospital"></i> ICD-11 Standard (MMS):</strong>
                    <div style="margin-top: 5px; padding: 10px; background: #cce5ff; border-radius: 4px; font-weight: 500;">
                        ${icd11StandardCode}
                    </div>
                </div>
            ` : ''}
            
            ${icd11TM2Code ? `
                <div style="margin-bottom: 15px;">
                    <strong><i class="fas fa-spa"></i> ICD-11 TM2:</strong>
                    <div style="margin-top: 5px; padding: 10px; background: #e7f3ff; border-radius: 4px; font-weight: 500;">
                        ${icd11TM2Code}
                    </div>
                </div>
            ` : ''}
            
            <div>
                <strong><i class="fas fa-hospital"></i> View in FHIR Server:</strong>
                <div style="margin-top: 10px;">
                    <a href="http://localhost:8090/fhir/Condition/${emrResult.resource_id}" target="_blank" 
                       style="color: var(--primary-color); word-break: break-all; display: block; padding: 10px; background: white; border-radius: 4px; text-decoration: none;">
                        <i class="fas fa-external-link-alt"></i> http://localhost:8090/fhir/Condition/${emrResult.resource_id}
                    </a>
                </div>
                <div style="margin-top: 10px; padding: 10px; background: #e8f5e9; border-radius: 4px; font-size: 0.9em;">
                    <i class="fas fa-info-circle"></i> Click the link above to view the stored FHIR Condition resource in your browser
                </div>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <details style="cursor: pointer;">
                <summary style="font-weight: 600; padding: 10px; background: var(--light-gray); border-radius: 8px;">
                    <i class="fas fa-code"></i> View Full FHIR Response
                </summary>
                <pre style="margin-top: 10px; padding: 15px; background: #f5f5f5; border-radius: 8px; overflow-x: auto; font-size: 12px; max-height: 300px; overflow-y: auto;">${JSON.stringify(emrResult.resource || emrResult, null, 2)}</pre>
            </details>
        </div>
        
        <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button class="btn btn-primary" onclick="window.open('http://localhost:8000/ui/emr_viewer.html', '_blank')">
                <i class="fas fa-hospital"></i> Open EMR Viewer
            </button>
            <button class="btn btn-secondary" onclick="window.open('http://localhost:8090/fhir/Condition/${emrResult.resource_id}', '_blank')">
                <i class="fas fa-code"></i> View FHIR JSON
            </button>
            <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                <i class="fas fa-times"></i> Close
            </button>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };
}
