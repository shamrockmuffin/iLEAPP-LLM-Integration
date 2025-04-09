# iLEAPP AI Usage Guide

This guide provides detailed instructions for using iLEAPP AI for iOS forensic analysis.

## Getting Started

### Launching the Application

#### GUI Mode:
```bash
python ileapp.py
```

#### CLI Mode:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts messages,app_usage,browser_history
```

### Creating a New Case

1. From the main menu, select "New Case"
2. Enter the case details:
   - Case ID
   - Case Name
   - Investigator Name
   - Description
3. Select the iOS data source:
   - iTunes Backup
   - File System Dump
   - Logical Acquisition
   - Physical Acquisition
4. Select the artifacts to analyze
5. Choose the analysis depth:
   - Basic: Quick analysis with minimal AI processing
   - Standard: Balanced analysis with moderate AI processing
   - Comprehensive: In-depth analysis with extensive AI processing
6. Click "Create Case" to begin the analysis

## Using the Artifact Analyzers

### Message Analyzer

The Message Analyzer provides advanced analysis of iOS messages and conversations.

#### Features:
- Conversation Threading
- Sentiment Analysis
- Topic Extraction
- Entity Recognition
- Contact Correlation
- Language Detection
- Pattern Detection

#### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts messages --analysis-depth comprehensive
```

### App Usage Analyzer

The App Usage Analyzer examines iOS app usage data to identify patterns and behaviors.

#### Features:
- Usage Patterns
- Screen Time Analysis
- App Transitions
- Behavioral Profiling
- Anomaly Detection
- Category Analysis
- Temporal Analysis

#### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts app_usage --analysis-depth comprehensive
```

### iTunes Music Analyzer

The iTunes Music Analyzer examines music listening history and preferences.

#### Features:
- Listening Patterns
- Genre Preferences
- Artist Analysis
- Playlist Analysis
- Purchase History
- Temporal Analysis
- Mood Analysis

#### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts itunes_music --analysis-depth comprehensive
```

### Chrome History Analyzer

The Chrome History Analyzer examines iOS Chrome browsing history.

#### Features:
- Browsing Patterns
- Domain Categorization
- Search Analysis
- Temporal Analysis
- Interest Profiling
- Session Analysis
- Bookmark Analysis

#### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts chrome_history --analysis-depth comprehensive
```

## Using the Timeline Visualization

The timeline visualization tool creates interactive timelines that combine events from different artifact types.

### Features:
- Multi-Artifact Integration
- Interactive Filtering
- Event Clustering
- Zoom and Pan
- Event Details
- Export Options
- Annotation

### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --generate-timeline --output-path /path/to/output/timeline.html
```

## Generating Reports

iLEAPP AI can generate comprehensive forensic reports from analysis results.

### Features:
- Template-Based Generation
- Executive Summaries
- Visualization Integration
- Natural Language Insights
- Multiple Formats
- Customizable Sections
- Chain of Custody

### Example CLI Usage:
```bash
python ileapp.py --cli --case-path /path/to/case --generate-report --output-format pdf --output-path /path/to/output/report.pdf
```

## Using the User Dashboard

The user dashboard provides a centralized interface for managing forensic cases.

### Features:
- Case Management
- Progress Tracking
- Result Filtering
- Report Access
- Notification System
- User Management
- Activity History

### Launching the Dashboard:
```bash
python dashboard.py --port 8080
```

Then access the dashboard at: http://localhost:8080

## Advanced Features

### Security Features

iLEAPP AI includes advanced security features to maintain forensic integrity.

#### Features:
- Chain of Custody Tracking
- Audit Logging
- Data Encryption
- Hash Verification
- Access Controls
- Local LLM Support
- Data Minimization

#### Enabling Audit Logging:
```bash
python ileapp.py --cli --case-path /path/to/case --enable-audit-logging --log-path /path/to/audit.log
```

#### Enabling Encryption:
```bash
python ileapp.py --cli --case-path /path/to/case --encrypt-data --encryption-password secure_password
```

### Integration Options

iLEAPP AI supports multiple integration options to fit different forensic workflows.

#### Features:
- Multiple LLM Providers
- Plugin Architecture
- API Integration
- Command-Line Interface
- Graphical User Interface
- Web Interface
- Standalone Mode

#### Selecting an LLM Provider:
```bash
python ileapp.py --cli --case-path /path/to/case --llm-provider openrouter --llm-model anthropic/claude-3-opus-20240229
```

## Troubleshooting

### Common Issues

1. **Analysis Timeout**:
   - Reduce the analysis depth
   - Process fewer artifacts at once
   - Check your internet connection

2. **Unexpected Results**:
   - Verify the data source is valid and complete
   - Check the artifact selection
   - Review the analysis depth setting

3. **Performance Issues**:
   - Close other resource-intensive applications
   - Use a machine with more RAM
   - Process artifacts in smaller batches

### Getting Help

If you encounter issues not covered here, please:
1. Check the documentation on the project website: https://vavktgas.manus.space
2. Open an issue on the GitHub repository
3. Contact the project maintainers through the website contact form
