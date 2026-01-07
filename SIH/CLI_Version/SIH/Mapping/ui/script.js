const API = "http://127.0.0.1:8000";

const input = document.getElementById("autocompleteInput");
const dropdown = document.getElementById("autocompleteDropdown");

// Current selected system
let currentSystem = "siddha";

// Update system labels
function onSystemChange() {
    currentSystem = document.getElementById("systemSelector").value;
    const systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
    
    document.getElementById("systemLabel").textContent = systemName;
    document.getElementById("systemLabel2").textContent = systemName;
    document.getElementById("systemLabel3").textContent = systemName;
    
    // Clear previous results
    input.value = "";
    dropdown.style.display = "none";
    mappingInput.value = "";
    mappingDropdown.style.display = "none";
    document.getElementById("autocompleteResults").innerHTML = "";
    document.getElementById("diagnosisResults").innerHTML = "";
    document.getElementById("mappingResults").innerHTML = "";
    document.getElementById("icdResults").innerHTML = "";
}

// ----------------------------------
// GOOGLE-STYLE AUTOCOMPLETE WITH FALLBACK
// ----------------------------------
input.addEventListener("input", async function () {
    const q = input.value.trim();

    if (q.length < 2) {
        dropdown.style.display = "none";
        return;
    }

    try {
        const res = await fetch(`${API}/${currentSystem}/autocomplete?q=${q}`);
        const data = await res.json();
        const results = data.results || [];
        const source = data.source || 'local';
        const message = data.message || '';

        dropdown.innerHTML = "";
        
        if (results.length === 0) {
            dropdown.style.display = "none";
            return;
        }
        
        dropdown.style.display = "block";

        // Add header based on source type
        if (source === 'fuzzy_match') {
            const header = document.createElement("div");
            header.style.cssText = "padding: 8px 12px; font-size: 0.85em; color: #ff9800; border-bottom: 1px solid #e0e0e0; background: #fff3e0; font-weight: 600;";
            header.innerHTML = `💡 ${message}`;
            dropdown.appendChild(header);
        } else if (source === 'google_fallback') {
            const header = document.createElement("div");
            header.style.cssText = "padding: 8px 12px; font-size: 0.85em; color: #ff6b00; border-bottom: 1px solid #e0e0e0; background: #fff8f0; font-weight: 600;";
            header.innerHTML = `🌐 ${message}`;
            dropdown.appendChild(header);
        }

        results.forEach(item => {
            const div = document.createElement("div");
            div.className = "dropdown-item";
            
            // Different styling for Google results
            if (item.source === 'google_search') {
                div.style.borderLeft = "3px solid #4285f4";
                div.innerHTML = `
                    <div class="item-title"><b>🔍 ${item.term}</b></div>
                    <div class="item-def">${item.definition.slice(0, 120)}${item.definition.length > 120 ? '...' : ''}</div>
                    <div style="font-size: 0.75em; color: #4285f4; margin-top: 4px;">Web Result</div>
                `;
            } else {
                div.innerHTML = `
                    <div class="item-title"><b>${item.code}</b> — ${item.term}</div>
                    <div class="item-def">${item.definition.slice(0, 120)}...</div>
                `;
            }

            div.onclick = () => {
                if (item.source === 'google_search') {
                    input.value = item.term;
                } else {
                    input.value = `${item.code} — ${item.term}`;
                }
                dropdown.style.display = "none";

                const systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
                document.getElementById("autocompleteResults").innerHTML = `
                    <div class="card">
                        <h3>Selected ${systemName} Entry</h3>
                        ${item.source === 'google_search' ? 
                            `<p style="color: #4285f4; margin-bottom: 10px;">🌐 Web Search Result</p>
                             <p><strong>Term:</strong> ${item.term}</p>
                             <p><strong>Description:</strong> ${item.definition}</p>
                             ${item.link ? `<p><a href="${item.link}" target="_blank" style="color: #0066ff;">View Source →</a></p>` : ''}` :
                            `<pre>${JSON.stringify(item, null, 2)}</pre>`
                        }
                    </div>
                `;
            };

            dropdown.appendChild(div);
        });
    } catch (error) {
        console.error('Autocomplete error:', error);
        dropdown.style.display = "none";
    }
});

