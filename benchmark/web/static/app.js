// JavaScript for Face Swap Benchmark UI
document.addEventListener('DOMContentLoaded', async () => {
  const app = document.getElementById('app');
  // Fetch test cases and tools
  const cases = await fetch('/api/test-cases').then(res => res.json());
  const tools = await fetch('/api/tools').then(res => res.json());
  // Controls container
  const controlsDiv = document.createElement('div');
  // Test cases selector
  const casesDiv = document.createElement('div');
  casesDiv.innerHTML = '<h2>Test Cases</h2>';
  casesDiv.style.marginBottom = '20px';
  
  cases.forEach(tc => {
    const caseContainer = document.createElement('div');
    caseContainer.style.marginBottom = '15px';
    caseContainer.style.padding = '10px';
    caseContainer.style.border = '1px solid #ccc';
    caseContainer.style.borderRadius = '5px';
    
    // Checkbox and label
    const label = document.createElement('label');
    label.style.fontWeight = 'bold';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = tc.id;
    checkbox.checked = true;
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(` ${tc.id} - ${tc.description || ''}`));
    caseContainer.appendChild(label);
    caseContainer.appendChild(document.createElement('br'));
    
    // Case details
    if (tc.instructions) {
      const instructions = document.createElement('div');
      instructions.textContent = tc.instructions;
      instructions.style.margin = '5px 0';
      instructions.style.fontStyle = 'italic';
      caseContainer.appendChild(instructions);
    }
    
    // Image previews container
    const imagesContainer = document.createElement('div');
    imagesContainer.style.display = 'flex';
    imagesContainer.style.flexWrap = 'wrap';
    imagesContainer.style.gap = '10px';
    imagesContainer.style.marginTop = '10px';
    
    // Template image
    if (tc.template_url) {
      const imgDiv = document.createElement('div');
      imgDiv.style.textAlign = 'center';
      
      const img = document.createElement('img');
      img.src = tc.template_url;
      img.width = 150;
      img.style.border = '1px solid #ddd';
      img.alt = 'Template';
      imgDiv.appendChild(img);
      
      const caption = document.createElement('div');
      caption.textContent = 'Template';
      caption.style.fontSize = '0.9em';
      caption.style.marginTop = '5px';
      imgDiv.appendChild(caption);
      
      imagesContainer.appendChild(imgDiv);
    }
    
    // Avatar images
    if (tc.avatar_urls && tc.avatar_urls.length) {
      tc.avatar_urls.forEach((url, index) => {
        const imgDiv = document.createElement('div');
        imgDiv.style.textAlign = 'center';
        
        const img = document.createElement('img');
        img.src = url;
        img.width = 100;
        img.style.border = '1px solid #ddd';
        img.alt = `Avatar ${index + 1}`;
        imgDiv.appendChild(img);
        
        const caption = document.createElement('div');
        caption.textContent = `Avatar ${index + 1}`;
        caption.style.fontSize = '0.9em';
        caption.style.marginTop = '5px';
        imgDiv.appendChild(caption);
        
        imagesContainer.appendChild(imgDiv);
      });
    }
    
    caseContainer.appendChild(imagesContainer);
    casesDiv.appendChild(caseContainer);
  });
  controlsDiv.appendChild(casesDiv);
  // Tools selector
  const toolsDiv = document.createElement('div');
  toolsDiv.innerHTML = '<h2>Tools</h2>';
  tools.forEach(tool => {
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" value="${tool}" checked> ${tool}`;
    toolsDiv.appendChild(label);
    toolsDiv.appendChild(document.createElement('br'));
  });
  controlsDiv.appendChild(toolsDiv);
  // Run button
  const runButton = document.createElement('button');
  runButton.textContent = 'Run Benchmark';
  controlsDiv.appendChild(runButton);
  app.appendChild(controlsDiv);
  // Log area (smaller, less obtrusive)
  const logPre = document.createElement('pre');
  logPre.id = 'log';
  logPre.style.fontSize = '0.8em';
  logPre.style.color = '#666';
  logPre.style.maxHeight = '100px';
  logPre.style.overflow = 'auto';
  logPre.style.padding = '5px';
  logPre.style.border = '1px solid #ddd';
  logPre.style.borderRadius = '3px';
  logPre.style.backgroundColor = '#f9f9f9';
  logPre.style.marginTop = '20px';
  app.appendChild(logPre);

  runButton.addEventListener('click', async () => {
    // Collect selections
    const selectedCases = Array.from(casesDiv.querySelectorAll('input[type=checkbox]:checked')).map(el => el.value);
    const selectedTools = Array.from(toolsDiv.querySelectorAll('input[type=checkbox]:checked')).map(el => el.value);
    if (!selectedCases.length || !selectedTools.length) {
      alert('Please select at least one test case and one tool.');
      return;
    }
    // Disable controls
    runButton.disabled = true;
    casesDiv.querySelectorAll('input').forEach(i => i.disabled = true);
    toolsDiv.querySelectorAll('input').forEach(i => i.disabled = true);
    logPre.textContent = 'Starting run...\n';

    // Prepare results table
    const resultsSection = document.createElement('div');
    resultsSection.innerHTML = '<h2>Results</h2>';
    
    const table = document.createElement('table');
    table.id = 'results';
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.marginTop = '20px';
    
    // Header row
    const header = document.createElement('tr');
    header.style.backgroundColor = '#f3f3f3';
    
    const caseHeader = document.createElement('th');
    caseHeader.textContent = 'Test Case';
    caseHeader.style.padding = '10px';
    caseHeader.style.borderBottom = '2px solid #ddd';
    caseHeader.style.textAlign = 'left';
    header.appendChild(caseHeader);
    
    selectedTools.forEach(tool => {
      const th = document.createElement('th'); 
      th.textContent = tool;
      th.style.padding = '10px';
      th.style.borderBottom = '2px solid #ddd';
      th.style.textAlign = 'center';
      header.appendChild(th);
    });
    table.appendChild(header);
    
    // Look up the test cases to get input images
    const caseMap = new Map();
    cases.forEach(c => caseMap.set(c.id, c));
    
    // Data rows
    selectedCases.forEach(caseId => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid #ddd';
      
      // Case cell with input images
      const tdCase = document.createElement('td');
      tdCase.style.padding = '10px';
      tdCase.style.verticalAlign = 'top';
      
      // Case ID and description
      const caseTitle = document.createElement('div');
      caseTitle.textContent = caseId;
      caseTitle.style.fontWeight = 'bold';
      caseTitle.style.marginBottom = '5px';
      tdCase.appendChild(caseTitle);
      
      // Get the case details
      const caseInfo = caseMap.get(caseId);
      if (caseInfo) {
        // Show description
        if (caseInfo.description) {
          const descDiv = document.createElement('div');
          descDiv.textContent = caseInfo.description;
          descDiv.style.fontSize = '0.9em';
          descDiv.style.marginBottom = '10px';
          tdCase.appendChild(descDiv);
        }
        
        // Show template and avatar thumbnails
        if (caseInfo.template_url || (caseInfo.avatar_urls && caseInfo.avatar_urls.length)) {
          const inputsDiv = document.createElement('div');
          inputsDiv.style.display = 'flex';
          inputsDiv.style.flexWrap = 'wrap';
          inputsDiv.style.gap = '5px';
          
          // Template image
          if (caseInfo.template_url) {
            const imgWrap = document.createElement('div');
            imgWrap.style.textAlign = 'center';
            
            const img = document.createElement('img');
            img.src = caseInfo.template_url;
            img.width = 80;
            img.height = 80;
            img.style.objectFit = 'cover';
            img.alt = 'Template';
            imgWrap.appendChild(img);
            
            const imgLabel = document.createElement('div');
            imgLabel.textContent = 'Template';
            imgLabel.style.fontSize = '0.8em';
            imgWrap.appendChild(imgLabel);
            
            inputsDiv.appendChild(imgWrap);
          }
          
          // Avatar images
          if (caseInfo.avatar_urls && caseInfo.avatar_urls.length) {
            caseInfo.avatar_urls.forEach((url, idx) => {
              const imgWrap = document.createElement('div');
              imgWrap.style.textAlign = 'center';
              
              const img = document.createElement('img');
              img.src = url;
              img.width = 60;
              img.height = 60;
              img.style.objectFit = 'cover';
              img.alt = `Avatar ${idx+1}`;
              imgWrap.appendChild(img);
              
              const imgLabel = document.createElement('div');
              imgLabel.textContent = `Avatar ${idx+1}`;
              imgLabel.style.fontSize = '0.8em';
              imgWrap.appendChild(imgLabel);
              
              inputsDiv.appendChild(imgWrap);
            });
          }
          
          tdCase.appendChild(inputsDiv);
        }
      }
      
      tr.appendChild(tdCase);
      
      // Tools results cells
      selectedTools.forEach(tool => {
        const td = document.createElement('td');
        td.id = `cell-${caseId}-${tool}`;
        td.textContent = 'queued';
        td.style.padding = '10px';
        td.style.textAlign = 'center';
        td.style.verticalAlign = 'top';
        tr.appendChild(td);
      });
      
      table.appendChild(tr);
    });
    
    resultsSection.appendChild(table);
    app.appendChild(resultsSection);

    // Start the run
    const resp = await fetch('/api/run', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ case_ids: selectedCases, tool_ids: selectedTools })
    });
    const { run_id: runId } = await resp.json();
    logPre.textContent += `Run ID: ${runId}\n`;

    // Export Report button
    const reportBtn = document.createElement('button');
    reportBtn.textContent = 'Export Report'; reportBtn.disabled = true;
    reportBtn.addEventListener('click', () => {
      window.location = `/api/report/${runId}`;
    });
    app.appendChild(reportBtn);

    // Track completion
    let scoredCount = 0;
    const total = selectedCases.length * selectedTools.length;

    // Function to update UI with run status data
    function updateUIWithStatus(msg) {
      if (msg.run_id !== runId) return;
      console.log(`Status update: ${msg.case_id} / ${msg.tool_id} = ${msg.status}`);
      
      const cell = document.getElementById(`cell-${msg.case_id}-${msg.tool_id}`);
      if (!cell) return;
      
      // Update cell content
      cell.innerHTML = '';
      
      // Status indicator
      const statusDiv = document.createElement('div'); 
      statusDiv.textContent = msg.status;
      statusDiv.style.fontWeight = 'bold';
      statusDiv.style.marginBottom = '5px';
      cell.appendChild(statusDiv);
      
      // Result image (if available)
      if (msg.image_url) {
        const img = document.createElement('img'); 
        img.src = msg.image_url; 
        img.width = 200;
        img.style.display = 'block';
        img.style.marginBottom = '10px';
        cell.appendChild(img);
      }
      
      // Score (if available)
      if (msg.score) {
        const scoreDiv = document.createElement('div'); 
        scoreDiv.textContent = `Score: ${msg.score}`;
        scoreDiv.style.marginBottom = '10px';
        cell.appendChild(scoreDiv);
      }
      
      // Rating controls for completed items
      if (msg.status === 'scored') {
        scoredCount++;
        
        // Human rating control
        const ratingDiv = document.createElement('div');
        ratingDiv.style.marginBottom = '10px';
        
        const label = document.createElement('label'); 
        label.textContent = 'Your Rating: ';
        ratingDiv.appendChild(label);
        
        const select = document.createElement('select');
        select.innerHTML = '<option value="">--</option>';
        for (let i = 1; i <= 5; i++) {
          const opt = document.createElement('option'); 
          opt.value = i; 
          opt.text = i + '★';
          select.appendChild(opt);
        }
        
        select.addEventListener('change', async () => {
          try {
            await fetch('/api/rate', {
              method: 'POST', 
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ run_item_id: msg.run_item_id, stars: select.value })
            });
          } catch (e) {
            console.error('Rating error:', e);
          }
        });
        
        ratingDiv.appendChild(select);
        cell.appendChild(ratingDiv);
      }
      
      if (scoredCount === total) reportBtn.disabled = false;
    }

    // Set up polling for status
    let pollingInterval = null;
    let noUpdateCount = 0;
    let lastUpdateTime = Date.now();
    
    async function pollForStatus() {
      try {
        const response = await fetch(`/api/run/${runId}/status`);
        const statuses = await response.json();
        
        // Log the raw status data for debugging (only to console)
        console.log("Poll received statuses:", statuses);
        
        let foundUpdate = false;
        
        statuses.forEach(status => {
          const cell = document.getElementById(`cell-${status.case_id}-${status.tool_id}`);
          if (cell) {
            // Always update the UI if the status is not queued
            if (status.status !== 'queued') {
              updateUIWithStatus(status);
              foundUpdate = true;
            } else {
              // For queued items, check if they've been stuck for too long
              const statusDiv = cell.querySelector('div');
              if (statusDiv && statusDiv.textContent === 'queued') {
                // If it's been queued for more than 30 seconds, try to force an update
                if (Date.now() - lastUpdateTime > 30000) {
                  updateUIWithStatus(status);
                }
              }
            }
          }
        });
        
        if (foundUpdate) {
          lastUpdateTime = Date.now();
          noUpdateCount = 0;
        } else {
          noUpdateCount++;
          if (noUpdateCount > 20) {  // If no updates after 20 polls (60 seconds), stop polling
            clearInterval(pollingInterval);
            console.log("Polling stopped due to inactivity.");
          }
        }
        
        // Check if all items are completed
        const allCompleted = statuses.length > 0 && statuses.every(s => s.status === 'scored' || s.status === 'evaluating');
        if (allCompleted) {
          const allScored = statuses.every(s => s.status === 'scored');
          if (allScored) {
            clearInterval(pollingInterval);
            console.log("All items scored. Polling stopped.");
            reportBtn.disabled = false;
          } else {
            console.log("All items completed. Waiting for final scores...");
          }
        }
      } catch (e) {
        console.error(`Polling error:`, e);
        noUpdateCount++;
      }
    }

    // Connect WebSocket for updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/run/${runId}`);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        updateUIWithStatus(msg);
        lastUpdateTime = Date.now();
      } catch (e) {
        console.error('Message parse error:', e);
      }
    };
    ws.onerror = (event) => {
      console.error('WebSocket error:', event.message || event);
      // Start polling as a fallback if WebSocket fails
      if (!pollingInterval) {
        console.log('Starting polling as WebSocket fallback');
        pollingInterval = setInterval(pollForStatus, 3000);
      }
    };
    ws.onclose = (event) => {
      console.log(`WebSocket closed: code=${event.code} reason=${event.reason}`);
      // Start polling as a fallback if WebSocket closes
      if (!pollingInterval) {
        console.log('Starting polling as WebSocket closed');
        pollingInterval = setInterval(pollForStatus, 3000);
      }
    };
    
    // Start polling anyway as a backup
    console.log('Starting background polling for updates');
    
    // Initial poll right away
    pollForStatus();
    
    // Then set up regular polling every 3 seconds
    pollingInterval = setInterval(pollForStatus, 3000);
  });
});