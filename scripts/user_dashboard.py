#!/usr/bin/env python3
"""
User Dashboard for iLEAPP AI Integration
This module provides a web-based dashboard for tracking analysis progress,
filtering results, and customizing reports.
"""

import os
import sys
import json
import time
import logging
import argparse
import webbrowser
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import threading
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the dashboard"""
    
    def __init__(self, *args, dashboard_data=None, **kwargs):
        self.dashboard_data = dashboard_data
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.dashboard_data).encode())
            return
        
        # Serve dashboard files
        if self.path == '/':
            self.path = '/dashboard.html'
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/update':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # Update dashboard data
            if self.dashboard_data is not None:
                self.dashboard_data.update(data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
            return
        
        self.send_response(404)
        self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class UserDashboard:
    """Web-based dashboard for iLEAPP AI Integration"""
    
    def __init__(self, data_dir=None, port=8080):
        """Initialize the dashboard
        
        Args:
            data_dir (str, optional): Directory containing analysis data
            port (int, optional): Port to run the dashboard server on
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.port = port
        self.dashboard_data = {
            "analyses": [],
            "current_analysis": None,
            "progress": {},
            "filters": {},
            "search_query": "",
            "report_templates": []
        }
        self.server = None
        self.server_thread = None
        
        # Create dashboard directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data if available
        self._load_data()
        
        # Create dashboard files
        self._create_dashboard_files()
    
    def _load_data(self):
        """Load existing dashboard data"""
        data_file = os.path.join(self.data_dir, 'dashboard_data.json')
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.dashboard_data.update(data)
                logger.info(f"Loaded dashboard data from {data_file}")
            except Exception as e:
                logger.error(f"Error loading dashboard data: {str(e)}")
    
    def _save_data(self):
        """Save dashboard data"""
        data_file = os.path.join(self.data_dir, 'dashboard_data.json')
        try:
            with open(data_file, 'w') as f:
                json.dump(self.dashboard_data, f, indent=2)
            logger.info(f"Saved dashboard data to {data_file}")
        except Exception as e:
            logger.error(f"Error saving dashboard data: {str(e)}")
    
    def _create_dashboard_files(self):
        """Create dashboard HTML, CSS, and JavaScript files"""
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create dashboard.html
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iLEAPP AI Integration Dashboard</title>
    <link rel="stylesheet" href="dashboard.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>iLEAPP AI Integration Dashboard</h1>
            <div class="controls">
                <select id="analysis-selector">
                    <option value="">Select Analysis</option>
                </select>
                <button id="new-analysis-btn">New Analysis</button>
            </div>
        </header>
        
        <div class="dashboard-content">
            <div class="sidebar">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="Search...">
                    <button id="search-btn">Search</button>
                </div>
                
                <div class="filter-section">
                    <h3>Filters</h3>
                    <div class="filter-group">
                        <h4>Artifact Types</h4>
                        <div id="artifact-filters"></div>
                    </div>
                    <div class="filter-group">
                        <h4>Date Range</h4>
                        <div class="date-filter">
                            <label>From: <input type="date" id="date-from"></label>
                            <label>To: <input type="date" id="date-to"></label>
                        </div>
                    </div>
                    <div class="filter-group">
                        <h4>Analysis Status</h4>
                        <div id="status-filters"></div>
                    </div>
                    <button id="apply-filters-btn">Apply Filters</button>
                    <button id="reset-filters-btn">Reset Filters</button>
                </div>
                
                <div class="report-section">
                    <h3>Report Templates</h3>
                    <select id="template-selector">
                        <option value="standard">Standard Report</option>
                        <option value="executive">Executive Summary</option>
                        <option value="technical">Technical Details</option>
                        <option value="timeline">Timeline Focus</option>
                        <option value="custom">Custom Template</option>
                    </select>
                    <button id="generate-report-btn">Generate Report</button>
                    <button id="customize-template-btn">Customize Template</button>
                </div>
            </div>
            
            <div class="main-content">
                <div class="progress-section">
                    <h2>Analysis Progress</h2>
                    <div class="progress-container">
                        <div id="progress-bar" class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <div id="progress-status">No analysis in progress</div>
                    </div>
                    <div class="progress-details">
                        <div id="progress-artifacts"></div>
                    </div>
                </div>
                
                <div class="results-section">
                    <h2>Analysis Results</h2>
                    <div class="results-tabs">
                        <button class="tab-btn active" data-tab="overview">Overview</button>
                        <button class="tab-btn" data-tab="messages">Messages</button>
                        <button class="tab-btn" data-tab="app-usage">App Usage</button>
                        <button class="tab-btn" data-tab="browser">Browser History</button>
                        <button class="tab-btn" data-tab="music">Music History</button>
                        <button class="tab-btn" data-tab="timeline">Timeline</button>
                    </div>
                    <div class="tab-content">
                        <div id="overview-tab" class="tab-pane active">
                            <div class="overview-stats">
                                <div class="stat-card">
                                    <h3>Artifacts Analyzed</h3>
                                    <div class="stat-value" id="artifacts-count">0</div>
                                </div>
                                <div class="stat-card">
                                    <h3>Key Insights</h3>
                                    <div class="stat-value" id="insights-count">0</div>
                                </div>
                                <div class="stat-card">
                                    <h3>Analysis Duration</h3>
                                    <div class="stat-value" id="analysis-duration">0:00</div>
                                </div>
                                <div class="stat-card">
                                    <h3>AI Queries</h3>
                                    <div class="stat-value" id="ai-queries-count">0</div>
                                </div>
                            </div>
                            <div class="overview-charts">
                                <div class="chart-container">
                                    <canvas id="artifacts-chart"></canvas>
                                </div>
                                <div class="chart-container">
                                    <canvas id="timeline-chart"></canvas>
                                </div>
                            </div>
                            <div class="key-findings">
                                <h3>Key Findings</h3>
                                <div id="key-findings-list"></div>
                            </div>
                        </div>
                        <div id="messages-tab" class="tab-pane">
                            <div class="artifact-controls">
                                <div class="artifact-search">
                                    <input type="text" placeholder="Search messages...">
                                </div>
                                <div class="artifact-filter">
                                    <select>
                                        <option value="all">All Conversations</option>
                                        <option value="sms">SMS</option>
                                        <option value="imessage">iMessage</option>
                                        <option value="whatsapp">WhatsApp</option>
                                    </select>
                                </div>
                            </div>
                            <div class="artifact-content" id="messages-content"></div>
                        </div>
                        <div id="app-usage-tab" class="tab-pane">
                            <div class="artifact-controls">
                                <div class="artifact-search">
                                    <input type="text" placeholder="Search apps...">
                                </div>
                                <div class="artifact-filter">
                                    <select>
                                        <option value="all">All Apps</option>
                                        <option value="social">Social</option>
                                        <option value="productivity">Productivity</option>
                                        <option value="entertainment">Entertainment</option>
                                    </select>
                                </div>
                            </div>
                            <div class="artifact-content" id="app-usage-content"></div>
                        </div>
                        <div id="browser-tab" class="tab-pane">
                            <div class="artifact-controls">
                                <div class="artifact-search">
                                    <input type="text" placeholder="Search browser history...">
                                </div>
                                <div class="artifact-filter">
                                    <select>
                                        <option value="all">All History</option>
                                        <option value="safari">Safari</option>
                                        <option value="chrome">Chrome</option>
                                        <option value="firefox">Firefox</option>
                                    </select>
                                </div>
                            </div>
                            <div class="artifact-content" id="browser-content"></div>
                        </div>
                        <div id="music-tab" class="tab-pane">
                            <div class="artifact-controls">
                                <div class="artifact-search">
                                    <input type="text" placeholder="Search music history...">
                                </div>
                                <div class="artifact-filter">
                                    <select>
                                        <option value="all">All Music</option>
                                        <option value="recent">Recently Played</option>
                                        <option value="most-played">Most Played</option>
                                        <option value="playlists">Playlists</option>
                                    </select>
                                </div>
                            </div>
                            <div class="artifact-content" id="music-content"></div>
                        </div>
                        <div id="timeline-tab" class="tab-pane">
                            <div class="artifact-controls">
                                <div class="artifact-search">
                                    <input type="text" placeholder="Search timeline...">
                                </div>
                                <div class="artifact-filter">
                                    <select>
                                        <option value="all">All Events</option>
                                        <option value="messages">Messages</option>
                                        <option value="app-usage">App Usage</option>
                                        <option value="browser">Browser</option>
                                        <option value="music">Music</option>
                                    </select>
                                </div>
                            </div>
                            <div class="artifact-content" id="timeline-content"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal for New Analysis -->
    <div id="new-analysis-modal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>New Analysis</h2>
            <form id="new-analysis-form">
                <div class="form-group">
                    <label for="analysis-name">Analysis Name:</label>
                    <input type="text" id="analysis-name" required>
                </div>
                <div class="form-group">
                    <label for="input-path">Input Path:</label>
                    <input type="text" id="input-path" required>
                    <button type="button" id="browse-input-btn">Browse</button>
                </div>
                <div class="form-group">
                    <label for="output-path">Output Path:</label>
                    <input type="text" id="output-path" required>
                    <button type="button" id="browse-output-btn">Browse</button>
                </div>
                <div class="form-group">
                    <label>Artifact Types:</label>
                    <div class="checkbox-group" id="artifact-types-checkboxes">
                        <label><input type="checkbox" name="artifact-type" value="messages" checked> Messages</label>
                        <label><input type="checkbox" name="artifact-type" value="app_usage" checked> App Usage</label>
                        <label><input type="checkbox" name="artifact-type" value="chrome_history" checked> Chrome History</label>
                        <label><input type="checkbox" name="artifact-type" value="itunes_music" checked> iTunes Music</label>
                        <label><input type="checkbox" name="artifact-type" value="location" checked> Location</label>
                        <label><input type="checkbox" name="artifact-type" value="photos" checked> Photos</label>
                        <label><input type="checkbox" name="artifact-type" value="notes" checked> Notes</label>
                        <label><input type="checkbox" name="artifact-type" value="calendar" checked> Calendar</label>
                    </div>
                </div>
                <div class="form-group">
                    <label for="ai-provider">AI Provider:</label>
                    <select id="ai-provider">
                        <option value="openrouter">OpenRouter</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="local">Local LLM</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="ai-model">AI Model:</label>
                    <select id="ai-model">
                        <option value="anthropic/claude-3-opus">Claude 3 Opus</option>
                        <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
                        <option value="openai/gpt-4o">GPT-4o</option>
                        <option value="openai/gpt-4-turbo">GPT-4 Turbo</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="analysis-depth">Analysis Depth:</label>
                    <select id="analysis-depth">
                        <option value="basic">Basic</option>
                        <option value="standard" selected>Standard</option>
                        <option value="comprehensive">Comprehensive</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="submit">Start Analysis</button>
                    <button type="button" id="cancel-analysis-btn">Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Modal for Template Customization -->
    <div id="template-modal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Customize Report Template</h2>
            <form id="template-form">
                <div class="form-group">
                    <label for="template-name">Template Name:</label>
                    <input type="text" id="template-name" required>
                </div>
                <div class="form-group">
                    <label>Sections to Include:</label>
                    <div class="checkbox-group" id="template-sections-checkboxes">
                        <label><input type="checkbox" name="template-section" value="executive_summary" checked> Executive Summary</label>
                        <label><input type="checkbox" name="template-section" value="key_findings" checked> Key Findings</label>
                        <label><input type="checkbox" name="template-section" value="messages_analysis" checked> Messages Analysis</label>
                        <label><input type="checkbox" name="template-section" value="app_usage_analysis" checked> App Usage Analysis</label>
                        <label><input type="checkbox" name="template-section" value="browser_analysis" checked> Browser History Analysis</label>
                        <label><input type="checkbox" name="template-section" value="music_analysis" checked> Music History Analysis</label>
                        <label><input type="checkbox" name="template-section" value="timeline" checked> Timeline</label>
                        <label><input type="checkbox" name="template-section" value="technical_details" checked> Technical Details</label>
                        <label><input type="checkbox" name="template-section" value="appendices" checked> Appendices</label>
                    </div>
                </div>
                <div class="form-group">
                    <label for="template-style">Report Style:</label>
                    <select id="template-style">
                        <option value="professional">Professional</option>
                        <option value="technical">Technical</option>
                        <option value="executive">Executive</option>
                        <option value="forensic">Forensic</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="template-format">Output Format:</label>
                    <select id="template-format">
                        <option value="html">HTML</option>
                        <option value="pdf">PDF</option>
                        <option value="docx">DOCX</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Visualization Options:</label>
                    <div class="checkbox-group" id="template-visualizations-checkboxes">
                        <label><input type="checkbox" name="template-viz" value="charts" checked> Charts and Graphs</label>
                        <label><input type="checkbox" name="template-viz" value="timeline" checked> Interactive Timeline</label>
                        <label><input type="checkbox" name="template-viz" value="network" checked> Network Diagrams</label>
                        <label><input type="checkbox" name="template-viz" value="heatmaps" checked> Heatmaps</label>
                        <label><input type="checkbox" name="template-viz" value="wordclouds" checked> Word Clouds</label>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit">Save Template</button>
                    <button type="button" id="cancel-template-btn">Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <script src="dashboard.js"></script>