// ----------------------------------
// MAPPING INPUT AUTOCOMPLETE
// ----------------------------------
const mappingInput = document.getElementById("mappingInput");
const mappingDropdown = document.getElementById("mappingDropdown");

mappingInput.addEventListener("input", async function () {
    const q = mappingInput.value.trim();

    if (q.length < 2) {
        mappingDropdown.style.display = "none";
        return;
    }

    try {
        const res = await fetch(`${API}/${currentSystem}/autocomplete?q=${q}`);
        const data = await res.json();
        const results = data.results || [];
        const source = data.source || 'local';
        const message = data.message || '';

        mappingDropdown.innerHTML = "";
        
        if (results.length === 0) {
            mappingDropdown.style.display = "none";
            return;
        }
        
        mappingDropdown.style.display = "block";

        // Add header based on source
        const header = document.createElement("div");
        if (source === 'fuzzy_match') {
            header.style.cssText = "padding: 8px 12px; font-size: 0.85em; color: #ff9800; border-bottom: 1px solid #e0e0e0; background: #fff3e0; font-weight: 600;";
            header.innerHTML = `💡 ${message}`;
        } else if (source === 'google_fallback') {
            header.style.cssText = "padding: 8px 12px; font-size: 0.85em; color: #ff6b00; border-bottom: 1px solid #e0e0e0; background: #fff8f0; font-weight: 600;";
            header.innerHTML = `🌐 ${message}`;
        } else {
            header.style.cssText = "padding: 8px 12px; font-size: 0.85em; color: #666; border-bottom: 1px solid #e0e0e0; background: #f9f9f9;";
            header.innerHTML = `<i>💡 Suggestions...</i>`;
        }
        mappingDropdown.appendChild(header);

        results.forEach(item => {
            const div = document.createElement("div");
            div.className = "dropdown-item";

            const displayTerm = item.english || item.term;
            const definition = item.definition || 'No description available.';

            // Different styling for Google results
            if (item.source === 'google_search') {
                div.style.borderLeft = "3px solid #4285f4";
                div.innerHTML = `
                    <div class="item-title"><b>🔍 ${displayTerm}</b></div>
                    <div class="item-def">${definition.slice(0, 120)}${definition.length > 120 ? '...' : ''}</div>
                    <div style="font-size: 0.75em; color: #4285f4; margin-top: 4px;">Web Result</div>
                `;
            } else {
                div.innerHTML = `
                    <div class="item-title"><b>${item.code}</b> — ${displayTerm}</div>
                    <div class="item-def">${definition.slice(0, 120)}${definition.length > 120 ? '...' : ''}</div>
                `;
            }

            div.onclick = () => {
                mappingInput.value = displayTerm;
                mappingDropdown.style.display = "none";
                
                // Optionally auto-trigger mapping
                // runMapping();
            };

            mappingDropdown.appendChild(div);
        });
    } catch (error) {
        console.error('Autocomplete error:', error);
        mappingDropdown.style.display = "none";
    }
});

// Hide dropdown when clicking outside
document.addEventListener('click', function(event) {
    if (!mappingInput.contains(event.target) && !mappingDropdown.contains(event.target)) {
        mappingDropdown.style.display = "none";
    }
    if (!input.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = "none";
    }
});

