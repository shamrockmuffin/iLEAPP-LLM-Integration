# iLEAPP AI - Enhanced iOS Forensics with Artificial Intelligence

This package contains the complete iLEAPP repository with LLM integration enhancements for iOS digital forensics investigations.

## Overview

iLEAPP AI extends the capabilities of the standard iLEAPP tool with advanced artificial intelligence features that enhance digital forensic investigations. The integration leverages large language models through the OpenRouter API to provide intelligent analysis of iOS artifacts.

## Key Features

- **Artifact-Specific Analyzers**: Specialized analyzers for messages, app usage, iTunes music history, and Chrome browsing history
- **Timeline Visualization**: Interactive timeline showing events across different artifact types
- **Automated Report Generation**: AI-enhanced reports with executive summaries and insights
- **Appendices Generation**: Comprehensive reference materials and statistics
- **Security Features**: Chain of custody tracking, audit logging, and data encryption
- **User Dashboard**: Track analysis progress and manage forensic cases
- **Integration Options**: Support for multiple LLM providers and deployment options

## Installation

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenRouter API key:
   ```
   export OPENROUTER_API_KEY="your_api_key"
   ```
4. Run the iLEAPP AI tool:
   ```
   python ileapp.py
   ```

## Documentation

Complete documentation is available on the project website:
https://vavktgas.manus.space

## Directory Structure

- `scripts/`: Core iLEAPP scripts with AI enhancements
  - `artifacts/`: Artifact extraction modules
  - `openrouter_client.py`: OpenRouter API client
  - `llm_analyzer.py`: Base LLM analyzer class
  - `message_analyzer.py`: Message analysis module
  - `app_usage_analyzer.py`: App usage analysis module
  - `itunes_music_analyzer.py`: iTunes music analysis module
  - `chrome_history_analyzer.py`: Chrome history analysis module
  - `appendices_generator.py`: Appendices generation module
  - `forensic_pipeline.py`: End-to-end forensic analysis pipeline
  - `gui_cli_integration.py`: GUI and CLI integration module
  - `security_enhancements.py`: Security features implementation
  - `user_dashboard.py`: User dashboard implementation
  - `llm_integration_options.py`: LLM integration options
  - `modular_architecture.py`: Modular architecture implementation
  - `demo/`: Demo showcase files and sample data
- `docs/`: Documentation files
  - `api_reference.md`: API reference documentation
  - `integration_guide.md`: Integration guide
  - `openrouter_integration.md`: OpenRouter integration documentation
- `website_backup/`: Backup of the project website

## License

This project is based on iLEAPP by Alexis Brignoni and is subject to the same license terms.

## Contact

For questions or support, please visit the project website or open an issue on the GitHub repository.