</body>
</html>
"""
        
        # Create dashboard.css
        css_content = """/* Dashboard Styles */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --background-color: #f5f7fa;
    --card-background: #ffffff;
    --text-color: #333333;
    --border-color: #dddddd;
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

.dashboard {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 {
    font-size: 1.5rem;
    font-weight: 500;
}

.controls {
    display: flex;
    gap: 1rem;
}

#analysis-selector {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid var(--border-color);
    min-width: 200px;
}

button {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #2980b9;
}

.dashboard-content {
    display: flex;
    flex: 1;
}

.sidebar {
    width: 300px;
    background-color: var(--card-background);
    border-right: 1px solid var(--border-color);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.search-box {
    display: flex;
    gap: 0.5rem;
}

.search-box input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.filter-section, .report-section {
    border-top: 1px solid var(--border-color);
    padding-top: 1rem;
}

.filter-section h3, .report-section h3 {
    margin-bottom: 1rem;
    font-size: 1.1rem;
    color: var(--primary-color);
}

.filter-group {
    margin-bottom: 1rem;
}

.filter-group h4 {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-color);
}

.date-filter {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.date-filter label {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.date-filter input {
    padding: 0.3rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

#template-selector {
    width: 100%;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.main-content {
    flex: 1;
    padding: 1rem 2rem;
    overflow-y: auto;
}

.progress-section {
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.progress-section h2 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.progress-container {
    margin-bottom: 1rem;
}

.progress-bar {
    height: 20px;
    background-color: #ecf0f1;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.progress-fill {
    height: 100%;
    background-color: var(--secondary-color);
    width: 0%;
    transition: width 0.3s ease;
}

#progress-status {
    font-size: 0.9rem;
    color: var(--text-color);
}

.progress-details {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}

.results-section {
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.results-section h2 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.results-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
}

.tab-btn {
    background-color: transparent;
    color: var(--text-color);
    padding: 0.5rem 1rem;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
}

.tab-btn.active {
    color: var(--secondary-color);
    border-bottom: 3px solid var(--secondary-color);
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
}

.overview-stats {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background-color: var(--background-color);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.stat-card h3 {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    color: var(--text-color);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: var(--secondary-color);
}

.overview-charts {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.chart-container {
    height: 300px;
}

.key-findings {
    background-color: var(--background-color);
    border-radius: 8px;
    padding: 1rem;
}

.key-findings h3 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.artifact-controls {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.artifact-search {
    flex: 1;
    margin-right: 1rem;
}

.artifact-search input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.artifact-filter select {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    min-width: 150px;
}

.artifact-content {
    background-color: var(--background-color);
    border-radius: 8px;
    padding: 1rem;
    min-height: 400px;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: var(--card-background);
    margin: 5% auto;
    padding: 2rem;
    border-radius: 8px;
    width: 80%;
    max-width: 700px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    position: relative;
}

.close {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    font-size: 1.5rem;
    cursor: pointer;
}

.modal h2 {
    margin-bottom: 1.5rem;
    color: var(--primary-color);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-group input[type="text"],
.form-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.5rem;
}

.checkbox-group label {
    display: flex;
    align-items: center;
    font-weight: normal;
}

.checkbox-group input[type="checkbox"] {
    margin-right: 0.5rem;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
}

#cancel-analysis-btn, #cancel-template-btn {
    background-color: #95a5a6;
}

#browse-input-btn, #browse-output-btn {
    margin-left: 0.5rem;
}

/* Responsive Styles */
@media (max-width: 1024px) {
    .dashboard-content {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border-color);
    }
    
    .overview-charts {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .controls {
        width: 100%;
    }
    
    #analysis-selector {
        flex: 1;
    }
    
    .overview-stats {
        grid-template-columns: 1fr 1fr;
    }
    
    .modal-content {
        width: 95%;
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .overview-stats {
        grid-template-columns: 1fr;
    }
    
    .checkbox-group {
        grid-template-columns: 1fr;
    }
}
"""
        
        # Create dashboard.js
        js_content = """// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadDashboardData();
});

// Global variables
let dashboardData = {
    analyses: [],
    current_analysis: null,
    progress: {},
    filters: {},
    search_query: "",
    report_templates: []
};

// Initialize dashboard
function initDashboard() {
    // Initialize charts
    initCharts();
    
    // Set up tabs
    setupTabs();
}

// Set up event listeners
function setupEventListeners() {
    // New analysis button
    document.getElementById('new-analysis-btn').addEventListener('click', function() {
        document.getElementById('new-analysis-modal').style.display = 'block';
    });
    
    // Close modal buttons
    document.querySelectorAll('.close').forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function() {
            document.getElementById('new-analysis-modal').style.display = 'none';
            document.getElementById('template-modal').style.display = 'none';
        });
    });
    
    // Cancel buttons
    document.getElementById('cancel-analysis-btn').addEventListener('click', function() {
        document.getElementById('new-analysis-modal').style.display = 'none';
    });
    
    document.getElementById('cancel-template-btn').addEventListener('click', function() {
        document.getElementById('template-modal').style.display = 'none';
    });
    
    // New analysis form submission
    document.getElementById('new-analysis-form').addEventListener('submit', function(e) {
        e.preventDefault();
        startNewAnalysis();
    });
    
    // Customize template button
    document.getElementById('customize-template-btn').addEventListener('click', function() {
        document.getElementById('template-modal').style.display = 'block';
    });
    
    // Template form submission
    document.getElementById('template-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveReportTemplate();
    });
    
    // Analysis selector
    document.getElementById('analysis-selector').addEventListener('change', function() {
        const analysisId = this.value;
        if (analysisId) {
            loadAnalysis(analysisId);
        }
    });
    
    // Search button
    document.getElementById('search-btn').addEventListener('click', function() {
        const searchQuery = document.getElementById('search-input').value;
        searchResults(searchQuery);
    });
    
    // Apply filters button
    document.getElementById('apply-filters-btn').addEventListener('click', function() {
        applyFilters();
    });
    
    // Reset filters button
    document.getElementById('reset-filters-btn').addEventListener('click', function() {
        resetFilters();
    });
    
    // Generate report button
    document.getElementById('generate-report-btn').addEventListener('click', function() {
        generateReport();
    });
}

