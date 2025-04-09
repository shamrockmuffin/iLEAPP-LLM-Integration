# iLEAPP AI Integration API Reference

## Overview

The iLEAPP AI Integration extends the capabilities of the iOS Logs, Events, And Plists Parser (iLEAPP) with artificial intelligence powered by large language models. This API reference documents the classes, methods, and functions available for developers to integrate with and extend the AI capabilities.

## Core Modules

### LLM Integration Options

The `llm_integration_options.py` module provides flexible integration with various LLM providers.

#### BaseLLMProvider

Abstract base class that all LLM providers must implement.

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def initialize(self, **kwargs):
        """Initialize the LLM provider with necessary credentials and settings"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text based on the provided prompt"""
        pass
    
    @abstractmethod
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output based on the provided prompt and schema"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of this LLM provider"""
        pass
```

#### OpenRouterProvider

Integration with OpenRouter API for accessing various LLM models.

```python
class OpenRouterProvider(BaseLLMProvider):
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = None
        self.initialized = False
    
    def initialize(self, api_key=None, model=None, **kwargs):
        """Initialize the OpenRouter provider"""
        # ...
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenRouter API"""
        # ...
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using OpenRouter API"""
        # ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the OpenRouter provider"""
        # ...
```

#### AnthropicProvider

Direct integration with Anthropic Claude API.

```python
class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = None
        self.initialized = False
    
    def initialize(self, api_key=None, model=None, **kwargs):
        """Initialize the Anthropic provider"""
        # ...
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic Claude API"""
        # ...
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using Anthropic Claude API"""
        # ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the Anthropic provider"""
        # ...
```

#### LocalLLMProvider

Integration with locally deployed LLM models.

```python
class LocalLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.client = None
        self.model_path = None
        self.model_type = None
        self.initialized = False
    
    def initialize(self, model_path=None, model_type=None, **kwargs):
        """Initialize the Local LLM provider"""
        # ...
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using local LLM"""
        # ...
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using local LLM"""
        # ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the Local LLM provider"""
        # ...
```

#### LLMProviderFactory

Factory class for creating LLM provider instances.

```python
class LLMProviderFactory:
    @staticmethod
    def create_provider(provider_type: str) -> BaseLLMProvider:
        """Create an LLM provider instance based on the provider type"""
        # ...
```

#### PluginManager

Manager for custom analyzer plugins.

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        # ...
    
    def discover_plugins(self):
        """Discover and register available plugins"""
        # ...
    
    def get_plugin(self, plugin_name: str) -> Optional[Dict]:
        """Get a plugin by name"""
        # ...
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins"""
        # ...
    
    def execute_plugin(self, plugin_name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin on the provided data"""
        # ...
```

#### ForensicToolIntegration

Integration with other forensic tools.

```python
class ForensicToolIntegration:
    def __init__(self):
        self.supported_tools = {
            'autopsy': self._integrate_with_autopsy,
            'ftk': self._integrate_with_ftk,
            'encase': self._integrate_with_encase,
            'cellebrite': self._integrate_with_cellebrite,
            'oxygen': self._integrate_with_oxygen
        }
    
    def list_supported_tools(self) -> List[str]:
        """List supported forensic tools"""
        # ...
    
    def integrate_with_tool(self, tool_name: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with a specific forensic tool"""
        # ...
```

#### IntegrationManager

Manager for all LLM integration options.

```python
class IntegrationManager:
    def __init__(self):
        self.llm_factory = LLMProviderFactory()
        self.plugin_manager = PluginManager()
        self.forensic_tool_integration = ForensicToolIntegration()
        self.active_provider = None
    
    def initialize(self, provider_type: str = 'openrouter', **kwargs) -> bool:
        """Initialize the integration manager with a specific provider"""
        # ...
    
    def get_provider_capabilities(self, provider_type: str = None) -> Dict[str, Any]:
        """Get capabilities of a specific provider or the active provider"""
        # ...
    
    def list_plugins(self) -> List[Dict]:
        """List all available plugins"""
        # ...
    
    def list_supported_forensic_tools(self) -> List[str]:
        """List supported forensic tools"""
        # ...
    
    def analyze_with_llm(self, data: Any, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze data using the active LLM provider"""
        # ...
    
    def execute_plugin(self, plugin_name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin on the provided data"""
        # ...
    
    def integrate_with_forensic_tool(self, tool_name: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with a specific forensic tool"""
        # ...
```

### Artifact Analyzers

The artifact analyzer modules provide specialized analysis for different types of iOS artifacts.

#### LLMAnalyzer

Base class for all artifact analyzers.

```python
class LLMAnalyzer:
    def __init__(self, client=None):
        self.client = client
    
    def analyze(self, data):
        """Base analyze method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement analyze method")
```

#### MessageAnalyzer

Analyzer for iOS message artifacts.

```python
class MessageAnalyzer(LLMAnalyzer):
    def analyze_conversation(self, messages):
        """Analyze a conversation from messages"""
        # ...
    
    def extract_entities(self, messages):
        """Extract entities from messages"""
        # ...
    
    def analyze_sentiment(self, messages):
        """Analyze sentiment in messages"""
        # ...
    
    def identify_topics(self, messages):
        """Identify topics in messages"""
        # ...
```

#### AppUsageAnalyzer

Analyzer for iOS app usage artifacts.

```python
class AppUsageAnalyzer(LLMAnalyzer):
    def analyze_app_usage(self, app_usage_data):
        """Analyze app usage patterns"""
        # ...
    
    def identify_usage_patterns(self, app_usage_data):
        """Identify patterns in app usage"""
        # ...
    
    def generate_usage_timeline(self, app_usage_data):
        """Generate a timeline of app usage"""
        # ...
    
    def assess_productivity(self, app_usage_data):
        """Assess productivity based on app usage"""
        # ...
```

