# iLEAPP AI Integration Guide

## Introduction

The iLEAPP AI Integration extends the iOS Logs, Events, And Plists Parser (iLEAPP) with artificial intelligence capabilities powered by large language models. This guide provides comprehensive instructions for installing, configuring, and using the AI integration with iLEAPP.

## Installation

### Prerequisites

- Python 3.8 or higher
- iLEAPP installed and functioning
- Internet connection (for cloud-based LLM providers)
- API key for your chosen LLM provider (OpenRouter, Anthropic, etc.)

### Installation Steps

1. **Clone the repository with AI integration**:

```bash
git clone https://github.com/abrignoni/iLEAPP.git
cd iLEAPP
git checkout openrouter_integration
```

2. **Install required dependencies**:

```bash
pip install -r requirements.txt
```

3. **Set up your API key**:

For OpenRouter:
```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

For Anthropic:
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

For local LLM deployment, see the [Local LLM Setup](#local-llm-setup) section.

## Configuration

### LLM Provider Configuration

The integration supports multiple LLM providers. You can configure your preferred provider in the following ways:

#### Command Line Configuration

When running iLEAPP from the command line, you can specify the LLM provider and related options:

```bash
python ileapp.py -i /path/to/input -o /path/to/output --llm-provider openrouter --llm-model anthropic/claude-3-opus
```

#### GUI Configuration

When using the iLEAPP GUI, you can configure the LLM provider in the "AI Settings" tab:

1. Launch the iLEAPP GUI: `python ileappGUI.py`
2. Go to the "AI Settings" tab
3. Select your preferred LLM provider
4. Enter your API key (if not set via environment variable)
5. Select the model to use
6. Configure additional options as needed

#### Configuration File

You can create a configuration file to store your LLM settings:

```json
{
  "llm_provider": "openrouter",
  "llm_model": "anthropic/claude-3-opus",
  "api_key": "your_api_key_here",
  "max_tokens": 4096,
  "temperature": 0.7
}
```

Save this file as `llm_config.json` in the iLEAPP directory or specify a custom path with the `--llm-config` option.

### Local LLM Setup

For sensitive investigations or offline use, you can deploy LLMs locally:

1. **Install the required packages**:

```bash
pip install llama-cpp-python
```

2. **Download a compatible model**:

For LLaMA models:
```bash
mkdir -p models
cd models
# Download LLaMA model (example for LLaMA-3-8B-Instruct)
wget https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf
```

3. **Configure iLEAPP to use the local model**:

```bash
python ileapp.py -i /path/to/input -o /path/to/output --llm-provider local --llm-model-path ./models/llama-3-8b-instruct.Q4_K_M.gguf --llm-model-type llama
```

## Using AI Features

### Command Line Usage

To run iLEAPP with AI analysis enabled:

```bash
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai
```

Additional AI-related options:

```bash
# Specify which artifact types to analyze with AI
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --ai-artifacts messages,app_usage,chrome_history

# Set the analysis depth (basic, standard, comprehensive)
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --ai-depth comprehensive

# Enable specific AI features
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --ai-features sentiment,entity_extraction,timeline_correlation
```

### GUI Usage

1. Launch the iLEAPP GUI: `python ileappGUI.py`
2. Load your iOS extraction
3. In the "Processing Options" section, check "Enable AI Analysis"
4. Configure AI options as needed
5. Click "Process" to start the analysis

### Viewing AI-Enhanced Reports

After processing, iLEAPP will generate an enhanced HTML report with AI analysis sections:

1. Open the generated report in your web browser
2. Navigate to the "AI Analysis" section for overall insights
3. Each artifact type will have its own AI analysis subsection
4. Interactive visualizations will help you explore the data

## Advanced Features

### Plugin System

The AI integration includes a plugin system that allows you to extend its capabilities:

1. **Create a new plugin**:

```bash
python -c "from scripts.llm_integration_options import create_plugin_template; create_plugin_template('my_custom_plugin')"
```

2. **Edit the plugin template** at `scripts/plugins/my_custom_plugin.py`

3. **Use your plugin**:

```bash
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --ai-plugins my_custom_plugin
```

### Integration with Other Forensic Tools

The AI integration can work with other forensic tools:

```bash
# Export iLEAPP data for use with Autopsy
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --export-for autopsy