// ----------------------------------
// DIAGNOSIS
// ----------------------------------
async function runDiagnosis() {
    const symptoms = document.getElementById("diagnosisInput").value;

    const res = await fetch(`${API}/${currentSystem}/diagnose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms })
    });

    const data = await res.json();

    // Display diagnosis results with better formatting
    let resultsHTML = '<div class="card"><h3>Top Diagnosis Candidates</h3>';
    
    if (data.candidates && data.candidates.length > 0) {
        data.candidates.forEach((candidate, index) => {
            const displayTerm = candidate.english || candidate.term;
            const originalTerm = candidate.term || '';
            const definition = candidate.definition || '';
            
            resultsHTML += `
                <div class="diagnosis-result" style="padding: 12px; margin: 10px 0; background: #f8f9fa; border-left: 4px solid #0066ff; border-radius: 4px;">
                    <div><strong>${index + 1}. ${candidate.code}</strong> — ${displayTerm}</div>
                    ${originalTerm && originalTerm !== displayTerm ? `<div style="font-size: 0.9em; color: #666; margin-top: 4px;">Original: ${originalTerm}</div>` : ''}
                    ${definition && definition !== 'No description available.' ? `<div style="font-size: 0.85em; color: #555; margin-top: 6px;">${definition}</div>` : ''}
                    <div style="margin-top: 6px;"><small>Confidence Score: ${candidate.score.toFixed(4)}</small></div>
                </div>
            `;
        });
    } else {
        resultsHTML += '<p>No results found</p>';
    }
    
    resultsHTML += '</div>';
    
    document.getElementById("diagnosisResults").innerHTML = resultsHTML;
}

// ----------------------------------
// FULL MAPPING
// ----------------------------------
async function runMapping() {
    const query = document.getElementById("mappingInput").value;

    const res = await fetch(`${API}/map`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, system: currentSystem })
    });

    const data = await res.json();

    // Format system name for display
    let systemName;
    if (currentSystem === 'ayurveda-sat') {
        systemName = 'Ayurveda-SAT';
    } else {
        systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
    }
    
    // Normalize system key (replace hyphen with underscore)
    const systemKey = currentSystem.replace('-', '_');
    const candidatesKey = `${systemKey}_candidates`;
    
    console.log('runMapping - System:', currentSystem);
    console.log('runMapping - Candidates Key:', candidatesKey);
    console.log('runMapping - Data:', data);
    
    // Check if candidates exist
    if (!data[candidatesKey] || data[candidatesKey].length === 0) {
        console.error('No candidates found for key:', candidatesKey);
        document.getElementById("mappingResults").innerHTML = `<div class="card"><p style="color: red;">No ${systemName} candidates found.</p></div>`;
        return;
    }
    
    // Display candidates as clickable cards with definitions
    let candidatesHTML = `<div class="card"><h3>${systemName} Candidates (Click to map to ICD)</h3>`;
    
    data[candidatesKey].forEach((candidate) => {
        const displayTerm = candidate.english || candidate.term;
        const originalTerm = candidate.term || '';
        const definition = candidate.definition || '';
        
        candidatesHTML += `
            <div class="siddha-candidate" onclick="mapToICD('${candidate.code}', '${displayTerm.replace(/'/g, "\\'")}')">
                <div><strong>${candidate.code}</strong> — ${displayTerm}</div>
                ${originalTerm && originalTerm !== displayTerm ? `<div style="font-size: 0.9em; color: #666; margin-top: 4px;">Original: ${originalTerm}</div>` : ''}
                ${definition && definition !== 'No description available.' ? `<div style="font-size: 0.85em; color: #555; margin-top: 6px; font-style: italic;">${definition.slice(0, 150)}${definition.length > 150 ? '...' : ''}</div>` : ''}
                <div style="margin-top: 6px;"><small>Score: ${candidate.score.toFixed(4)}</small></div>
            </div>
        `;
    });
    
    candidatesHTML += '</div>';
    
    document.getElementById("mappingResults").innerHTML = candidatesHTML;
    document.getElementById("icdResults").innerHTML = '';
}

// ----------------------------------
// MAP SPECIFIC SYSTEM TO ICD
// ----------------------------------
async function mapToICD(code, term) {
    // Format system name for display
    let systemName;
    if (currentSystem === 'ayurveda-sat') {
        systemName = 'Ayurveda-SAT';
    } else {
        systemName = currentSystem.charAt(0).toUpperCase() + currentSystem.slice(1);
    }
    
    const res = await fetch(`${API}/map/${currentSystem}-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, term })
    });

    const data = await res.json();

    // Debug logging
    console.log('API Response:', data);
    console.log('Current System:', currentSystem);

    // Normalize system key (replace hyphen with underscore for object key access)
    const systemKey = currentSystem.replace('-', '_');
    console.log('System Key:', systemKey);
    console.log('Candidates Key:', `${systemKey}_candidates`);
    console.log('Candidates:', data[`${systemKey}_candidates`]);

    // Check if data is valid (allow empty arrays, just check if keys exist)
    if (!data.hasOwnProperty('icd11_standard_candidates') || !data.hasOwnProperty('icd11_tm2_candidates')) {
        console.error('Missing ICD candidates keys in response:', data);
        alert('Error: ICD mapping data structure is invalid. Please check the console for details.');
        return;
    }
    
    // Log the ICD candidates for debugging
    console.log('ICD-11 Standard Candidates:', data.icd11_standard_candidates);
    console.log('ICD-11 TM2 Candidates:', data.icd11_tm2_candidates);

    // Store mapping result and selected TM candidate for FHIR export
    window.currentMappingResult = data;
    
    const tmCandidates = data[`${systemKey}_candidates`];
    if (!tmCandidates || tmCandidates.length === 0) {
        console.error('No TM candidates found for key:', `${systemKey}_candidates`);
        alert('Error: Traditional Medicine candidates not found in response.');
        return;
    }

    window.selectedTMCandidate = {
        system: currentSystem,
        code: code,
        term: term,
        data: tmCandidates.find(c => c.code === code)
    };
    window.selectedICD11Standard = null;
    window.selectedICD11TM2 = null;

    // Display ICD-11 Standard and ICD-11 TM2 results side by side
    let icdHTML = `
        <div class="card">
            <h3>Selected ${systemName}: ${code} — ${term}</h3>
            <p style="color: #666; font-size: 0.9em; margin-top: 10px;">
                Click on ICD-11 codes below to select them for FHIR export
            </p>
            <div id="selectionStatus" style="margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 4px; display: none;">
                <strong>Selected for FHIR Export:</strong>
                <div id="selectedCodes" style="margin-top: 5px;"></div>
            </div>
            <button class="btn btn-secondary" onclick="exportFHIR()" style="margin-top: 10px;" id="exportBtn" disabled>
                📋 Export as FHIR JSON (Bahmni EMR)
            </button>
            <p style="color: #999; font-size: 0.85em; margin-top: 5px;">
                Select at least one ICD-11 code to enable export
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="card">
                <h3>ICD-11 Standard (Click to Select)</h3>
                ${formatICDResults(data.icd11_standard_candidates, 'standard')}
            </div>
            
            <div class="card">
                <h3>ICD-11 TM2 (Click to Select)</h3>
                ${formatICDResults(data.icd11_tm2_candidates, 'tm2')}
            </div>
        </div>
    `;
    
    document.getElementById("icdResults").innerHTML = icdHTML;
}

