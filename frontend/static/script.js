// Project Samarth - Frontend JavaScript
// Handles user interactions, API calls, and data visualization

class SamarthApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentQuery = null;
        this.chatHistory = [];
        this.charts = {};
        
        this.init();
    }
    
    init() {
        // Load example queries
        this.loadExampleQueries();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize status
        this.updateStatus('ready', 'Ready');
    }
    
    setupEventListeners() {
        // Query input enter key
        document.getElementById('query-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitQuery();
            }
        });
        
        // Auto-resize chat messages
        window.addEventListener('resize', () => {
            this.scrollToBottom();
        });
    }
    
    async loadExampleQueries() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/examples`);
            const data = await response.json();
            
            if (data.success) {
                this.renderExampleQueries(data.examples);
            }
        } catch (error) {
            console.error('Error loading examples:', error);
        }
    }
    
    renderExampleQueries(examples) {
        const container = document.getElementById('example-queries');
        container.innerHTML = '';
        
        examples.forEach((example, index) => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-success btn-sm example-query-btn';
            button.textContent = example.query;
            button.title = example.description;
            button.onclick = () => this.useExampleQuery(example.query);
            
            container.appendChild(button);
        });
    }
    
    useExampleQuery(query) {
        document.getElementById('query-input').value = query;
        this.submitQuery();
    }
    
    async submitQuery() {
        const input = document.getElementById('query-input');
        const query = input.value.trim();
        
        if (!query) {
            this.showError('Please enter a question.');
            return;
        }
        
        // Clear input
        input.value = '';
        
        // Add user message to chat
        this.addUserMessage(query);
        
        // Show loading state
        this.updateStatus('processing', 'Processing');
        const loadingMessage = this.addLoadingMessage();
        
        try {
            // Call API
            const response = await fetch(`${this.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
            
            const data = await response.json();
            
            // Remove loading message
            this.removeLoadingMessage(loadingMessage);
            
            if (data.success) {
                this.addAssistantMessage(data);
                this.updateStatus('ready', 'Ready');
            } else {
                this.addErrorMessage(data.error || 'An error occurred while processing your query.');
                this.updateStatus('error', 'Error');
            }
            
        } catch (error) {
            console.error('API Error:', error);
            this.removeLoadingMessage(loadingMessage);
            this.addErrorMessage('Failed to connect to the server. Please try again.');
            this.updateStatus('error', 'Connection Error');
        }
    }
    
    addUserMessage(query) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-container user-message';
        messageDiv.innerHTML = `
            <div class="message-bubble user">
                <div class="d-flex align-items-start">
                    <div class="me-2">
                        <strong>You</strong>
                        <p class="mb-0">${this.escapeHtml(query)}</p>
                    </div>
                    <i class="bi bi-person-circle mt-1"></i>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addLoadingMessage() {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-container assistant-message loading-message';
        messageDiv.innerHTML = `
            <div class="message-bubble loading">
                <div class="d-flex align-items-start">
                    <i class="bi bi-robot me-2 mt-1"></i>
                    <div>
                        <strong>Samarth Assistant</strong>
                        <p class="mb-0">Analyzing your query<span class="loading-dots"></span></p>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    removeLoadingMessage(messageDiv) {
        if (messageDiv && messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }
    
    addAssistantMessage(data) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-container assistant-message';
        
        // Build confidence indicator
        const confidenceClass = this.getConfidenceClass(data.confidence);
        const confidenceIcon = this.getConfidenceIcon(data.confidence);
        
        let content = `
            <div class="message-bubble assistant">
                <div class="d-flex align-items-start">
                    <i class="bi bi-robot me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <strong>Samarth Assistant</strong>
                            <span class="confidence-indicator ${confidenceClass}" title="Confidence: ${Math.round(data.confidence * 100)}%">
                                <i class="bi ${confidenceIcon}"></i>
                            </span>
                        </div>
                        <p class="mb-2">${this.escapeHtml(data.answer)}</p>
        `;
        
        // Add statistics if available
        if (data.metadata && data.metadata.datasets_used) {
            content += `
                <div class="answer-stats">
                    <span class="stat-item">
                        <i class="bi bi-database me-1"></i>
                        ${data.metadata.datasets_used.length} datasets
                    </span>
                    <span class="stat-item">
                        <i class="bi bi-graph-up me-1"></i>
                        ${data.metadata.entities_found} entities found
                    </span>
                    ${data.cached ? `
                    <span class="stat-item bg-warning text-dark">
                        <i class="bi bi-lightning-charge me-1"></i>
                        Cached result
                    </span>
                    ` : `
                    <span class="stat-item bg-success text-white">
                        <i class="bi bi-cpu me-1"></i>
                        Fresh analysis
                    </span>
                    `}
                </div>
            `;
        }
        
        // Add data tables and charts
        if (data.data && Object.keys(data.data).length > 0) {
            content += this.renderDataTables(data.data);
        }
        
        if (data.visualizations && data.visualizations.length > 0) {
            content += this.renderCharts(data.visualizations, data.data);
        }
        
        // Add citations
        if (data.citations && data.citations.length > 0) {
            content += this.renderCitations(data.citations);
        }
        
        content += `
                    </div>
                </div>
            </div>
        `;
        
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Initialize any charts that were added
        this.initializeCharts(messageDiv, data.visualizations, data.data);
    }
    
    addErrorMessage(error) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-container assistant-message';
        messageDiv.innerHTML = `
            <div class="message-bubble assistant">
                <div class="d-flex align-items-start">
                    <i class="bi bi-exclamation-triangle-fill text-danger me-2 mt-1"></i>
                    <div>
                        <strong class="text-danger">Error</strong>
                        <div class="error-message">
                            ${this.escapeHtml(error)}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    renderDataTables(data) {
        let content = '';
        
        for (const [key, value] of Object.entries(data)) {
            if (value.data && value.data.length > 0) {
                content += `
                    <div class="data-table-container mt-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">${this.formatTableTitle(key)}</h6>
                            <button class="btn btn-outline-success btn-sm btn-view-data" 
                                    onclick="app.showDataModal('${key}', ${this.escapeForJson(JSON.stringify(value))})">
                                <i class="bi bi-table"></i> View Details
                            </button>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-striped table-hover data-table">
                                <thead>
                                    <tr>
                `;
                
                // Table headers
                if (value.columns && value.columns.length > 0) {
                    value.columns.forEach(col => {
                        content += `<th>${this.formatColumnName(col)}</th>`;
                    });
                }
                
                content += `
                                    </tr>
                                </thead>
                                <tbody>
                `;
                
                // Table rows (limit to first 5 for chat display)
                const displayRows = value.data.slice(0, 5);
                displayRows.forEach(row => {
                    content += `<tr>`;
                    value.columns.forEach(col => {
                        const cellValue = row[col];
                        content += `<td>${this.formatCellValue(cellValue)}</td>`;
                    });
                    content += `</tr>`;
                });
                
                if (value.data.length > 5) {
                    content += `
                        <tr>
                            <td colspan="${value.columns.length}" class="text-center text-muted">
                                <em>... and ${value.data.length - 5} more rows</em>
                            </td>
                        </tr>
                    `;
                }
                
                content += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
        }
        
        return content;
    }
    
    renderCharts(visualizations, data) {
        let content = '';
        
        visualizations.forEach((viz, index) => {
            const chartId = `chart_${Date.now()}_${index}`;
            
            content += `
                <div class="chart-container mt-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="chart-title">${viz.title}</h6>
                        <button class="btn btn-outline-success btn-sm btn-view-chart" 
                                onclick="app.showChartModal('${viz.title}', '${chartId}')">
                            <i class="bi bi-bar-chart"></i> Expand
                        </button>
                    </div>
                    <canvas id="${chartId}" width="400" height="200"></canvas>
                </div>
            `;
        });
        
        return content;
    }
    
    renderCitations(citations) {
        let content = `
            <div class="citations mt-3">
                <h6><i class="bi bi-book me-1"></i> Data Sources & Traceability</h6>
        `;
        
        citations.forEach((citation, index) => {
            content += `
                <div class="citation-item mb-3 p-2 border rounded bg-light">
                    <div class="row">
                        <div class="col-md-8">
                            <strong class="text-primary">${citation.dataset_name}</strong>
                            <br>
                            <small class="text-muted">
                                <strong>Source:</strong> ${citation.source_organization}<br>
                                <strong>Publisher:</strong> ${citation.publisher}<br>
                                <strong>Dataset ID:</strong> ${citation.dataset_id}<br>
                                <strong>Data Quality:</strong> <span class="badge bg-success">${citation.data_quality}</span>
                                <strong>Freshness:</strong> <span class="badge bg-info">${citation.data_freshness}</span>
                            </small>
                        </div>
                        <div class="col-md-4 text-end">
                            <a href="${citation.url}" target="_blank" rel="noopener noreferrer" 
                               class="btn btn-outline-primary btn-sm mb-1">
                                <i class="bi bi-box-arrow-up-right"></i> View on data.gov.in
                            </a>
                            <br>
                            <small class="text-muted">
                                Records: ${citation.records_analyzed}/${citation.total_records_available}<br>
                                Updated: ${citation.update_frequency}<br>
                                License: ${citation.license}
                            </small>
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="bi bi-clock"></i> Accessed: ${citation.accessed_date} at ${citation.accessed_time}
                            ${citation.variables_used && citation.variables_used.length > 0 ? 
                                ` | Variables: ${citation.variables_used.slice(0, 5).join(', ')}${citation.variables_used.length > 5 ? '...' : ''}` : 
                                ''}
                        </small>
                    </div>
                </div>
            `;
        });
        
        content += `</div>`;
        return content;
    }
    
    initializeCharts(messageDiv, visualizations, data) {
        if (!visualizations) return;
        
        visualizations.forEach((viz, index) => {
            const chartId = `chart_${Date.now()}_${index}`;
            const canvas = messageDiv.querySelector(`#${chartId}`);
            
            if (canvas && data[viz.data_key]) {
                this.createChart(canvas, viz, data[viz.data_key]);
            }
        });
    }
    
    createChart(canvas, vizSpec, data) {
        const ctx = canvas.getContext('2d');
        
        // Prepare chart data
        const chartData = this.prepareChartData(vizSpec, data);
        
        // Chart configuration
        const config = {
            type: this.getChartType(vizSpec.type),
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: this.formatColumnName(vizSpec.x_axis)
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: this.formatColumnName(vizSpec.y_axis)
                        }
                    }
                }
            }
        };
        
        // Create chart
        const chart = new Chart(ctx, config);
        this.charts[canvas.id] = chart;
    }
    
    prepareChartData(vizSpec, data) {
        const labels = [];
        const values = [];
        
        if (data.data && Array.isArray(data.data)) {
            data.data.forEach(row => {
                if (row[vizSpec.x_axis] !== undefined && row[vizSpec.y_axis] !== undefined) {
                    labels.push(String(row[vizSpec.x_axis]));
                    values.push(Number(row[vizSpec.y_axis]) || 0);
                }
            });
        }
        
        return {
            labels: labels,
            datasets: [{
                label: this.formatColumnName(vizSpec.y_axis),
                data: values,
                backgroundColor: 'rgba(25, 135, 84, 0.2)',
                borderColor: 'rgba(25, 135, 84, 1)',
                borderWidth: 2,
                fill: vizSpec.type === 'line' ? false : true
            }]
        };
    }
    
    getChartType(type) {
        const typeMap = {
            'line': 'line',
            'bar': 'bar',
            'horizontal_bar': 'bar',
            'pie': 'pie',
            'doughnut': 'doughnut'
        };
        
        return typeMap[type] || 'bar';
    }
    
    // Modal functions
    showDataModal(key, data) {
        const modal = new bootstrap.Modal(document.getElementById('dataModal'));
        const title = document.getElementById('dataModalTitle');
        const content = document.getElementById('modal-content');
        
        title.textContent = `Data: ${this.formatTableTitle(key)}`;
        
        // Create full data table
        let tableHtml = `
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-success">
                        <tr>
        `;
        
        data.columns.forEach(col => {
            tableHtml += `<th>${this.formatColumnName(col)}</th>`;
        });
        
        tableHtml += `
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        data.data.forEach(row => {
            tableHtml += `<tr>`;
            data.columns.forEach(col => {
                const cellValue = row[col];
                tableHtml += `<td>${this.formatCellValue(cellValue)}</td>`;
            });
            tableHtml += `</tr>`;
        });
        
        tableHtml += `
                    </tbody>
                </table>
            </div>
            <div class="mt-3">
                <small class="text-muted">
                    Total records: ${data.data.length} | 
                    Columns: ${data.columns.length}
                </small>
            </div>
        `;
        
        content.innerHTML = tableHtml;
        modal.show();
    }
    
    showChartModal(title, chartId) {
        // Implementation for expanded chart view
        console.log('Show chart modal:', title, chartId);
    }
    
    downloadData() {
        // Implementation for data download
        console.log('Download data');
    }
    
    // Utility functions
    updateStatus(type, message) {
        const indicator = document.getElementById('status-indicator');
        indicator.className = `badge me-2`;
        
        switch (type) {
            case 'ready':
                indicator.classList.add('bg-light', 'text-success');
                break;
            case 'processing':
                indicator.classList.add('status-processing');
                break;
            case 'error':
                indicator.classList.add('status-error');
                break;
        }
        
        indicator.innerHTML = `<i class="bi bi-circle-fill me-1"></i>${message}`;
    }
    
    getConfidenceClass(confidence) {
        if (confidence >= 0.8) return 'confidence-high';
        if (confidence >= 0.6) return 'confidence-medium';
        return 'confidence-low';
    }
    
    getConfidenceIcon(confidence) {
        if (confidence >= 0.8) return 'bi-check-circle-fill';
        if (confidence >= 0.6) return 'bi-exclamation-circle-fill';
        return 'bi-question-circle-fill';
    }
    
    formatTableTitle(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatColumnName(column) {
        return String(column).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatCellValue(value) {
        if (value === null || value === undefined) return '-';
        if (typeof value === 'number') {
            if (value % 1 === 0) return value.toLocaleString();
            return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
        }
        return String(value);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    escapeForJson(str) {
        return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
    }
    
    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }
    
    showError(message) {
        // Simple alert for now, could be enhanced with toast notifications
        alert(message);
    }
}

// Global functions for HTML onclick handlers
function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    // Keep the welcome message
    const welcomeMessage = chatMessages.querySelector('.assistant-message');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    }
    app.updateStatus('ready', 'Ready');
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        app.submitQuery();
    }
}

function submitQuery() {
    app.submitQuery();
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SamarthApp();
});