// Load dashboard data from API
function loadDashboardData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            dashboardData = data;
            updateDashboard();
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
        });
}

// Update dashboard with current data
function updateDashboard() {
    // Update analysis selector
    updateAnalysisSelector();
    
    // Update progress if there's a current analysis
    if (dashboardData.current_analysis) {
        updateProgress();
    }
    
    // Update filters
    updateFilters();
    
    // Update report templates
    updateReportTemplates();
    
    // Update results if there's a current analysis
    if (dashboardData.current_analysis) {
        updateResults();
    }
}

// Update analysis selector with available analyses
function updateAnalysisSelector() {
    const selector = document.getElementById('analysis-selector');
    
    // Clear existing options except the first one
    while (selector.options.length > 1) {
        selector.remove(1);
    }
    
    // Add options for each analysis
    dashboardData.analyses.forEach(analysis => {
        const option = document.createElement('option');
        option.value = analysis.id;
        option.textContent = analysis.name;
        
        if (dashboardData.current_analysis && analysis.id === dashboardData.current_analysis.id) {
            option.selected = true;
        }
        
        selector.appendChild(option);
    });
}

// Update progress display
function updateProgress() {
    const progress = dashboardData.progress;
    
    // Update progress bar
    const progressFill = document.querySelector('.progress-fill');
    progressFill.style.width = `${progress.percentage || 0}%`;
    
    // Update progress status
    const progressStatus = document.getElementById('progress-status');
    progressStatus.textContent = progress.status || 'No analysis in progress';
    
    // Update progress details
    const progressArtifacts = document.getElementById('progress-artifacts');
    progressArtifacts.innerHTML = '';
    
    if (progress.artifacts) {
        Object.entries(progress.artifacts).forEach(([artifact, status]) => {
            const artifactDiv = document.createElement('div');
            artifactDiv.className = 'artifact-progress';
            
            const statusClass = status === 'completed' ? 'success' : 
                               status === 'in_progress' ? 'warning' : 
                               status === 'error' ? 'danger' : '';
            
            artifactDiv.innerHTML = `
                <span class="artifact-name">${artifact}</span>
                <span class="artifact-status ${statusClass}">${status}</span>
            `;
            
            progressArtifacts.appendChild(artifactDiv);
        });
    }
}