// ----------------------------------
// EXPORT FHIR JSON
// ----------------------------------
async function exportFHIR() {
    if (!window.selectedTMCandidate) {
        alert('No Traditional Medicine candidate selected');
        return;
    }
    
    if (!window.selectedICD11Standard && !window.selectedICD11TM2) {
        alert('Please select at least one ICD-11 code (Standard or TM2)');
        return;
    }
    
    try {
        // Build custom mapping result with only selected codes
        // Normalize system key (replace hyphen with underscore)
        const systemKey = window.selectedTMCandidate.system.replace('-', '_');
        const customMappingResult = {
            system: window.selectedTMCandidate.system,
            input: window.currentMappingResult.input || "",
            [`${systemKey}_candidates`]: [window.selectedTMCandidate.data],
            icd11_standard_candidates: window.selectedICD11Standard ? [window.selectedICD11Standard] : [],
            icd11_tm2_candidates: window.selectedICD11TM2 ? [window.selectedICD11TM2] : []
        };
        
        const res = await fetch(`${API}/fhir/condition`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
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
        
        // Create downloadable JSON file
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
        
        // Also display in a modal
        showFHIRModal(fhirData);
        
    } catch (error) {
        console.error('Error exporting FHIR:', error);
        alert('Error generating FHIR JSON: ' + error.message);
    }
}

function showFHIRModal(fhirData) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 8px;
        max-width: 800px;
        max-height: 80vh;
        overflow: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;
    
    content.innerHTML = `
        <h2>FHIR Condition Resource (Bahmni EMR Format)</h2>
        <p style="color: #666; margin-bottom: 20px;">
            This FHIR R4 Condition resource is compatible with Bahmni EMR and includes 
            Traditional Medicine and ICD-11 mappings.
        </p>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow: auto; max-height: 400px;">${JSON.stringify(fhirData, null, 2)}</pre>
        <button class="btn" onclick="this.parentElement.parentElement.remove()" style="margin-top: 15px;">Close</button>
        <button class="btn btn-secondary" onclick="copyToClipboard('${JSON.stringify(fhirData).replace(/'/g, "\\'")}'); alert('Copied to clipboard!')" style="margin-top: 15px; margin-left: 10px;">Copy JSON</button>
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
}

// ----------------------------------
// FORMAT ICD RESULTS (CLICKABLE)
// ----------------------------------
function formatICDResults(candidates, type) {
    if (!candidates || candidates.length === 0) {
        return '<p>No results found</p>';
    }
    
    let html = '<div class="icd-list">';
    
    candidates.forEach((candidate, index) => {
        const definition = candidate.definition || '';
        const candidateJson = JSON.stringify(candidate).replace(/"/g, '&quot;');
        
        html += `
            <div class="icd-item icd-selectable" 
                 onclick="selectICDCode('${type}', ${index}, this)" 
                 data-candidate='${candidateJson}'
                 id="icd-${type}-${index}">
                <div><strong>${index + 1}. ${candidate.code}</strong></div>
                <div style="margin-top: 4px; font-weight: 500;">${candidate.title}</div>
                ${definition ? `<div style="font-size: 0.85em; color: #555; margin-top: 6px; line-height: 1.4;">${definition.slice(0, 200)}${definition.length > 200 ? '...' : ''}</div>` : ''}
                <div style="margin-top: 6px;"><small>Score: ${candidate.score.toFixed(4)}</small></div>
                <div class="selection-indicator" style="display: none;">✓ Selected</div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// ----------------------------------
// SELECT ICD CODE
// ----------------------------------
function selectICDCode(type, index, element) {
    const candidate = JSON.parse(element.getAttribute('data-candidate'));
    
    if (type === 'standard') {
        // Deselect previous standard selection
        document.querySelectorAll('.icd-item[id^="icd-standard-"]').forEach(el => {
            el.classList.remove('selected');
            el.querySelector('.selection-indicator').style.display = 'none';
        });
        
        // Select new one
        element.classList.add('selected');
        element.querySelector('.selection-indicator').style.display = 'block';
        window.selectedICD11Standard = candidate;
    } else if (type === 'tm2') {
        // Deselect previous tm2 selection
        document.querySelectorAll('.icd-item[id^="icd-tm2-"]').forEach(el => {
            el.classList.remove('selected');
            el.querySelector('.selection-indicator').style.display = 'none';
        });
        
        // Select new one
        element.classList.add('selected');
        element.querySelector('.selection-indicator').style.display = 'block';
        window.selectedICD11TM2 = candidate;
    }
    
    updateSelectionStatus();
}

// ----------------------------------
// UPDATE SELECTION STATUS
// ----------------------------------
function updateSelectionStatus() {
    const statusDiv = document.getElementById('selectionStatus');
    const selectedCodesDiv = document.getElementById('selectedCodes');
    const exportBtn = document.getElementById('exportBtn');
    
    let selectedCodes = [];
    
    if (window.selectedTMCandidate) {
        const systemName = window.selectedTMCandidate.system.charAt(0).toUpperCase() + 
                          window.selectedTMCandidate.system.slice(1);
        selectedCodes.push(`${systemName}: ${window.selectedTMCandidate.code}`);
    }
    
    if (window.selectedICD11Standard) {
        selectedCodes.push(`ICD-11 Standard: ${window.selectedICD11Standard.code}`);
    }
    
    if (window.selectedICD11TM2) {
        selectedCodes.push(`ICD-11 TM2: ${window.selectedICD11TM2.code}`);
    }
    
    if (selectedCodes.length > 1) { // At least TM + one ICD
        statusDiv.style.display = 'block';
        selectedCodesDiv.innerHTML = selectedCodes.map(code => 
            `<div style="padding: 4px 0;">✓ ${code}</div>`
        ).join('');
        exportBtn.disabled = false;
        exportBtn.style.opacity = '1';
        exportBtn.style.cursor = 'pointer';
    } else {
        statusDiv.style.display = 'none';
        exportBtn.disabled = true;
        exportBtn.style.opacity = '0.5';
        exportBtn.style.cursor = 'not-allowed';
    }
}
