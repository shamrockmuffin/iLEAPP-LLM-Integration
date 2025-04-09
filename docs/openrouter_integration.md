# iLEAPP OpenRouter Integration Documentation

## Overview

This documentation provides comprehensive information about the integration of OpenRouter's LLM capabilities with iLEAPP (iOS Logs, Events, And Plists Parser) for enhanced digital forensics analysis. The integration leverages advanced AI models to analyze iOS artifacts, identify patterns, extract insights, and generate comprehensive reports that augment traditional forensic analysis.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Components](#components)
7. [Artifact Analysis](#artifact-analysis)
8. [Report Generation](#report-generation)
9. [API Reference](#api-reference)
10. [Extending the Integration](#extending-the-integration)
11. [Security Considerations](#security-considerations)
12. [Troubleshooting](#troubleshooting)

## Introduction

The iLEAPP OpenRouter Integration enhances digital forensics analysis of iOS artifacts by incorporating advanced Large Language Models (LLMs) through the OpenRouter API. This integration enables:

- Natural language analysis of iOS artifacts
- Pattern detection and anomaly identification
- Relationship mapping between different data points
- Comprehensive report generation with insights
- Automated appendices and reference materials

This AI-enhanced approach complements traditional forensic analysis by providing deeper insights, identifying non-obvious patterns, and presenting findings in a more accessible format.

## Architecture

The integration follows a modular architecture with the following key components:

1. **OpenRouter Client**: Handles communication with the OpenRouter API
2. **LLM Analyzer**: Base class for artifact analysis with LLM capabilities
3. **Specialized Analyzers**: Artifact-specific analyzers for different iOS data types
4. **OpenRouter Integration**: Main orchestration layer connecting iLEAPP with LLM capabilities
5. **Forensic Analysis Pipeline**: Automated workflow for processing artifacts and generating reports

The architecture is designed to be:
- Modular and extensible
- Minimally invasive to the core iLEAPP functionality
- Configurable for different analysis needs
- Secure in handling sensitive forensic data

![Architecture Diagram](architecture_diagram.png)

## Installation

### Prerequisites

- Python 3.8 or higher
- iLEAPP installed and configured
- OpenRouter API key

### Installation Steps

1. Clone the repository with the OpenRouter integration branch:

```bash
git clone -b openrouter_integration https://github.com/abrignoni/iLEAPP.git ileapp_openrouter
cd ileapp_openrouter
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

## Configuration

The integration can be configured through environment variables or directly in the code:

| Variable | Description | Default |
|----------|-------------|---------|
| OPENROUTER_API_KEY | Your OpenRouter API key | None (Required) |
| OPENROUTER_LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| OPENROUTER_BASE_URL | Base URL for the OpenRouter API | https://openrouter.ai/api/v1 |
| OPENROUTER_DEFAULT_MODEL | Default model to use for analysis | anthropic/claude-3-haiku |

## Usage

### Basic Usage

1. Run iLEAPP with the OpenRouter integration:

```bash
python3 ileapp.py -o /path/to/output -i /path/to/ios/extraction
```

2. Access the AI-enhanced reports in the output directory under the "AI_Enhanced" folder.

### Testing with Sample Data

To test the integration with sample data:

```bash
python3 scripts/test_forensic_analysis.py --api-key your_api_key_here --generate-data
```

This will generate sample data and run the analysis pipeline on it.

## Components

### OpenRouter Client

The `OpenRouterClient` class handles communication with the OpenRouter API, providing methods for:

- Text analysis
- Structured data analysis
- Report generation

### LLM Analyzer

The `LLMAnalyzer` base class provides common functionality for artifact analysis:

- Artifact data processing
- LLM prompt creation
- Model selection based on artifact type and data size
- Analysis result processing

### Specialized Analyzers

The integration includes specialized analyzers for different artifact types:

- **MessageAnalyzer**: Analyzes SMS and iMessage communications
- **AppUsageAnalyzer**: Analyzes app usage patterns
- **iTunesMusicAnalyzer**: Analyzes music listening history
- **ChromeHistoryAnalyzer**: Analyzes web browsing history
- **AppendicesGenerator**: Generates comprehensive reference materials

### OpenRouter Integration

The `OpenRouterIntegration` class orchestrates the analysis process:

- Initializes specialized analyzers
- Routes artifacts to appropriate analyzers
- Handles report generation
- Manages error handling and logging

### Forensic Analysis Pipeline

The `ForensicAnalysisPipeline` class automates the workflow:

- Extracts data from artifact files
- Processes artifacts with LLM capabilities
- Generates enhanced reports
- Creates comprehensive case materials
- Integrates with iLEAPP's reporting system

## Artifact Analysis

The integration supports analysis of the following artifact types:

### Messages (SMS & iMessage)

- Conversation threading and contact correlation
- Sentiment analysis of messages
- Topic extraction and categorization
- Entity recognition (people, places, organizations)
- Anomaly detection in communication patterns

### App Usage

- Usage pattern analysis by time and frequency
- Screen time analysis
- App transition patterns
- Behavioral profiling based on app usage
- Anomaly detection in usage patterns

### iTunes Music History

- Genre and artist preference analysis
- Listening pattern analysis by time
- Mood analysis based on music choices
- Trend analysis of music preferences
- Correlation between music choices and other activities

### Chrome Browser History

- Domain categorization and analysis
- Search query analysis
- Browsing pattern analysis by time
- Interest profiling based on browsing history
- Suspicious activity detection

## Report Generation

The integration enhances iLEAPP's reporting capabilities with:

### Enhanced Artifact Reports

- Detailed analysis with key findings
- Pattern identification and anomaly detection
- Visual representations of data
- Recommendations for further investigation

### Comprehensive Case Summary

- Executive summary of all findings
- Cross-artifact correlations and patterns
- Timeline of significant events
- Overall assessment and recommendations

### Appendices

- Technical appendices with database structure and artifact types
- Timeline appendices with chronological event sequences
- Statistical appendices with data distributions and correlations
- Reference appendices with lookup tables and explanations

## API Reference

### OpenRouterClient

```python
client = OpenRouterClient(api_key)

# Analyze text
response = client.analyze_text(text, model="anthropic/claude-3-haiku")

# Analyze structured data
response = client.analyze_structured_data(data, instructions, model="anthropic/claude-3-sonnet")

# Generate report
response = client.generate_report(data, template, model="anthropic/claude-3-opus")
```

### LLMAnalyzer

```python
analyzer = LLMAnalyzer(api_key)

# Analyze artifact
results = analyzer.analyze_artifact(artifact_data, artifact_type, context)

# Generate insights
insights = analyzer.generate_insights(analysis_results)
```

### OpenRouterIntegration

```python
integration = OpenRouterIntegration(api_key)

# Analyze artifact
results = integration.analyze_artifact(artifact_type, artifact_data, context)

# Generate report
report_html = integration.generate_report(artifact_type, analysis_results)

# Generate appendices
appendices = integration.generate_appendices(all_artifact_data, output_dir)

# Generate case summary
summary_html = integration.generate_case_summary(all_artifact_data, all_analysis_results)

# Custom query
response = integration.custom_query(query, data, model)
```

### ForensicAnalysisPipeline

```python
pipeline = ForensicAnalysisPipeline(api_key)

# Process artifact
pipeline.process_artifact(artifact_type, files_found, report_folder, seeker, wrap_text, timezone_offset)

# Generate case materials
pipeline.generate_case_materials(report_folder, all_artifact_data)
```

## Extending the Integration

The integration is designed to be extensible. To add support for new artifact types:

1. Create a new specialized analyzer class that inherits from `LLMAnalyzer`
2. Implement artifact-specific analysis methods
3. Add extraction logic in the `ForensicAnalysisPipeline` class
4. Update the `OpenRouterIntegration` class to route to the new analyzer

Example:

```python
class NewArtifactAnalyzer(LLMAnalyzer):
    def analyze_new_artifact(self, artifact_data, context=None):
        return self.analyze_artifact(artifact_data, "new_artifact_type", context)
    
    # Implement specialized analysis methods
    def analyze_specific_aspect(self, artifact_data):
        # Implementation
        pass
```

## Security Considerations

The integration handles sensitive forensic data and should be used with appropriate security measures:

- **API Key Security**: Store your OpenRouter API key securely and never commit it to version control
- **Data Privacy**: Be aware that data sent to the OpenRouter API may be processed on external servers
- **Sensitive Information**: Consider redacting sensitive personal information before analysis
- **Result Verification**: Always verify AI-generated insights with traditional forensic methods
- **Chain of Custody**: Document all AI-enhanced analysis steps for legal requirements

## Troubleshooting

### Common Issues

#### API Key Issues

```
Error: OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set
```

Solution: Set the OPENROUTER_API_KEY environment variable or provide it directly to the constructor.

#### Model Selection Errors

```
Error from OpenRouter API: 404 - Model not found
```

Solution: Check that you're using a valid model identifier from the OpenRouter API.

#### Rate Limiting

```
Error from OpenRouter API: 429 - Too Many Requests
```

Solution: Implement rate limiting or request throttling in your application.

#### Large Data Issues

```
Error processing LLM response: Context length exceeded
```

Solution: Reduce the amount of data sent in a single request or use chunking strategies.

### Logging

The integration uses Python's logging module. To enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter issues not covered in this documentation:

1. Check the logs for detailed error messages
2. Review the OpenRouter API documentation
3. Open an issue on the GitHub repository
4. Contact the maintainers for support

---

## License

This integration is released under the same license as iLEAPP.

## Acknowledgments

- The iLEAPP project and its contributors
- OpenRouter for providing access to advanced LLM capabilities
- The digital forensics community for feedback and testing