// Update filters display
function updateFilters() {
    // Update artifact filters
    const artifactFilters = document.getElementById('artifact-filters');
    artifactFilters.innerHTML = '';
    
    const artifactTypes = [
        { id: 'messages', name: 'Messages' },
        { id: 'app_usage', name: 'App Usage' },
        { id: 'chrome_history', name: 'Chrome History' },
        { id: 'itunes_music', name: 'iTunes Music' },
        { id: 'location', name: 'Location' },
        { id: 'photos', name: 'Photos' },
        { id: 'notes', name: 'Notes' },
        { id: 'calendar', name: 'Calendar' }
    ];
    
    artifactTypes.forEach(type => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = type.id;
        checkbox.checked = !dashboardData.filters.artifacts || 
                          !dashboardData.filters.artifacts.length || 
                          dashboardData.filters.artifacts.includes(type.id);
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` ${type.name}`));
        
        artifactFilters.appendChild(label);
    });
    
    // Update status filters
    const statusFilters = document.getElementById('status-filters');
    statusFilters.innerHTML = '';
    
    const statusTypes = [
        { id: 'completed', name: 'Completed' },
        { id: 'in_progress', name: 'In Progress' },
        { id: 'pending', name: 'Pending' },
        { id: 'error', name: 'Error' }
    ];
    
    statusTypes.forEach(type => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = type.id;
        checkbox.checked = !dashboardData.filters.status || 
                          !dashboardData.filters.status.length || 
                          dashboardData.filters.status.includes(type.id);
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` ${type.name}`));
        
        statusFilters.appendChild(label);
    });
    
    // Update date filters
    if (dashboardData.filters.date_from) {
        document.getElementById('date-from').value = dashboardData.filters.date_from;
    }
    
    if (dashboardData.filters.date_to) {
        document.getElementById('date-to').value = dashboardData.filters.date_to;
    }
}

// Update report templates
function updateReportTemplates() {
    const selector = document.getElementById('template-selector');
    
    // Add custom templates
    dashboardData.report_templates.forEach(template => {
        // Check if the template option already exists
        let exists = false;
        for (let i = 0; i < selector.options.length; i++) {
            if (selector.options[i].value === template.id) {
                exists = true;
                break;
            }
        }
        
        if (!exists) {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            selector.appendChild(option);
        }
    });
}

// Update results display
function updateResults() {
    const analysis = dashboardData.current_analysis;
    
    if (!analysis) return;
    
    // Update overview stats
    document.getElementById('artifacts-count').textContent = analysis.artifacts_count || 0;
    document.getElementById('insights-count').textContent = analysis.insights_count || 0;
    document.getElementById('analysis-duration').textContent = analysis.duration || '0:00';
    document.getElementById('ai-queries-count').textContent = analysis.ai_queries_count || 0;
    
    // Update key findings
    const keyFindingsList = document.getElementById('key-findings-list');
    keyFindingsList.innerHTML = '';
    
    if (analysis.key_findings && analysis.key_findings.length) {
        analysis.key_findings.forEach(finding => {
            const findingDiv = document.createElement('div');
            findingDiv.className = 'finding-item';
            findingDiv.innerHTML = `
                <h4>${finding.title}</h4>
                <p>${finding.description}</p>
            `;
            keyFindingsList.appendChild(findingDiv);
        });
    } else {
        keyFindingsList.innerHTML = '<p>No key findings available.</p>';
    }
    
    // Update artifact tabs
    updateArtifactTab('messages', analysis.messages);
    updateArtifactTab('app-usage', analysis.app_usage);
    updateArtifactTab('browser', analysis.browser_history);
    updateArtifactTab('music', analysis.music_history);
    updateArtifactTab('timeline', analysis.timeline);
    
    // Update charts
    updateCharts(analysis);
}

// Update specific artifact tab
function updateArtifactTab(tabId, data) {
    const contentDiv = document.getElementById(`${tabId}-content`);
    
    if (!data || !data.length) {
        contentDiv.innerHTML = '<p>No data available.</p>';
        return;
    }
    
    contentDiv.innerHTML = '';
    
    // Create content based on tab type
    switch (tabId) {
        case 'messages':
            createMessagesContent(contentDiv, data);
            break;
        case 'app-usage':
            createAppUsageContent(contentDiv, data);
            break;
        case 'browser':
            createBrowserContent(contentDiv, data);
            break;
        case 'music':
            createMusicContent(contentDiv, data);
            break;
        case 'timeline':
            createTimelineContent(contentDiv, data);
            break;
    }
}

// Create messages content
function createMessagesContent(container, data) {
    const messagesDiv = document.createElement('div');
    messagesDiv.className = 'messages-container';
    
    data.forEach(conversation => {
        const conversationDiv = document.createElement('div');
        conversationDiv.className = 'conversation-card';
        
        conversationDiv.innerHTML = `
            <div class="conversation-header">
                <h3>${conversation.participants.join(', ')}</h3>
                <span class="message-count">${conversation.messages.length} messages</span>
            </div>
            <div class="conversation-summary">
                <p>${conversation.summary}</p>
            </div>
            <div class="conversation-insights">
                <div class="insight-item">
                    <span class="insight-label">Sentiment:</span>
                    <span class="insight-value">${conversation.sentiment}</span>
                </div>
                <div class="insight-item">
                    <span class="insight-label">Topics:</span>
                    <span class="insight-value">${conversation.topics.join(', ')}</span>
                </div>
            </div>
            <button class="view-details-btn" data-id="${conversation.id}">View Details</button>
        `;
        
        messagesDiv.appendChild(conversationDiv);
    });
    
    container.appendChild(messagesDiv);
    
    // Add event listeners to view details buttons
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const conversationId = this.getAttribute('data-id');
            viewConversationDetails(conversationId);
        });
    });
}