#### ChromeHistoryAnalyzer

Analyzer for iOS Chrome browser history artifacts.

```python
class ChromeHistoryAnalyzer(LLMAnalyzer):
    def analyze_browsing_history(self, history_data):
        """Analyze browsing history"""
        # ...
    
    def categorize_websites(self, history_data):
        """Categorize websites visited"""
        # ...
    
    def identify_browsing_patterns(self, history_data):
        """Identify patterns in browsing behavior"""
        # ...
    
    def assess_security_risks(self, history_data):
        """Assess security risks based on browsing history"""
        # ...
```

#### iTunesMusicAnalyzer

Analyzer for iOS iTunes music history artifacts.

```python
class iTunesMusicAnalyzer(LLMAnalyzer):
    def analyze_music_history(self, music_data):
        """Analyze music listening history"""
        # ...
    
    def identify_music_preferences(self, music_data):
        """Identify music preferences"""
        # ...
    
    def categorize_by_genre(self, music_data):
        """Categorize music by genre"""
        # ...
    
    def generate_listening_timeline(self, music_data):
        """Generate a timeline of music listening"""
        # ...
```

### Forensic Pipeline

The forensic pipeline module provides a comprehensive analysis workflow.

#### ForensicPipeline

Orchestrates the analysis of multiple artifact types.

```python
class ForensicPipeline:
    def __init__(self, client=None):
        self.client = client
        self.analyzers = {
            'messages': MessageAnalyzer(client),
            'app_usage': AppUsageAnalyzer(client),
            'chrome_history': ChromeHistoryAnalyzer(client),
            'itunes_music': iTunesMusicAnalyzer(client)
        }
    
    def analyze(self, forensic_data):
        """Run the full forensic analysis pipeline"""
        # ...
    
    def generate_timeline(self, forensic_data):
        """Generate a comprehensive timeline from all artifacts"""
        # ...
    
    def identify_correlations(self, forensic_data):
        """Identify correlations between different artifact types"""
        # ...
    
    def generate_report(self, analysis_results):
        """Generate a comprehensive report from analysis results"""
        # ...
```

## Demo Showcase

The demo showcase module provides interactive demonstrations of the AI-enhanced forensic capabilities.

#### DemoShowcase

Interactive demonstration of iLEAPP AI integration capabilities.

```python
class DemoShowcase:
    def __init__(self, api_key=None):
        """Initialize the demo showcase"""
        # ...
    
    def run_message_analysis_demo(self):
        """Run a demonstration of message analysis capabilities"""
        # ...
    
    def run_app_usage_analysis_demo(self):
        """Run a demonstration of app usage analysis capabilities"""
        # ...
    
    def run_chrome_history_analysis_demo(self):
        """Run a demonstration of Chrome history analysis capabilities"""
        # ...
    
    def run_itunes_music_analysis_demo(self):
        """Run a demonstration of iTunes music history analysis capabilities"""
        # ...
    
    def run_full_pipeline_demo(self):
        """Run a demonstration of the full forensic analysis pipeline"""
        # ...
    
    def run_all_demos(self):
        """Run all demonstration modules"""
        # ...
```

## Plugin Development

### Creating a Plugin

Plugins allow you to extend the functionality of the iLEAPP AI Integration. Here's how to create a plugin:

1. Use the `create_plugin_template` function to generate a plugin template:

```python
from scripts.llm_integration_options import create_plugin_template

plugin_path = create_plugin_template("my_custom_plugin")
```

2. Edit the generated plugin file to implement your custom logic:

```python
def register_plugin() -> Dict[str, Any]:
    """Register the plugin with the plugin manager"""
    return {
        "name": "my_custom_plugin",
        "description": "My custom plugin for iLEAPP AI Integration",
        "version": "1.0.0",
        "author": "Your Name",
        "input_type": "any",
        "output_type": "any"
    }

def process(data: Any, **kwargs) -> Any:
    """Process the input data"""
    # Implement your plugin logic here
    # ...
    return result
```

3. Place your plugin in the `scripts/plugins` directory to make it discoverable by the plugin manager.

## Command Line Usage

### LLM Integration Options

```bash
python scripts/llm_integration_options.py --provider openrouter --api-key YOUR_API_KEY
python scripts/llm_integration_options.py --provider local --model-path /path/to/model --model-type llama
python scripts/llm_integration_options.py --list-capabilities
python scripts/llm_integration_options.py --create-plugin my_custom_plugin
```

### Demo Showcase

```bash
python scripts/demo/demo_showcase.py --api-key YOUR_API_KEY
python scripts/demo/demo_showcase.py --demo messages
python scripts/demo/demo_showcase.py --demo app-usage
python scripts/demo/demo_showcase.py --demo chrome
python scripts/demo/demo_showcase.py --demo itunes
python scripts/demo/demo_showcase.py --demo pipeline
python scripts/demo/demo_showcase.py --demo all
```

## Integration with iLEAPP

The AI integration is designed to work seamlessly with the existing iLEAPP framework. The integration points include:

1. **Report Enhancement**: AI analysis is added to the standard iLEAPP HTML reports.
2. **CLI Integration**: AI capabilities are accessible through the iLEAPP command line interface.
3. **GUI Integration**: AI capabilities are integrated into the iLEAPP graphical user interface.

For more details on how to use these integration points, see the [Integration Guide](integration_guide.md).
