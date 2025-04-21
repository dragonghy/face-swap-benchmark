/**
 * Face Swap Benchmark UI
 * 
 * This file contains the JavaScript code for the Face Swap Benchmark web interface.
 * It handles loading test cases, running benchmarks, and displaying results.
 */

// Main application namespace
const BenchmarkApp = {
  // DOM elements
  elements: {
    app: null,
    logContainer: null,
    resultsSection: null
  },
  
  // Application state
  state: {
    cases: [],
    tools: [],
    selectedCases: [],
    selectedTools: [],
    runId: null,
    pollingInterval: null,
    noUpdateCount: 0,
    lastUpdateTime: Date.now(),
    scoredCount: 0,
    totalItems: 0
  },
  
  /**
   * Initialize the application
   */
  async init() {
    this.elements.app = document.querySelector('#app main');
    
    try {
      // Fetch test cases and tools
      await this.fetchData();
      
      // Render the UI
      this.renderControls();
      this.createLogContainer();
      
    } catch (error) {
      console.error('Error initializing application:', error);
      this.showError('Failed to initialize application', error.message);
    }
  },
  
  /**
   * Fetch test cases and tools from the API
   */
  async fetchData() {
    const [casesResponse, toolsResponse] = await Promise.all([
      fetch('/api/test-cases'),
      fetch('/api/tools')
    ]);
    
    this.state.cases = await casesResponse.json();
    this.state.tools = await toolsResponse.json();
    
    console.log('Loaded data:', { 
      cases: this.state.cases.length, 
      tools: this.state.tools.length 
    });
  },
  
  /**
   * Create a container for log messages
   */
  createLogContainer() {
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
    this.elements.app.appendChild(logPre);
    this.elements.logContainer = logPre;
  },
  
  /**
   * Render the controls section (test cases and tools)
   */
  renderControls() {
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'controls-container';
    
    // Test cases selector
    const casesDiv = this.renderTestCases();
    controlsDiv.appendChild(casesDiv);
    
    // Tools selector
    const toolsDiv = this.renderTools();
    controlsDiv.appendChild(toolsDiv);
    
    // Run button
    const runButton = document.createElement('button');
    runButton.textContent = 'Run Benchmark';
    runButton.addEventListener('click', () => this.runBenchmark());
    controlsDiv.appendChild(runButton);
    
    this.elements.app.appendChild(controlsDiv);
  },
  
  /**
   * Render the test cases selection UI
   */
  renderTestCases() {
    const casesDiv = document.createElement('div');
    casesDiv.innerHTML = '<h2>Test Cases</h2>';
    casesDiv.style.marginBottom = '20px';
    
    this.state.cases.forEach(tc => {
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
    
    return casesDiv;
  },
  
  /**
   * Render the tools selection UI
   */
  renderTools() {
    const toolsDiv = document.createElement('div');
    toolsDiv.innerHTML = '<h2>Tools</h2>';
    
    this.state.tools.forEach(tool => {
      const label = document.createElement('label');
      label.innerHTML = `<input type="checkbox" value="${tool}" checked> ${tool}`;
      toolsDiv.appendChild(label);
      toolsDiv.appendChild(document.createElement('br'));
    });
    
    return toolsDiv;
  },
  
  /**
   * Run the benchmark with selected cases and tools
   */
  async runBenchmark() {
    // Collect selections
    this.state.selectedCases = Array.from(
      document.querySelectorAll('.controls-container input[type=checkbox]:checked')
    )
    .filter(el => this.state.cases.some(c => c.id === el.value))
    .map(el => el.value);
    
    this.state.selectedTools = Array.from(
      document.querySelectorAll('.controls-container input[type=checkbox]:checked')
    )
    .filter(el => this.state.tools.includes(el.value))
    .map(el => el.value);
    
    if (!this.state.selectedCases.length || !this.state.selectedTools.length) {
      alert('Please select at least one test case and one tool.');
      return;
    }
    
    // Disable controls
    const runButton = document.querySelector('.controls-container button');
    runButton.disabled = true;
    document.querySelectorAll('.controls-container input').forEach(i => i.disabled = true);
    this.elements.logContainer.textContent = 'Starting run...\n';
    
    // Render results table
    this.renderResultsTable();
    
    // Start the run
    try {
      const resp = await fetch('/api/run', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
          case_ids: this.state.selectedCases, 
          tool_ids: this.state.selectedTools 
        })
      });
      
      const { run_id } = await resp.json();
      this.state.runId = run_id;
      this.elements.logContainer.textContent += `Run ID: ${run_id}\n`;
      
      // Add export report button
      this.addReportButton();
      
      // Setup WebSocket and polling
      this.setupStatusMonitoring();
      
    } catch (error) {
      console.error('Error starting benchmark:', error);
      this.elements.logContainer.textContent += `Error: ${error.message}\n`;
    }
  },
  
  /**
   * Render the results table
   */
  renderResultsTable() {
    // Create results section if it doesn't exist
    if (!this.elements.resultsSection) {
      const resultsSection = document.createElement('div');
      resultsSection.innerHTML = '<h2>Results</h2>';
      this.elements.resultsSection = resultsSection;
      this.elements.app.appendChild(resultsSection);
    }
    
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
    
    this.state.selectedTools.forEach(tool => {
      const th = document.createElement('th'); 
      th.textContent = tool;
      th.style.padding = '10px';
      th.style.borderBottom = '2px solid #ddd';
      th.style.textAlign = 'center';
      header.appendChild(th);
    });
    
    table.appendChild(header);
    
    // Create a map for quick access to test case data
    const caseMap = new Map();
    this.state.cases.forEach(c => caseMap.set(c.id, c));
    
    // Data rows
    this.state.selectedCases.forEach(caseId => {
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
      this.state.selectedTools.forEach(tool => {
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
    
    // Calculate total items for tracking completion
    this.state.totalItems = this.state.selectedCases.length * this.state.selectedTools.length;
    this.state.scoredCount = 0;
    
    // Replace any existing table
    const existingTable = this.elements.resultsSection.querySelector('table');
    if (existingTable) {
      existingTable.replaceWith(table);
    } else {
      this.elements.resultsSection.appendChild(table);
    }
  },
  
  /**
   * Add the export report button
   */
  addReportButton() {
    if (this.elements.resultsSection.querySelector('.report-button')) {
      return; // Button already exists
    }
    
    const reportBtn = document.createElement('button');
    reportBtn.textContent = 'Export Report';
    reportBtn.className = 'report-button';
    reportBtn.disabled = true;
    reportBtn.style.marginTop = '20px';
    
    reportBtn.addEventListener('click', () => {
      window.location = `/api/report/${this.state.runId}`;
    });
    
    this.elements.resultsSection.appendChild(reportBtn);
  },
  
  /**
   * Setup WebSocket and polling for status updates
   */
  setupStatusMonitoring() {
    // WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/run/${this.state.runId}`);
    
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.updateUIWithStatus(msg);
        this.state.lastUpdateTime = Date.now();
      } catch (e) {
        console.error('Message parse error:', e);
      }
    };
    
    ws.onerror = (event) => {
      console.error('WebSocket error:', event.message || event);
      // Start polling as a fallback if WebSocket fails
      if (!this.state.pollingInterval) {
        console.log('Starting polling as WebSocket fallback');
        this.state.pollingInterval = setInterval(() => this.pollForStatus(), 3000);
      }
    };
    
    ws.onclose = (event) => {
      console.log(`WebSocket closed: code=${event.code} reason=${event.reason}`);
      // Start polling as a fallback if WebSocket closes
      if (!this.state.pollingInterval) {
        console.log('Starting polling as WebSocket closed');
        this.state.pollingInterval = setInterval(() => this.pollForStatus(), 3000);
      }
    };
    
    // Start polling anyway as a backup
    console.log('Starting background polling for updates');
    
    // Initial poll right away
    this.pollForStatus();
    
    // Then set up regular polling every 3 seconds
    this.state.pollingInterval = setInterval(() => this.pollForStatus(), 3000);
  },
  
  /**
   * Poll the API for status updates
   */
  async pollForStatus() {
    try {
      const response = await fetch(`/api/run/${this.state.runId}/status`);
      const statuses = await response.json();
      
      // Log the raw status data for debugging (only to console)
      console.log("Poll received statuses:", statuses);
      
      let foundUpdate = false;
      
      statuses.forEach(status => {
        const cell = document.getElementById(`cell-${status.case_id}-${status.tool_id}`);
        if (cell) {
          // Always update the UI if the status is not queued
          if (status.status !== 'queued') {
            this.updateUIWithStatus(status);
            foundUpdate = true;
          } else {
            // For queued items, check if they've been stuck for too long
            const statusDiv = cell.querySelector('div');
            if (statusDiv && statusDiv.textContent === 'queued') {
              // If it's been queued for more than 30 seconds, try to force an update
              if (Date.now() - this.state.lastUpdateTime > 30000) {
                this.updateUIWithStatus(status);
              }
            }
          }
        }
      });
      
      if (foundUpdate) {
        this.state.lastUpdateTime = Date.now();
        this.state.noUpdateCount = 0;
      } else {
        this.state.noUpdateCount++;
        if (this.state.noUpdateCount > 20) {  // If no updates after 20 polls (60 seconds), stop polling
          clearInterval(this.state.pollingInterval);
          console.log("Polling stopped due to inactivity.");
        }
      }
      
      // Check if all items are completed
      const allCompleted = statuses.length > 0 && statuses.every(s => s.status === 'scored' || s.status === 'evaluating');
      if (allCompleted) {
        const allScored = statuses.every(s => s.status === 'scored');
        if (allScored) {
          clearInterval(this.state.pollingInterval);
          console.log("All items scored. Polling stopped.");
          const reportBtn = this.elements.resultsSection.querySelector('.report-button');
          if (reportBtn) reportBtn.disabled = false;
        } else {
          console.log("All items completed. Waiting for final scores...");
        }
      }
    } catch (e) {
      console.error(`Polling error:`, e);
      this.state.noUpdateCount++;
    }
  },
  
  /**
   * Update the UI with status information
   */
  updateUIWithStatus(msg) {
    if (msg.run_id !== this.state.runId) return;
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
      this.state.scoredCount++;
      
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
    
    if (this.state.scoredCount === this.state.totalItems) {
      const reportBtn = this.elements.resultsSection.querySelector('.report-button');
      if (reportBtn) reportBtn.disabled = false;
    }
  },
  
  /**
   * Show an error message to the user
   */
  showError(title, message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-container';
    errorContainer.style.backgroundColor = '#ffdddd';
    errorContainer.style.padding = '15px';
    errorContainer.style.margin = '15px 0';
    errorContainer.style.borderRadius = '4px';
    errorContainer.style.borderLeft = '5px solid #f44336';
    
    const errorHeading = document.createElement('h3');
    errorHeading.textContent = title;
    errorHeading.style.margin = '0 0 10px 0';
    errorHeading.style.color = '#f44336';
    
    const errorMessage = document.createElement('div');
    errorMessage.textContent = message;
    
    errorContainer.appendChild(errorHeading);
    errorContainer.appendChild(errorMessage);
    this.elements.app.appendChild(errorContainer);
  }
};

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  BenchmarkApp.init();
});