// Create app usage content
function createAppUsageContent(container, data) {
    const appsDiv = document.createElement('div');
    appsDiv.className = 'apps-container';
    
    data.forEach(app => {
        const appDiv = document.createElement('div');
        appDiv.className = 'app-card';
        
        appDiv.innerHTML = `
            <div class="app-header">
                <h3>${app.name}</h3>
                <span class="app-category">${app.category}</span>
            </div>
            <div class="app-stats">
                <div class="stat-item">
                    <span class="stat-label">Total Usage:</span>
                    <span class="stat-value">${app.total_usage}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Last Used:</span>
                    <span class="stat-value">${app.last_used}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Usage Pattern:</span>
                    <span class="stat-value">${app.usage_pattern}</span>
                </div>
            </div>
            <div class="app-insights">
                <p>${app.insights}</p>
            </div>
            <button class="view-details-btn" data-id="${app.id}">View Details</button>
        `;
        
        appsDiv.appendChild(appDiv);
    });
    
    container.appendChild(appsDiv);
    
    // Add event listeners to view details buttons
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const appId = this.getAttribute('data-id');
            viewAppDetails(appId);
        });
    });
}

// Create browser content
function createBrowserContent(container, data) {
    const browserDiv = document.createElement('div');
    browserDiv.className = 'browser-container';
    
    // Group by domain
    const domainGroups = {};
    data.forEach(visit => {
        const domain = new URL(visit.url).hostname;
        if (!domainGroups[domain]) {
            domainGroups[domain] = [];
        }
        domainGroups[domain].push(visit);
    });
    
    // Create domain cards
    Object.entries(domainGroups).forEach(([domain, visits]) => {
        const domainDiv = document.createElement('div');
        domainDiv.className = 'domain-card';
        
        const categories = [...new Set(visits.map(v => v.category))].join(', ');
        
        domainDiv.innerHTML = `
            <div class="domain-header">
                <h3>${domain}</h3>
                <span class="visit-count">${visits.length} visits</span>
            </div>
            <div class="domain-stats">
                <div class="stat-item">
                    <span class="stat-label">Categories:</span>
                    <span class="stat-value">${categories}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Last Visit:</span>
                    <span class="stat-value">${visits[0].timestamp}</span>
                </div>
            </div>
            <div class="domain-insights">
                <p>${visits[0].insights || 'No insights available.'}</p>
            </div>
            <button class="view-details-btn" data-domain="${domain}">View Details</button>
        `;
        
        browserDiv.appendChild(domainDiv);
    });
    
    container.appendChild(browserDiv);
    
    // Add event listeners to view details buttons
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const domain = this.getAttribute('data-domain');
            viewDomainDetails(domain);
        });
    });
}

// Create music content
function createMusicContent(container, data) {
    const musicDiv = document.createElement('div');
    musicDiv.className = 'music-container';
    
    // Group by artist
    const artistGroups = {};
    data.forEach(track => {
        if (!artistGroups[track.artist]) {
            artistGroups[track.artist] = [];
        }
        artistGroups[track.artist].push(track);
    });
    
    // Create artist cards
    Object.entries(artistGroups).forEach(([artist, tracks]) => {
        const artistDiv = document.createElement('div');
        artistDiv.className = 'artist-card';
        
        const genres = [...new Set(tracks.map(t => t.genre))].join(', ');
        
        artistDiv.innerHTML = `
            <div class="artist-header">
                <h3>${artist}</h3>
                <span class="track-count">${tracks.length} tracks</span>
            </div>
            <div class="artist-stats">
                <div class="stat-item">
                    <span class="stat-label">Genres:</span>
                    <span class="stat-value">${genres}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Most Played:</span>
                    <span class="stat-value">${tracks[0].title}</span>
                </div>
            </div>
            <div class="artist-insights">
                <p>${tracks[0].insights || 'No insights available.'}</p>
            </div>
            <button class="view-details-btn" data-artist="${artist}">View Details</button>
        `;
        
        musicDiv.appendChild(artistDiv);
    });
    
    container.appendChild(musicDiv);
    
    // Add event listeners to view details buttons
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const artist = this.getAttribute('data-artist');
            viewArtistDetails(artist);
        });
    });
}

// Create timeline content
function createTimelineContent(container, data) {
    const timelineDiv = document.createElement('div');
    timelineDiv.className = 'timeline-container';
    
    // Sort events by timestamp
    data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Group events by date
    const dateGroups = {};
    data.forEach(event => {
        const date = new Date(event.timestamp).toLocaleDateString();
        if (!dateGroups[date]) {
            dateGroups[date] = [];
        }
        dateGroups[date].push(event);
    });
    
    // Create timeline
    Object.entries(dateGroups).forEach(([date, events]) => {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'timeline-date';
        
        dateDiv.innerHTML = `<h3>${date}</h3>`;
        
        const eventsDiv = document.createElement('div');
        eventsDiv.className = 'timeline-events';
        
        events.forEach(event => {
            const eventDiv = document.createElement('div');
            eventDiv.className = `timeline-event ${event.type}`;
            
            const time = new Date(event.timestamp).toLocaleTimeString();
            
            eventDiv.innerHTML = `
                <div class="event-time">${time}</div>
                <div class="event-content">
                    <div class="event-type">${event.type}</div>
                    <div class="event-title">${event.title}</div>
                    <div class="event-description">${event.description}</div>
                </div>
            `;
            
            eventsDiv.appendChild(eventDiv);
        });
        
        dateDiv.appendChild(eventsDiv);
        timelineDiv.appendChild(dateDiv);
    });
    
    container.appendChild(timelineDiv);
}

// Initialize charts
function initCharts() {
    // Artifacts chart
    const artifactsCtx = document.getElementById('artifacts-chart').getContext('2d');
    window.artifactsChart = new Chart(artifactsCtx, {
        type: 'bar',
        data: {
            labels: ['Messages', 'App Usage', 'Browser', 'Music', 'Location', 'Photos'],
            datasets: [{
                label: 'Artifacts Count',
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#e74c3c',
                    '#f39c12',
                    '#9b59b6',
                    '#1abc9c'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Artifacts Distribution'
                }
            }
        }
    });
    
    // Timeline chart
    const timelineCtx = document.getElementById('timeline-chart').getContext('2d');
    window.timelineChart = new Chart(timelineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Messages',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'App Usage',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Browser',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Music',
                    data: [],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Activity Timeline'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Activity Count'
                    }
                }
            }
        }
    });
}