# Import and analyze data from Cellebrite UFED
python ileapp.py --import-from cellebrite --import-path /path/to/cellebrite/export -o /path/to/output --enable-ai
```

### Demo Showcase

To explore the AI capabilities without a real iOS extraction:

```bash
python scripts/demo/demo_showcase.py --api-key YOUR_API_KEY
```

This will run demonstrations of various AI analysis features using sample data.

## Troubleshooting

### Common Issues

#### API Key Issues

**Problem**: "Error: No API key provided"

**Solution**: Ensure you've set your API key either via environment variable or in the configuration.

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

#### Model Availability

**Problem**: "Error: Model not available"

**Solution**: Check that you're using a valid model name for your chosen provider. For OpenRouter, valid models include:

- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `openai/gpt-4o`

#### Local LLM Issues

**Problem**: "Error loading local model"

**Solution**: 
- Verify the model path is correct
- Ensure you have sufficient RAM for the model size
- Check that you've installed the correct version of llama-cpp-python for your system

#### Plugin Errors

**Problem**: "Error loading plugin"

**Solution**:
- Check that your plugin is in the correct directory (`scripts/plugins/`)
- Verify that your plugin has the required `register_plugin()` and `process()` functions
- Check for syntax errors in your plugin code

### Getting Help

If you encounter issues not covered here:

1. Check the logs in the `logs` directory
2. Visit the [GitHub repository](https://github.com/abrignoni/iLEAPP) for the latest updates
3. Open an issue on GitHub with details about your problem

## Security Considerations

### Data Privacy

When using cloud-based LLM providers, be aware that your data may be sent to external servers. For sensitive investigations:

1. Use the local LLM option
2. Review the privacy policy of your chosen LLM provider
3. Consider using a VPN or isolated network for API calls

### Chain of Custody

The AI integration maintains chain of custody by:

1. Never modifying original artifacts
2. Logging all AI analysis activities
3. Clearly distinguishing between original data and AI-generated insights in reports

### Audit Logging

All AI operations are logged for accountability:

- Log files are stored in the `logs` directory
- Each log entry includes timestamp, operation type, and parameters
- Logs can be included in reports for transparency

## Best Practices

### Effective AI Usage

1. **Start with basic analysis** before diving into comprehensive analysis
2. **Verify AI insights** against the raw data
3. **Use multiple models** for critical investigations to cross-validate findings
4. **Document your AI settings** for reproducibility

### Performance Optimization

1. **Limit the scope** of AI analysis to relevant artifacts
2. **Use local models** for large datasets to avoid API costs
3. **Batch processing** for large extractions
4. **Cache results** to avoid redundant API calls

### Integration with Workflow

1. **Start with traditional analysis** to identify areas for AI focus
2. **Use AI for summarization** of complex artifacts
3. **Leverage timeline correlation** to identify relationships between artifacts
4. **Export findings** for use in reports and presentations

## Advanced Configuration

### Custom Prompts

You can customize the prompts used for AI analysis:

1. Create a `prompts` directory in your iLEAPP installation
2. Create prompt files for specific artifact types (e.g., `messages_prompt.txt`)
3. Use the `--custom-prompts-dir` option to specify your prompts directory

### Fine-tuning Analysis Parameters

For advanced users, you can fine-tune the analysis parameters:

```bash
python ileapp.py -i /path/to/input -o /path/to/output --enable-ai --ai-temperature 0.5 --ai-max-tokens 8192 --ai-top-p 0.9
```

### Batch Processing

For processing multiple extractions:

```bash
python ileapp.py --batch-dir /path/to/extractions -o /path/to/output --enable-ai
```

## Conclusion

The iLEAPP AI Integration enhances digital forensics investigations by providing intelligent analysis of iOS artifacts. By following this guide, you can leverage the power of large language models to gain deeper insights from your forensic data while maintaining the rigor and reliability required for forensic work.

For more detailed information, refer to the [API Reference](api_reference.md) and explore the demo showcase to see the capabilities in action.
