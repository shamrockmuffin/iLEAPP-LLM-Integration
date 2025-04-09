# Installation Guide for iLEAPP AI

This guide provides detailed instructions for installing and configuring iLEAPP AI for iOS forensic analysis.

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **Python**: Python 3.8 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 1GB for installation, plus space for case data
- **Internet Connection**: Required for OpenRouter API access (unless using local LLM mode)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ileapp-ai.git
cd ileapp-ai
```

### 2. Create a Virtual Environment (Recommended)

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the root directory with your API keys:

```
OPENROUTER_API_KEY=your_openrouter_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

Alternatively, you can set these as environment variables.

### 5. Verify Installation

Run the verification script to ensure everything is installed correctly:

```bash
python verify_installation.py
```

### 6. Launch iLEAPP AI

#### GUI Mode:
```bash
python ileapp.py
```

#### CLI Mode:
```bash
python ileapp.py --cli --case-path /path/to/case --artifacts messages,app_usage,browser_history
```

## Configuration Options

### LLM Provider Selection

Edit the `config.json` file to select your preferred LLM provider:

```json
{
  "llm_provider": "openrouter",
  "llm_model": "anthropic/claude-3-opus-20240229",
  "analysis_depth": "comprehensive"
}
```

Available providers:
- `openrouter`: Uses the OpenRouter API (default)
- `anthropic`: Uses the Anthropic API directly
- `openai`: Uses the OpenAI API
- `local`: Uses a local LLM model

### Local LLM Setup (Optional)

For sensitive investigations where data cannot leave the local environment:

1. Install the required local LLM dependencies:
   ```bash
   pip install -r requirements-local.txt
   ```

2. Download a compatible model (e.g., Llama 3):
   ```bash
   python download_local_model.py --model llama-3-70b
   ```

3. Update the configuration to use the local model:
   ```json
   {
     "llm_provider": "local",
     "llm_model": "llama-3-70b",
     "analysis_depth": "comprehensive"
   }
   ```

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure your API keys are correctly set in the `.env` file or as environment variables
   - Verify you have sufficient credits/quota with your API provider

2. **Dependency Errors**:
   - Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`
   - Ensure you have the correct Python version (3.8+)

3. **Memory Errors**:
   - Reduce the analysis depth in `config.json` to `basic` or `standard`
   - Process fewer artifacts at once

4. **Local LLM Issues**:
   - Ensure you have sufficient RAM for the selected model
   - Check GPU compatibility and drivers if using GPU acceleration

### Getting Help

If you encounter issues not covered here, please:
1. Check the documentation on the project website: https://vavktgas.manus.space
2. Open an issue on the GitHub repository
3. Contact the project maintainers through the website contact form