// Update charts with analysis data
function updateCharts(analysis) {
    // Update artifacts chart
    if (window.artifactsChart) {
        window.artifactsChart.data.datasets[0].data = [
            analysis.messages ? analysis.messages.length : 0,
            analysis.app_usage ? analysis.app_usage.length : 0,
            analysis.browser_history ? analysis.browser_history.length : 0,
            analysis.music_history ? analysis.music_history.length : 0,
            analysis.location ? analysis.location.length : 0,
            analysis.photos ? analysis.photos.length : 0
        ];
        window.artifactsChart.update();
    }
    
    // Update timeline chart
    if (window.timelineChart && analysis.timeline_data) {
        window.timelineChart.data.labels = analysis.timeline_data.labels || [];
        
        if (analysis.timeline_data.datasets) {
            analysis.timeline_data.datasets.forEach((dataset, index) => {
                if (index < window.timelineChart.data.datasets.length) {
                    window.timelineChart.data.datasets[index].data = dataset.data || [];
                }
            });
        }
        
        window.timelineChart.update();
    }
}

// Set up tabs
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and panes
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

// Start a new analysis
function startNewAnalysis() {
    const name = document.getElementById('analysis-name').value;
    const inputPath = document.getElementById('input-path').value;
    const outputPath = document.getElementById('output-path').value;
    const provider = document.getElementById('ai-provider').value;
    const model = document.getElementById('ai-model').value;
    const depth = document.getElementById('analysis-depth').value;
    
    // Get selected artifact types
    const artifactTypes = [];
    document.querySelectorAll('input[name="artifact-type"]:checked').forEach(checkbox => {
        artifactTypes.push(checkbox.value);
    });
    
    // Create analysis object
    const analysis = {
        id: Date.now().toString(),
        name: name,
        input_path: inputPath,
        output_path: outputPath,
        provider: provider,
        model: model,
        depth: depth,
        artifact_types: artifactTypes,
        start_time: new Date().toISOString(),
        status: 'in_progress'
    };
    
    // Add to analyses list
    dashboardData.analyses.push(analysis);
    
    // Set as current analysis
    dashboardData.current_analysis = analysis;
    
    // Initialize progress
    dashboardData.progress = {
        percentage: 0,
        status: 'Starting analysis...',
        artifacts: {}
    };
    
    // Save data
    saveData();
    
    // Update dashboard
    updateDashboard();
    
    // Close modal
    document.getElementById('new-analysis-modal').style.display = 'none';
    
    // Simulate analysis progress (for demo purposes)
    simulateAnalysisProgress();
}

// Save a report template
function saveReportTemplate() {
    const name = document.getElementById('template-name').value;
    const style = document.getElementById('template-style').value;
    const format = document.getElementById('template-format').value;
    
    // Get selected sections
    const sections = [];
    document.querySelectorAll('input[name="template-section"]:checked').forEach(checkbox => {
        sections.push(checkbox.value);
    });
    
    // Get selected visualizations
    const visualizations = [];
    document.querySelectorAll('input[name="template-viz"]:checked').forEach(checkbox => {
        visualizations.push(checkbox.value);
    });
    
    // Create template object
    const template = {
        id: Date.now().toString(),
        name: name,
        style: style,
        format: format,
        sections: sections,
        visualizations: visualizations
    };
    
    // Add to templates list
    dashboardData.report_templates.push(template);
    
    // Save data
    saveData();
    
    // Update dashboard
    updateReportTemplates();
    
    // Close modal
    document.getElementById('template-modal').style.display = 'none';
}

// Load an analysis
function loadAnalysis(analysisId) {
    const analysis = dashboardData.analyses.find(a => a.id === analysisId);
    
    if (analysis) {
        dashboardData.current_analysis = analysis;
        updateDashboard();
    }
}

// Search results
function searchResults(query) {
    dashboardData.search_query = query;
    
    // In a real implementation, this would filter the results based on the query
    // For demo purposes, we'll just update the dashboard
    updateDashboard();
}

// Apply filters
function applyFilters() {
    // Get artifact filters
    const artifactFilters = [];
    document.querySelectorAll('#artifact-filters input:checked').forEach(checkbox => {
        artifactFilters.push(checkbox.value);
    });
    
    // Get status filters
    const statusFilters = [];
    document.querySelectorAll('#status-filters input:checked').forEach(checkbox => {
        statusFilters.push(checkbox.value);
    });
    
    // Get date filters
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    // Update filters
    dashboardData.filters = {
        artifacts: artifactFilters,
        status: statusFilters,
        date_from: dateFrom,
        date_to: dateTo
    };
    
    // Save data
    saveData();
    
    // Update dashboard
    updateDashboard();
}

// Reset filters
function resetFilters() {
    // Clear filters
    dashboardData.filters = {};
    
    // Reset form elements
    document.querySelectorAll('#artifact-filters input').forEach(checkbox => {
        checkbox.checked = true;
    });
    
    document.querySelectorAll('#status-filters input').forEach(checkbox => {
        checkbox.checked = true;
    });
    
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    
    // Save data
    saveData();
    
    // Update dashboard
    updateDashboard();
}

// Generate report
function generateReport() {
    const templateId = document.getElementById('template-selector').value;
    
    // In a real implementation, this would generate a report based on the selected template
    // For demo purposes, we'll just show an alert
    alert(`Generating report with template: ${templateId}`);
}

// View conversation details
function viewConversationDetails(conversationId) {
    // In a real implementation, this would show detailed conversation data
    // For demo purposes, we'll just show an alert
    alert(`Viewing conversation details: ${conversationId}`);
}

// View app details
function viewAppDetails(appId) {
    // In a real implementation, this would show detailed app usage data
    // For demo purposes, we'll just show an alert
    alert(`Viewing app details: ${appId}`);
}

// View domain details
function viewDomainDetails(domain) {
    // In a real implementation, this would show detailed domain visit data
    // For demo purposes, we'll just show an alert
    alert(`Viewing domain details: ${domain}`);
}

// View artist details
function viewArtistDetails(artist) {
    // In a real implementation, this would show detailed artist track data
    // For demo purposes, we'll just show an alert
    alert(`Viewing artist details: ${artist}`);
}

// Save dashboard data to API
function saveData() {
    fetch('/api/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dashboardData)
    })
    .catch(error => {
        console.error('Error saving dashboard data:', error);
    });
}

