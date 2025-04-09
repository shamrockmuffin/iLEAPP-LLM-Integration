#!/usr/bin/env python3
"""
LLM Integration Options Module for iLEAPP
This module provides expanded integration options for different LLM providers and local models.
"""

import os
import sys
import json
import importlib
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
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

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API integration for accessing various LLM models"""
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = None
        self.initialized = False
    
    def initialize(self, api_key=None, model=None, **kwargs):
        """Initialize the OpenRouter provider
        
        Args:
            api_key (str, optional): OpenRouter API key. If not provided, will look for 
                                     OPENROUTER_API_KEY environment variable
            model (str, optional): Model to use. Defaults to 'anthropic/claude-3-opus'
        """
        try:
            # Add the parent directory to the path to import from scripts
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from openrouter_client import OpenRouterClient
            
            self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
            if not self.api_key:
                logger.warning("No OpenRouter API key provided. Set OPENROUTER_API_KEY environment variable.")
                return False
            
            self.model = model or 'anthropic/claude-3-opus'
            self.client = OpenRouterClient(api_key=self.api_key, model=self.model)
            self.initialized = True
            logger.info(f"OpenRouter provider initialized with model: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter provider: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenRouter API
        
        Args:
            prompt (str): The prompt to send to the model
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            str: Generated text response
        """
        if not self.initialized or not self.client:
            logger.error("OpenRouter provider not initialized")
            return "Error: OpenRouter provider not initialized"
        
        try:
            response = self.client.generate_text(prompt, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Error generating text with OpenRouter: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using OpenRouter API
        
        Args:
            prompt (str): The prompt to send to the model
            output_schema (Dict): JSON schema defining the expected output structure
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            Dict: Structured response according to the provided schema
        """
        if not self.initialized or not self.client:
            logger.error("OpenRouter provider not initialized")
            return {"error": "OpenRouter provider not initialized"}
        
        try:
            response = self.client.generate_structured_output(prompt, output_schema, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Error generating structured output with OpenRouter: {str(e)}")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the OpenRouter provider"""
        return {
            "name": "OpenRouter",
            "description": "Access to multiple LLM providers through OpenRouter API",
            "models": [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o",
                "openai/gpt-4-turbo",
                "google/gemini-pro",
                "meta-llama/llama-3-70b-instruct"
            ],
            "features": [
                "text_generation",
                "structured_output",
                "multi_provider_access"
            ],
            "max_tokens": 100000,
            "requires_api_key": True,
            "supports_streaming": True
        }

class AnthropicProvider(BaseLLMProvider):
    """Direct Anthropic Claude API integration"""
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self.model = None
        self.initialized = False
    
    def initialize(self, api_key=None, model=None, **kwargs):
        """Initialize the Anthropic provider
        
        Args:
            api_key (str, optional): Anthropic API key. If not provided, will look for 
                                     ANTHROPIC_API_KEY environment variable
            model (str, optional): Model to use. Defaults to 'claude-3-opus-20240229'
        """
        try:
            import anthropic
            
            self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
            if not self.api_key:
                logger.warning("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable.")
                return False
            
            self.model = model or 'claude-3-opus-20240229'
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.initialized = True
            logger.info(f"Anthropic provider initialized with model: {self.model}")
            return True
        except ImportError:
            logger.error("Anthropic Python SDK not installed. Install with: pip install anthropic")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic Claude API
        
        Args:
            prompt (str): The prompt to send to the model
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            str: Generated text response
        """
        if not self.initialized or not self.client:
            logger.error("Anthropic provider not initialized")
            return "Error: Anthropic provider not initialized"
        
        try:
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 0.7)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using Anthropic Claude API
        
        Args:
            prompt (str): The prompt to send to the model
            output_schema (Dict): JSON schema defining the expected output structure
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            Dict: Structured response according to the provided schema
        """
        if not self.initialized or not self.client:
            logger.error("Anthropic provider not initialized")
            return {"error": "Anthropic provider not initialized"}
        
        try:
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 0.7)
            
            # Create a system prompt that instructs Claude to output JSON according to the schema
            system_prompt = f"You are a helpful assistant that outputs JSON according to this schema: {json.dumps(output_schema)}"
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON from the response
            response_text = message.content[0].text
            
            # Find JSON in the response (it might be wrapped in ```json blocks)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.error("Could not find valid JSON in Anthropic response")
                return {"error": "Could not find valid JSON in response"}
        except Exception as e:
            logger.error(f"Error generating structured output with Anthropic: {str(e)}")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the Anthropic provider"""
        return {
            "name": "Anthropic Claude",
            "description": "Direct integration with Anthropic Claude API",
            "models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "features": [
                "text_generation",
                "structured_output",
                "vision_capabilities"
            ],
            "max_tokens": 100000,
            "requires_api_key": True,
            "supports_streaming": True
        }

class LocalLLMProvider(BaseLLMProvider):
    """Integration with locally deployed LLM models"""
    
    def __init__(self):
        self.client = None
        self.model_path = None
        self.model_type = None
        self.initialized = False
    
    def initialize(self, model_path=None, model_type=None, **kwargs):
        """Initialize the Local LLM provider
        
        Args:
            model_path (str): Path to the local model
            model_type (str): Type of model ('llama', 'mistral', 'falcon', etc.)
            **kwargs: Additional parameters for model initialization
        """
        try:
            self.model_path = model_path
            if not self.model_path:
                logger.warning("No model path provided for local LLM")
                return False
            
            self.model_type = model_type or 'llama'
            
            # Initialize based on model type
            if self.model_type.lower() == 'llama':
                try:
                    from llama_cpp import Llama
                    
                    n_gpu_layers = kwargs.get('n_gpu_layers', -1)  # -1 means use all available layers
                    n_ctx = kwargs.get('n_ctx', 2048)
                    
                    self.client = Llama(
                        model_path=self.model_path,
                        n_gpu_layers=n_gpu_layers,
                        n_ctx=n_ctx
                    )
                    self.initialized = True
                    logger.info(f"Local LLM provider initialized with model: {self.model_path}")
                    return True
                except ImportError:
                    logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
                    return False
            
            elif self.model_type.lower() == 'mistral':
                try:
                    from mistralai.client import MistralClient
                    from mistralai.models.chat_completion import ChatMessage
                    
                    # For Mistral, we assume it's running as a local API server
                    api_base = kwargs.get('api_base', 'http://localhost:8000')
                    api_key = kwargs.get('api_key', 'not-needed-for-local')
                    
                    self.client = MistralClient(api_key=api_key, endpoint=api_base)
                    self.chat_message_class = ChatMessage
                    self.initialized = True
                    logger.info(f"Local Mistral provider initialized with endpoint: {api_base}")
                    return True
                except ImportError:
                    logger.error("mistralai client not installed. Install with: pip install mistralai")
                    return False
            
            else:
                logger.error(f"Unsupported model type: {self.model_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Local LLM provider: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using local LLM
        
        Args:
            prompt (str): The prompt to send to the model
            **kwargs: Additional parameters to pass to the model
        
        Returns:
            str: Generated text response
        """
        if not self.initialized or not self.client:
            logger.error("Local LLM provider not initialized")
            return "Error: Local LLM provider not initialized"
        
        try:
            if self.model_type.lower() == 'llama':
                max_tokens = kwargs.get('max_tokens', 512)
                temperature = kwargs.get('temperature', 0.7)
                
                output = self.client.create_completion(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return output['choices'][0]['text']
            
            elif self.model_type.lower() == 'mistral':
                max_tokens = kwargs.get('max_tokens', 512)
                temperature = kwargs.get('temperature', 0.7)
                
                messages = [self.chat_message_class(role="user", content=prompt)]
                
                chat_response = self.client.chat(
                    model="local-model",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return chat_response.choices[0].message.content
            
            else:
                return "Error: Unsupported model type"
                
        except Exception as e:
            logger.error(f"Error generating text with Local LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_structured_output(self, prompt: str, output_schema: Dict, **kwargs) -> Dict:
        """Generate structured output using local LLM
        
        Args:
            prompt (str): The prompt to send to the model
            output_schema (Dict): JSON schema defining the expected output structure
            **kwargs: Additional parameters to pass to the model
        
        Returns:
            Dict: Structured response according to the provided schema
        """
        if not self.initialized or not self.client:
            logger.error("Local LLM provider not initialized")
            return {"error": "Local LLM provider not initialized"}
        
        try:
            # Create a prompt that instructs the model to output JSON according to the schema
            structured_prompt = f"""
            You must respond with valid JSON that matches this schema:
            {json.dumps(output_schema, indent=2)}
            
            Your task: {prompt}
            
            Response (valid JSON only):
            """
            
            response_text = self.generate_text(structured_prompt, **kwargs)
            
            # Find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.error("Could not find valid JSON in Local LLM response")
                return {"error": "Could not find valid JSON in response"}
                
        except Exception as e:
            logger.error(f"Error generating structured output with Local LLM: {str(e)}")
            return {"error": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of the Local LLM provider"""
        capabilities = {
            "name": "Local LLM",
            "description": "Integration with locally deployed LLM models",
            "features": [
                "text_generation",
                "structured_output",
                "offline_operation",
                "privacy_focused"
            ],
            "requires_api_key": False,
            "supports_streaming": False
        }
        
        if self.model_type.lower() == 'llama':
            capabilities.update({
                "models": ["LLaMA-2", "LLaMA-3"],
                "max_tokens": 4096
            })
        elif self.model_type.lower() == 'mistral':
            capabilities.update({
                "models": ["Mistral-7B", "Mixtral-8x7B"],
                "max_tokens": 8192
            })
        
        return capabilities

class LLMProviderFactory:
    """Factory class for creating LLM provider instances"""
    
    @staticmethod
    def create_provider(provider_type: str) -> BaseLLMProvider:
        """Create an LLM provider instance based on the provider type
        
        Args:
            provider_type (str): Type of provider ('openrouter', 'anthropic', 'local')
        
        Returns:
            BaseLLMProvider: An instance of the requested provider
        """
        provider_type = provider_type.lower()
        
        if provider_type == 'openrouter':
            return OpenRouterProvider()
        elif provider_type == 'anthropic':
            return AnthropicProvider()
        elif provider_type == 'local':
            return LocalLLMProvider()
        else:
            logger.error(f"Unsupported provider type: {provider_type}")
            raise ValueError(f"Unsupported provider type: {provider_type}")

class PluginManager:
    """Manager for custom analyzer plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        
        # Create plugins directory if it doesn't exist
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            # Create __init__.py to make it a proper package
            with open(os.path.join(self.plugin_dir, '__init__.py'), 'w') as f:
                f.write('# Plugin package for iLEAPP AI Integration\n')
    
    def discover_plugins(self):
        """Discover and register available plugins"""
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return
        
        # Get all Python files in the plugins directory
        plugin_files = [f[:-3] for f in os.listdir(self.plugin_dir) 
                       if f.endswith('.py') and f != '__init__.py']
        
        for plugin_name in plugin_files:
            try:
                # Import the plugin module
                module_path = f"plugins.{plugin_name}"
                plugin_module = importlib.import_module(module_path)
                
                # Check if the module has a register_plugin function
                if hasattr(plugin_module, 'register_plugin'):
                    plugin_info = plugin_module.register_plugin()
                    self.plugins[plugin_name] = plugin_info
                    logger.info(f"Registered plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} does not have a register_plugin function")
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Dict]:
        """Get a plugin by name
        
        Args:
            plugin_name (str): Name of the plugin
        
        Returns:
            Optional[Dict]: Plugin information or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins
        
        Returns:
            List[Dict]: List of plugin information dictionaries
        """
        return [{"name": name, **info} for name, info in self.plugins.items()]
    
    def execute_plugin(self, plugin_name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin on the provided data
        
        Args:
            plugin_name (str): Name of the plugin to execute
            data (Any): Data to process with the plugin
            **kwargs: Additional parameters for the plugin
        
        Returns:
            Any: Result of the plugin execution
        """
        plugin_info = self.get_plugin(plugin_name)
        if not plugin_info:
            logger.error(f"Plugin not found: {plugin_name}")
            return None
        
        try:
            # Import the plugin module
            module_path = f"plugins.{plugin_name}"
            plugin_module = importlib.import_module(module_path)
            
            # Execute the plugin's process function
            if hasattr(plugin_module, 'process'):
                return plugin_module.process(data, **kwargs)
            else:
                logger.error(f"Plugin {plugin_name} does not have a process function")
                return None
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {str(e)}")
            return None

class ForensicToolIntegration:
    """Integration with other forensic tools"""
    
    def __init__(self):
        self.supported_tools = {
            'autopsy': self._integrate_with_autopsy,
            'ftk': self._integrate_with_ftk,
            'encase': self._integrate_with_encase,
            'cellebrite': self._integrate_with_cellebrite,
            'oxygen': self._integrate_with_oxygen
        }
    
    def list_supported_tools(self) -> List[str]:
        """List supported forensic tools
        
        Returns:
            List[str]: List of supported tool names
        """
        return list(self.supported_tools.keys())
    
    def integrate_with_tool(self, tool_name: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with a specific forensic tool
        
        Args:
            tool_name (str): Name of the forensic tool
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        tool_name = tool_name.lower()
        if tool_name not in self.supported_tools:
            logger.error(f"Unsupported forensic tool: {tool_name}")
            return {"error": f"Unsupported forensic tool: {tool_name}"}
        
        try:
            integration_func = self.supported_tools[tool_name]
            return integration_func(data_path, **kwargs)
        except Exception as e:
            logger.error(f"Error integrating with {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    def _integrate_with_autopsy(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with Autopsy
        
        Args:
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        logger.info(f"Integrating with Autopsy: {data_path}")
        
        # Implementation would depend on Autopsy's API or command-line interface
        # This is a placeholder for the actual implementation
        return {
            "tool": "Autopsy",
            "status": "integration_placeholder",
            "data_path": data_path
        }
    
    def _integrate_with_ftk(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with Forensic Toolkit (FTK)
        
        Args:
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        logger.info(f"Integrating with FTK: {data_path}")
        
        # Implementation would depend on FTK's API or command-line interface
        # This is a placeholder for the actual implementation
        return {
            "tool": "FTK",
            "status": "integration_placeholder",
            "data_path": data_path
        }
    
    def _integrate_with_encase(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with EnCase
        
        Args:
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        logger.info(f"Integrating with EnCase: {data_path}")
        
        # Implementation would depend on EnCase's API or command-line interface
        # This is a placeholder for the actual implementation
        return {
            "tool": "EnCase",
            "status": "integration_placeholder",
            "data_path": data_path
        }
    
    def _integrate_with_cellebrite(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with Cellebrite UFED
        
        Args:
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        logger.info(f"Integrating with Cellebrite UFED: {data_path}")
        
        # Implementation would depend on Cellebrite's API or command-line interface
        # This is a placeholder for the actual implementation
        return {
            "tool": "Cellebrite UFED",
            "status": "integration_placeholder",
            "data_path": data_path
        }
    
    def _integrate_with_oxygen(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with Oxygen Forensic Detective
        
        Args:
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        logger.info(f"Integrating with Oxygen Forensic Detective: {data_path}")
        
        # Implementation would depend on Oxygen's API or command-line interface
        # This is a placeholder for the actual implementation
        return {
            "tool": "Oxygen Forensic Detective",
            "status": "integration_placeholder",
            "data_path": data_path
        }

class IntegrationManager:
    """Manager for all LLM integration options"""
    
    def __init__(self):
        self.llm_factory = LLMProviderFactory()
        self.plugin_manager = PluginManager()
        self.forensic_tool_integration = ForensicToolIntegration()
        self.active_provider = None
    
    def initialize(self, provider_type: str = 'openrouter', **kwargs) -> bool:
        """Initialize the integration manager with a specific provider
        
        Args:
            provider_type (str, optional): Type of LLM provider. Defaults to 'openrouter'.
            **kwargs: Additional parameters for provider initialization
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create provider
            self.active_provider = self.llm_factory.create_provider(provider_type)
            
            # Initialize provider
            success = self.active_provider.initialize(**kwargs)
            
            # Discover plugins
            self.plugin_manager.discover_plugins()
            
            return success
        except Exception as e:
            logger.error(f"Error initializing integration manager: {str(e)}")
            return False
    
    def get_provider_capabilities(self, provider_type: str = None) -> Dict[str, Any]:
        """Get capabilities of a specific provider or the active provider
        
        Args:
            provider_type (str, optional): Type of provider to get capabilities for.
                                          If None, returns capabilities of the active provider.
        
        Returns:
            Dict[str, Any]: Provider capabilities
        """
        if provider_type:
            provider = self.llm_factory.create_provider(provider_type)
            return provider.get_capabilities()
        elif self.active_provider:
            return self.active_provider.get_capabilities()
        else:
            return {"error": "No active provider"}
    
    def list_plugins(self) -> List[Dict]:
        """List all available plugins
        
        Returns:
            List[Dict]: List of plugin information dictionaries
        """
        return self.plugin_manager.list_plugins()
    
    def list_supported_forensic_tools(self) -> List[str]:
        """List supported forensic tools
        
        Returns:
            List[str]: List of supported tool names
        """
        return self.forensic_tool_integration.list_supported_tools()
    
    def analyze_with_llm(self, data: Any, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze data using the active LLM provider
        
        Args:
            data (Any): Data to analyze
            analysis_type (str): Type of analysis to perform
            **kwargs: Additional parameters for the analysis
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        if not self.active_provider:
            logger.error("No active LLM provider")
            return {"error": "No active LLM provider"}
        
        try:
            # Convert data to a format suitable for the LLM
            if isinstance(data, dict) or isinstance(data, list):
                data_str = json.dumps(data, indent=2)
            else:
                data_str = str(data)
            
            # Create prompt based on analysis type
            if analysis_type == 'message_analysis':
                prompt = f"""
                Analyze the following message data:
                {data_str}
                
                Provide a detailed analysis including:
                1. Conversation summary
                2. Sentiment analysis
                3. Key topics discussed
                4. Relationship assessment between participants
                """
                
                output_schema = {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "sentiment_analysis": {"type": "string"},
                        "key_topics": {"type": "array", "items": {"type": "string"}},
                        "relationship_assessment": {"type": "string"}
                    }
                }
            
            elif analysis_type == 'app_usage_analysis':
                prompt = f"""
                Analyze the following app usage data:
                {data_str}
                
                Provide a detailed analysis including:
                1. Usage pattern summary
                2. Behavioral insights
                3. Productivity assessment
                4. Recommendations for the user
                """
                
                output_schema = {
                    "type": "object",
                    "properties": {
                        "usage_pattern_summary": {"type": "string"},
                        "behavioral_insights": {"type": "string"},
                        "productivity_assessment": {"type": "string"},
                        "recommendations": {"type": "array", "items": {"type": "string"}}
                    }
                }
            
            elif analysis_type == 'browser_history_analysis':
                prompt = f"""
                Analyze the following browser history data:
                {data_str}
                
                Provide a detailed analysis including:
                1. Browsing pattern summary
                2. Interest categories
                3. Security assessment
                4. Behavioral insights
                """
                
                output_schema = {
                    "type": "object",
                    "properties": {
                        "browsing_pattern_summary": {"type": "string"},
                        "interest_categories": {"type": "array", "items": {"type": "string"}},
                        "security_assessment": {"type": "string"},
                        "behavioral_insights": {"type": "string"}
                    }
                }
            
            elif analysis_type == 'music_history_analysis':
                prompt = f"""
                Analyze the following music listening history:
                {data_str}
                
                Provide a detailed analysis including:
                1. Music taste summary
                2. Genre preferences
                3. Listening pattern insights
                4. Music recommendations
                """
                
                output_schema = {
                    "type": "object",
                    "properties": {
                        "music_taste_summary": {"type": "string"},
                        "genre_preferences": {"type": "array", "items": {"type": "string"}},
                        "listening_pattern_insights": {"type": "string"},
                        "music_recommendations": {"type": "array", "items": {"type": "string"}}
                    }
                }
            
            elif analysis_type == 'custom':
                # For custom analysis, the prompt and schema should be provided in kwargs
                prompt = kwargs.get('prompt')
                output_schema = kwargs.get('output_schema')
                
                if not prompt or not output_schema:
                    logger.error("Custom analysis requires 'prompt' and 'output_schema' parameters")
                    return {"error": "Custom analysis requires 'prompt' and 'output_schema' parameters"}
            
            else:
                logger.error(f"Unsupported analysis type: {analysis_type}")
                return {"error": f"Unsupported analysis type: {analysis_type}"}
            
            # Generate structured output
            result = self.active_provider.generate_structured_output(prompt, output_schema, **kwargs)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing data with LLM: {str(e)}")
            return {"error": str(e)}
    
    def execute_plugin(self, plugin_name: str, data: Any, **kwargs) -> Any:
        """Execute a plugin on the provided data
        
        Args:
            plugin_name (str): Name of the plugin to execute
            data (Any): Data to process with the plugin
            **kwargs: Additional parameters for the plugin
        
        Returns:
            Any: Result of the plugin execution
        """
        return self.plugin_manager.execute_plugin(plugin_name, data, **kwargs)
    
    def integrate_with_forensic_tool(self, tool_name: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """Integrate with a specific forensic tool
        
        Args:
            tool_name (str): Name of the forensic tool
            data_path (str): Path to the data to be processed
            **kwargs: Additional parameters for the integration
        
        Returns:
            Dict[str, Any]: Results of the integration
        """
        return self.forensic_tool_integration.integrate_with_tool(tool_name, data_path, **kwargs)

# Example plugin template
def create_plugin_template(plugin_name: str, plugin_dir: str = None):
    """Create a template for a new plugin
    
    Args:
        plugin_name (str): Name of the plugin
        plugin_dir (str, optional): Directory to create the plugin in.
                                   If None, uses the default plugins directory.
    
    Returns:
        str: Path to the created plugin file
    """
    if not plugin_dir:
        plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
    
    # Create plugins directory if it doesn't exist
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
        # Create __init__.py to make it a proper package
        with open(os.path.join(plugin_dir, '__init__.py'), 'w') as f:
            f.write('# Plugin package for iLEAPP AI Integration\n')
    
    plugin_file = os.path.join(plugin_dir, f"{plugin_name}.py")
    
    # Create plugin template
    template = f"""#!/usr/bin/env python3
\"\"\"
{plugin_name} Plugin for iLEAPP AI Integration
\"\"\"

import json
from typing import Dict, List, Any

def register_plugin() -> Dict[str, Any]:
    \"\"\"Register the plugin with the plugin manager
    
    Returns:
        Dict[str, Any]: Plugin information
    \"\"\"
    return {{
        "name": "{plugin_name}",
        "description": "Description of {plugin_name} plugin",
        "version": "1.0.0",
        "author": "Your Name",
        "input_type": "any",  # Specify the expected input type
        "output_type": "any"  # Specify the output type
    }}

def process(data: Any, **kwargs) -> Any:
    \"\"\"Process the input data
    
    Args:
        data (Any): Input data to process
        **kwargs: Additional parameters
    
    Returns:
        Any: Processed data
    \"\"\"
    # Implement your plugin logic here
    
    # Example: If input is a list of messages, count messages by sender
    if isinstance(data, list) and all(isinstance(item, dict) and 'sender' in item for item in data):
        sender_counts = {{}}
        for message in data:
            sender = message['sender']
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        return {{
            "plugin": "{plugin_name}",
            "analysis_type": "message_count_by_sender",
            "results": sender_counts
        }}
    
    # Default return if input type is not handled
    return {{
        "plugin": "{plugin_name}",
        "error": "Unsupported input type",
        "input_type": str(type(data))
    }}

# Example usage
if __name__ == "__main__":
    # Test the plugin with sample data
    sample_data = [
        {{"sender": "John", "content": "Hello"}},
        {{"sender": "Jane", "content": "Hi there"}},
        {{"sender": "John", "content": "How are you?"}},
    ]
    
    result = process(sample_data)
    print(json.dumps(result, indent=2))
"""
    
    with open(plugin_file, 'w') as f:
        f.write(template)
    
    logger.info(f"Created plugin template: {plugin_file}")
    return plugin_file

# Main function for testing
def main():
    """Main function for testing the integration options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Integration Options for iLEAPP")
    parser.add_argument("--provider", choices=["openrouter", "anthropic", "local"], default="openrouter",
                        help="LLM provider to use")
    parser.add_argument("--api-key", help="API key for the selected provider")
    parser.add_argument("--model", help="Model to use with the selected provider")
    parser.add_argument("--model-path", help="Path to local model (for local provider)")
    parser.add_argument("--model-type", help="Type of local model (for local provider)")
    parser.add_argument("--create-plugin", help="Create a plugin template with the given name")
    parser.add_argument("--list-capabilities", action="store_true", help="List capabilities of the selected provider")
    
    args = parser.parse_args()
    
    # Create plugin template if requested
    if args.create_plugin:
        plugin_path = create_plugin_template(args.create_plugin)
        print(f"Created plugin template: {plugin_path}")
        return
    
    # Initialize integration manager
    manager = IntegrationManager()
    
    # Initialize with selected provider
    kwargs = {}
    if args.api_key:
        kwargs["api_key"] = args.api_key
    if args.model:
        kwargs["model"] = args.model
    if args.model_path:
        kwargs["model_path"] = args.model_path
    if args.model_type:
        kwargs["model_type"] = args.model_type
    
    success = manager.initialize(args.provider, **kwargs)
    
    if not success:
        print(f"Failed to initialize {args.provider} provider")
        return
    
    print(f"Successfully initialized {args.provider} provider")
    
    # List capabilities if requested
    if args.list_capabilities:
        capabilities = manager.get_provider_capabilities()
        print("\nProvider Capabilities:")
        print(json.dumps(capabilities, indent=2))
    
    # List plugins
    plugins = manager.list_plugins()
    if plugins:
        print("\nAvailable Plugins:")
        for plugin in plugins:
            print(f"- {plugin['name']}: {plugin['description']}")
    else:
        print("\nNo plugins available")
    
    # List supported forensic tools
    tools = manager.list_supported_forensic_tools()
    print("\nSupported Forensic Tools:")
    for tool in tools:
        print(f"- {tool}")

if __name__ == "__main__":
    main()