// Simulate analysis progress (for demo purposes)
function simulateAnalysisProgress() {
    const artifacts = [
        'messages',
        'app_usage',
        'chrome_history',
        'itunes_music',
        'location',
        'photos'
    ];
    
    let currentArtifact = 0;
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += 5;
        
        if (progress >= 100) {
            progress = 0;
            currentArtifact++;
            
            if (currentArtifact >= artifacts.length) {
                clearInterval(interval);
                completeAnalysis();
                return;
            }
        }
        
        // Update progress
        dashboardData.progress.percentage = Math.round((currentArtifact * 100 + progress) / artifacts.length);
        dashboardData.progress.status = `Analyzing ${artifacts[currentArtifact]}...`;
        
        // Update artifact status
        dashboardData.progress.artifacts = {};
        for (let i = 0; i < artifacts.length; i++) {
            if (i < currentArtifact) {
                dashboardData.progress.artifacts[artifacts[i]] = 'completed';
            } else if (i === currentArtifact) {
                dashboardData.progress.artifacts[artifacts[i]] = 'in_progress';
            } else {
                dashboardData.progress.artifacts[artifacts[i]] = 'pending';
            }
        }
        
        // Save data
        saveData();
        
        // Update dashboard
        updateProgress();
    }, 200);
}

// Complete analysis (for demo purposes)
function completeAnalysis() {
    // Update analysis status
    dashboardData.current_analysis.status = 'completed';
    dashboardData.current_analysis.end_time = new Date().toISOString();
    
    // Calculate duration
    const startTime = new Date(dashboardData.current_analysis.start_time);
    const endTime = new Date(dashboardData.current_analysis.end_time);
    const durationMs = endTime - startTime;
    const durationMin = Math.floor(durationMs / 60000);
    const durationSec = Math.floor((durationMs % 60000) / 1000);
    dashboardData.current_analysis.duration = `${durationMin}:${durationSec.toString().padStart(2, '0')}`;
    
    // Update progress
    dashboardData.progress.percentage = 100;
    dashboardData.progress.status = 'Analysis completed';
    
    // Generate sample results (for demo purposes)
    generateSampleResults();
    
    // Save data
    saveData();
    
    // Update dashboard
    updateDashboard();
}

// Generate sample results (for demo purposes)
function generateSampleResults() {
    // Sample messages
    dashboardData.current_analysis.messages = [
        {
            id: '1',
            participants: ['John Doe', 'Jane Smith'],
            summary: 'Discussion about weekend plans and dinner arrangements.',
            sentiment: 'Positive',
            topics: ['Weekend', 'Dinner', 'Plans'],
            messages: [
                { sender: 'John Doe', content: 'Hey, what are your plans this weekend?', timestamp: '2025-04-01T10:15:00Z' },
                { sender: 'Jane Smith', content: 'Not much, thinking of trying that new restaurant downtown.', timestamp: '2025-04-01T10:17:00Z' },
                { sender: 'John Doe', content: 'Sounds great! Want to go together?', timestamp: '2025-04-01T10:18:00Z' },
                { sender: 'Jane Smith', content: 'Sure! How about Saturday at 7?', timestamp: '2025-04-01T10:20:00Z' },
                { sender: 'John Doe', content: 'Perfect, see you then!', timestamp: '2025-04-01T10:21:00Z' }
            ]
        },
        {
            id: '2',
            participants: ['John Doe', 'Bob Johnson'],
            summary: 'Work-related discussion about project deadlines and meeting schedule.',
            sentiment: 'Neutral',
            topics: ['Work', 'Project', 'Deadlines'],
            messages: [
                { sender: 'Bob Johnson', content: 'Hi John, do you have the latest project timeline?', timestamp: '2025-04-02T09:05:00Z' },
                { sender: 'John Doe', content: 'Yes, I\'ll send it over in a few minutes.', timestamp: '2025-04-02T09:10:00Z' },
                { sender: 'Bob Johnson', content: 'Thanks. Also, can we move tomorrow\'s meeting to 3pm?', timestamp: '2025-04-02T09:12:00Z' },
                { sender: 'John Doe', content: 'That works for me. I\'ll update the calendar invite.', timestamp: '2025-04-02T09:15:00Z' },
                { sender: 'Bob Johnson', content: 'Great, thanks!', timestamp: '2025-04-02T09:16:00Z' }
            ]
        }
    ];
    
    // Sample app usage
    dashboardData.current_analysis.app_usage = [
        {
            id: '1',
            name: 'Messages',
            category: 'Communication',
            total_usage: '2h 15m',
            last_used: '2025-04-03 15:45',
            usage_pattern: 'Daily, primarily mornings and evenings',
            insights: 'Heavy usage for personal communication, with consistent daily patterns.'
        },
        {
            id: '2',
            name: 'Safari',
            category: 'Browsing',
            total_usage: '3h 45m',
            last_used: '2025-04-03 18:20',
            usage_pattern: 'Daily, throughout the day',
            insights: 'Frequent browsing activity with focus on news, social media, and research topics.'
        },
        {
            id: '3',
            name: 'Calendar',
            category: 'Productivity',
            total_usage: '45m',
            last_used: '2025-04-03 10:15',
            usage_pattern: 'Weekdays, primarily mornings',
            insights: 'Regular usage for work scheduling and appointment management.'
        },
        {
            id: '4',
            name: 'Music',
            category: 'Entertainment',
            total_usage: '1h 30m',
            last_used: '2025-04-03 17:30',
            usage_pattern: 'Daily, primarily afternoons',
            insights: 'Consistent music listening during work hours and commuting times.'
        }
    ];
    
    // Sample browser history
    dashboardData.current_analysis.browser_history = [
        {
            url: 'https://www.nytimes.com/section/technology',
            title: 'Technology News - The New York Times',
            timestamp: '2025-04-03 09:15',
            category: 'News',
            insights: 'Regular visits to technology news sections, indicating interest in tech trends.'
        },
        {
            url: 'https://www.github.com/abrignoni/iLEAPP',
            title: 'abrignoni/iLEAPP: iOS Logs, Events, And Plists Parser',
            timestamp: '2025-04-03 10:30',
            category: 'Development',
            insights: 'Frequent visits to GitHub repositories related to digital forensics tools.'
        },
        {
            url: 'https://www.linkedin.com/feed/',
            title: 'LinkedIn Feed',
            timestamp: '2025-04-03 12:45',
            category: 'Social',
            insights: 'Regular professional networking activity during lunch hours.'
        },
        {
            url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            title: 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
            timestamp: '2025-04-03 15:20',
            category: 'Entertainment',
            insights: 'Occasional entertainment breaks during work hours.'
        }
    ];
    
    // Sample music history
    dashboardData.current_analysis.music_history = [
        {
            artist: 'The Beatles',
            title: 'Hey Jude',
            genre: 'Rock',
            play_count: 12,
            last_played: '2025-04-02 18:30',
            insights: 'Frequent listening to classic rock, particularly during evening hours.'
        },
        {
            artist: 'The Beatles',
            title: 'Let It Be',
            genre: 'Rock',
            play_count: 8,
            last_played: '2025-04-01 19:15',
            insights: 'Part of a pattern of listening to complete albums by classic artists.'
        },
        {
            artist: 'Daft Punk',
            title: 'Get Lucky',
            genre: 'Electronic',
            play_count: 15,
            last_played: '2025-04-03 14:20',
            insights: 'High frequency of electronic music during work hours, possibly for focus.'
        },
        {
            artist: 'Daft Punk',
            title: 'Around the World',
            genre: 'Electronic',
            play_count: 10,
            last_played: '2025-04-03 15:05',
            insights: 'Part of a pattern of electronic music during afternoon work sessions.'
        }
    ];
    
    // Sample timeline
    dashboardData.current_analysis.timeline = [
        {
            type: 'message',
            title: 'Conversation with Jane Smith',
            description: 'Discussed weekend plans and dinner arrangements.',
            timestamp: '2025-04-01T10:15:00Z'
        },
        {
            type: 'app',
            title: 'Safari',
            description: 'Browsed technology news on The New York Times.',
            timestamp: '2025-04-03T09:15:00Z'
        },
        {
            type: 'browser',
            title: 'GitHub',
            description: 'Visited iLEAPP repository.',
            timestamp: '2025-04-03T10:30:00Z'
        },
        {
            type: 'message',
            title: 'Conversation with Bob Johnson',
            description: 'Discussed work project deadlines and meeting schedule.',
            timestamp: '2025-04-02T09:05:00Z'
        },
        {
            type: 'music',
            title: 'Daft Punk - Get Lucky',
            description: 'Listened during work hours.',
            timestamp: '2025-04-03T14:20:00Z'
        },
        {
            type: 'app',
            title: 'Calendar',
            description: 'Updated meeting schedule.',
            timestamp: '2025-04-03T10:15:00Z'
        }
    ];
    
    // Sample timeline data for chart
    dashboardData.current_analysis.timeline_data = {
        labels: ['Apr 1', 'Apr 2', 'Apr 3'],
        datasets: [
            {
                label: 'Messages',
                data: [5, 5, 0]
            },
            {
                label: 'App Usage',
                data: [2, 3, 4]
            },
            {
                label: 'Browser',
                data: [3, 2, 4]
            },
            {
                label: 'Music',
                data: [0, 2, 4]
            }
        ]
    };
    
    // Sample key findings
    dashboardData.current_analysis.key_findings = [
        {
            title: 'Social Communication Pattern',
            description: 'Regular communication with a small group of contacts, primarily discussing social plans and work-related topics.'
        },
        {
            title: 'Productivity Focus',
            description: 'Significant usage of productivity apps during work hours, with regular calendar management and project tracking.'
        },
        {
            title: 'Technology Interest',
            description: 'Frequent browsing of technology news and development resources, indicating professional interest in tech topics.'
        },
        {
            title: 'Music During Work',
            description: 'Consistent pattern of listening to electronic music during work hours, potentially as a focus aid.'
        }
    ];
    
    // Sample stats
    dashboardData.current_analysis.artifacts_count = 14;
    dashboardData.current_analysis.insights_count = 8;
    dashboardData.current_analysis.ai_queries_count = 22;
}
"""
        
        # Write files
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(dashboard_dir, 'dashboard.html'), 'w') as f:
            f.write(html_content)
        
        with open(os.path.join(dashboard_dir, 'dashboard.css'), 'w') as f:
            f.write(css_content)
        
        with open(os.path.join(dashboard_dir, 'dashboard.js'), 'w') as f:
            f.write(js_content)
        
        logger.info("Created dashboard files")
    
    def start_server(self):
        """Start the dashboard server"""
        try:
            # Create handler with dashboard data
            handler = lambda *args, **kwargs: DashboardHandler(*args, dashboard_data=self.dashboard_data, **kwargs)
            
            # Find an available port if the specified one is in use
            port = self.port
            while True:
                try:
                    self.server = ThreadedHTTPServer(("", port), handler)
                    break
                except socket.error:
                    port += 1
                    if port > self.port + 10:  # Try 10 ports before giving up
                        raise Exception("Could not find an available port")
            
            self.port = port
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"Dashboard server started on port {self.port}")
            
            return True
        except Exception as e:
            logger.error(f"Error starting dashboard server: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Dashboard server stopped")
    
    def open_dashboard(self):
        """Open the dashboard in a web browser"""
        url = f"http://localhost:{self.port}"
        webbrowser.open(url)
        logger.info(f"Opened dashboard at {url}")
    
    def update_progress(self, percentage, status, artifacts=None):
        """Update analysis progress
        
        Args:
            percentage (int): Progress percentage (0-100)
            status (str): Status message
            artifacts (dict, optional): Artifact status dictionary
        """
        self.dashboard_data['progress'] = {
            'percentage': percentage,
            'status': status,
            'artifacts': artifacts or {}
        }
        
        self._save_data()
    
    def add_analysis(self, analysis_data):
        """Add a new analysis
        
        Args:
            analysis_data (dict): Analysis data
        """
        if 'id' not in analysis_data:
            analysis_data['id'] = str(int(time.time()))
        
        self.dashboard_data['analyses'].append(analysis_data)
        self.dashboard_data['current_analysis'] = analysis_data
        
        self._save_data()
    
    def set_current_analysis(self, analysis_id):
        """Set the current analysis
        
        Args:
            analysis_id (str): ID of the analysis to set as current
        """
        for analysis in self.dashboard_data['analyses']:
            if analysis['id'] == analysis_id:
                self.dashboard_data['current_analysis'] = analysis
                self._save_data()
                return True
        
        return False
    
    def update_analysis_results(self, analysis_id, results):
        """Update analysis results
        
        Args:
            analysis_id (str): ID of the analysis to update
            results (dict): Analysis results
        """
        for analysis in self.dashboard_data['analyses']:
            if analysis['id'] == analysis_id:
                analysis.update(results)
                
                if self.dashboard_data['current_analysis'] and self.dashboard_data['current_analysis']['id'] == analysis_id:
                    self.dashboard_data['current_analysis'] = analysis
                
                self._save_data()
                return True
        
        return False
    
    def add_report_template(self, template_data):
        """Add a new report template
        
        Args:
            template_data (dict): Template data
        """
        if 'id' not in template_data:
            template_data['id'] = str(int(time.time()))
        
        self.dashboard_data['report_templates'].append(template_data)
        
        self._save_data()
    
    def set_filters(self, filters):
        """Set dashboard filters
        
        Args:
            filters (dict): Filter settings
        """
        self.dashboard_data['filters'] = filters
        
        self._save_data()

def main():
    """Main function for running the dashboard"""
    parser = argparse.ArgumentParser(description="iLEAPP AI Integration Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the dashboard server on")
    parser.add_argument("--data-dir", help="Directory for dashboard data")
    
    args = parser.parse_args()
    
    # Create dashboard
    dashboard = UserDashboard(data_dir=args.data_dir, port=args.port)
    
    # Start server
    if dashboard.start_server():
        # Open dashboard in browser
        dashboard.open_dashboard()
        
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Stop server on keyboard interrupt
            dashboard.stop_server()
            print("\nDashboard server stopped")

if __name__ == "__main__":
    main()
