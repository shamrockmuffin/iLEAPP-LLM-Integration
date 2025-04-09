"""
Versioning and modular architecture for iLEAPP LLM integration.

This module provides a plugin architecture and versioning system for the LLM-enhanced iLEAPP.
"""

import os
import sys
import json
import importlib
import inspect
import logging
import pkgutil
import semver
from typing import Dict, List, Any, Callable, Optional, Type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ileapp_llm_architecture")

class VersionManager:
    """Manages versioning for the LLM integration components."""
    
    VERSION_FILE = "version.json"
    
    def __init__(self, base_dir: str = None):
        """Initialize the version manager.
        
        Args:
            base_dir: Base directory for version file storage
        """
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.version_file = os.path.join(self.base_dir, self.VERSION_FILE)
        self.version_info = self._load_version_info()
        
    def _load_version_info(self) -> Dict[str, Any]:
        """Load version information from file."""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Invalid version file: {self.version_file}")
                return self._create_default_version_info()
        else:
            return self._create_default_version_info()
    
    def _create_default_version_info(self) -> Dict[str, Any]:
        """Create default version information."""
        return {
            "version": "1.0.0",
            "components": {},
            "compatibility": {
                "ileapp_min_version": "1.0.0",
                "python_min_version": "3.6.0"
            },
            "release_date": None,
            "release_notes": ""
        }
    
    def get_version(self) -> str:
        """Get the current version string."""
        return self.version_info.get("version", "0.0.0")
    
    def update_version(self, version_type: str = "patch") -> str:
        """Update the version according to semver.
        
        Args:
            version_type: Type of version update (major, minor, patch)
            
        Returns:
            Updated version string
        """
        current = self.get_version()
        
        if version_type == "major":
            new_version = str(semver.VersionInfo.parse(current).bump_major())
        elif version_type == "minor":
            new_version = str(semver.VersionInfo.parse(current).bump_minor())
        else:  # patch
            new_version = str(semver.VersionInfo.parse(current).bump_patch())
            
        self.version_info["version"] = new_version
        self._save_version_info()
        
        logger.info(f"Version updated from {current} to {new_version}")
        return new_version
    
    def register_component(self, name: str, version: str, description: str = "") -> None:
        """Register a component with its version.
        
        Args:
            name: Component name
            version: Component version
            description: Component description
        """
        self.version_info.setdefault("components", {})
        self.version_info["components"][name] = {
            "version": version,
            "description": description
        }
        self._save_version_info()
        logger.info(f"Component registered: {name} v{version}")
    
    def _save_version_info(self) -> None:
        """Save version information to file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.version_info, f, indent=2)


class PluginManager:
    """Manages plugins for the LLM integration."""
    
    def __init__(self, plugin_dirs: List[str] = None):
        """Initialize the plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self.plugins = {}
        self.plugin_instances = {}
        
        # Add default plugin directory
        default_plugin_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "plugins"
        )
        if os.path.exists(default_plugin_dir) and default_plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(default_plugin_dir)
            
        # Ensure plugin directories exist
        for plugin_dir in self.plugin_dirs:
            os.makedirs(plugin_dir, exist_ok=True)
            
        # Add plugin directories to path
        for plugin_dir in self.plugin_dirs:
            if plugin_dir not in sys.path:
                sys.path.append(plugin_dir)
    
    def discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Discover available plugins in the plugin directories.
        
        Returns:
            Dictionary of plugin information
        """
        self.plugins = {}
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
                
            for _, name, ispkg in pkgutil.iter_modules([plugin_dir]):
                if not ispkg:
                    try:
                        module = importlib.import_module(name)
                        
                        # Look for plugin class
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (inspect.isclass(attr) and 
                                hasattr(attr, 'PLUGIN_TYPE') and 
                                hasattr(attr, 'PLUGIN_NAME')):
                                
                                plugin_info = {
                                    "name": attr.PLUGIN_NAME,
                                    "type": attr.PLUGIN_TYPE,
                                    "description": getattr(attr, 'PLUGIN_DESCRIPTION', ''),
                                    "version": getattr(attr, 'PLUGIN_VERSION', '0.1.0'),
                                    "module": name,
                                    "class": attr_name,
                                    "path": plugin_dir
                                }
                                
                                plugin_id = f"{name}.{attr_name}"
                                self.plugins[plugin_id] = plugin_info
                                logger.info(f"Discovered plugin: {plugin_info['name']} ({plugin_id})")
                                
                    except (ImportError, AttributeError) as e:
                        logger.warning(f"Error loading plugin {name}: {str(e)}")
        
        return self.plugins
    
    def load_plugin(self, plugin_id: str) -> Any:
        """Load a specific plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance
        """
        if plugin_id not in self.plugins:
            if plugin_id not in self.discover_plugins():
                raise ValueError(f"Plugin not found: {plugin_id}")
        
        if plugin_id in self.plugin_instances:
            return self.plugin_instances[plugin_id]
            
        plugin_info = self.plugins[plugin_id]
        module_name = plugin_info["module"]
        class_name = plugin_info["class"]
        
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()
            
            self.plugin_instances[plugin_id] = plugin_instance
            logger.info(f"Loaded plugin: {plugin_info['name']}")
            
            return plugin_instance
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load plugin {plugin_id}: {str(e)}")
            raise
    
    def load_plugins_by_type(self, plugin_type: str) -> Dict[str, Any]:
        """Load all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to load
            
        Returns:
            Dictionary of plugin instances by ID
        """
        self.discover_plugins()
        loaded_plugins = {}
        
        for plugin_id, plugin_info in self.plugins.items():
            if plugin_info["type"] == plugin_type:
                try:
                    plugin = self.load_plugin(plugin_id)
                    loaded_plugins[plugin_id] = plugin
                except Exception as e:
                    logger.warning(f"Failed to load plugin {plugin_id}: {str(e)}")
        
        return loaded_plugins
    
    def register_plugin(self, plugin_class: Type, module_name: str = None) -> str:
        """Register a new plugin.
        
        Args:
            plugin_class: Plugin class to register
            module_name: Module name (defaults to class module)
            
        Returns:
            Plugin ID
        """
        if not (hasattr(plugin_class, 'PLUGIN_TYPE') and 
                hasattr(plugin_class, 'PLUGIN_NAME')):
            raise ValueError("Invalid plugin class: missing PLUGIN_TYPE or PLUGIN_NAME")
        
        if not module_name:
            module_name = plugin_class.__module__
            
        class_name = plugin_class.__name__
        plugin_id = f"{module_name}.{class_name}"
        
        plugin_info = {
            "name": plugin_class.PLUGIN_NAME,
            "type": plugin_class.PLUGIN_TYPE,
            "description": getattr(plugin_class, 'PLUGIN_DESCRIPTION', ''),
            "version": getattr(plugin_class, 'PLUGIN_VERSION', '0.1.0'),
            "module": module_name,
            "class": class_name,
            "path": None  # Dynamic registration
        }
        
        self.plugins[plugin_id] = plugin_info
        logger.info(f"Registered plugin: {plugin_info['name']} ({plugin_id})")
        
        return plugin_id


class ModuleRegistry:
    """Registry for LLM integration modules."""
    
    def __init__(self):
        """Initialize the module registry."""
        self.modules = {}
        self.dependencies = {}
        
    def register_module(self, name: str, module_class: Type, 
                        dependencies: List[str] = None) -> None:
        """Register a module.
        
        Args:
            name: Module name
            module_class: Module class
            dependencies: List of module dependencies
        """
        self.modules[name] = module_class
        self.dependencies[name] = dependencies or []
        logger.info(f"Registered module: {name}")
        
    def get_module(self, name: str) -> Optional[Type]:
        """Get a module by name.
        
        Args:
            name: Module name
            
        Returns:
            Module class or None if not found
        """
        return self.modules.get(name)
    
    def get_module_dependencies(self, name: str) -> List[str]:
        """Get module dependencies.
        
        Args:
            name: Module name
            
        Returns:
            List of dependency module names
        """
        return self.dependencies.get(name, [])
    
    def get_all_modules(self) -> Dict[str, Type]:
        """Get all registered modules.
        
        Returns:
            Dictionary of module classes by name
        """
        return self.modules.copy()
    
    def resolve_dependencies(self, module_name: str) -> List[str]:
        """Resolve module dependencies in order.
        
        Args:
            module_name: Module name
            
        Returns:
            List of module names in dependency order
        """
        if module_name not in self.modules:
            raise ValueError(f"Module not found: {module_name}")
            
        visited = set()
        ordered = []
        
        def visit(name):
            if name in visited:
                return
            visited.add(name)
            
            for dep in self.dependencies.get(name, []):
                if dep not in self.modules:
                    raise ValueError(f"Dependency not found: {dep} (required by {name})")
                visit(dep)
                
            ordered.append(name)
            
        visit(module_name)
        return ordered


class LLMIntegrationManager:
    """Main manager for LLM integration components."""
    
    def __init__(self):
        """Initialize the integration manager."""
        self.version_manager = VersionManager()
        self.plugin_manager = PluginManager()
        self.module_registry = ModuleRegistry()
        
        # Register core modules
        self._register_core_modules()
        
    def _register_core_modules(self):
        """Register core modules for the integration."""
        # This would be implemented to register the built-in modules
        pass
        
    def initialize(self):
        """Initialize the integration components."""
        # Discover plugins
        self.plugin_manager.discover_plugins()
        
        # Log version information
        logger.info(f"Initializing LLM Integration v{self.version_manager.get_version()}")
        
    def get_analyzer_plugins(self):
        """Get all analyzer plugins."""
        return self.plugin_manager.load_plugins_by_type("analyzer")
    
    def get_integration_plugins(self):
        """Get all LLM integration plugins."""
        return self.plugin_manager.load_plugins_by_type("llm_integration")
    
    def get_visualization_plugins(self):
        """Get all visualization plugins."""
        return self.plugin_manager.load_plugins_by_type("visualization")
    
    def create_plugin_template(self, plugin_type, plugin_name, output_dir=None):
        """Create a template for a new plugin.
        
        Args:
            plugin_type: Type of plugin
            plugin_name: Name of the plugin
            output_dir: Output directory (defaults to default plugin directory)
            
        Returns:
            Path to the created plugin file
        """
        if not output_dir:
            output_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "plugins"
            )
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert name to snake_case for filename
        filename = plugin_name.lower().replace(' ', '_').replace('-', '_')
        if not filename.endswith('.py'):
            filename += '.py'
            
        file_path = os.path.join(output_dir, filename)
        
        # Create plugin template
        template = f'''"""
{plugin_name} - A {plugin_type} plugin for iLEAPP LLM integration.
"""

class {plugin_name.replace(' ', '')}Plugin:
    """
    {plugin_name} plugin implementation.
    """
    
    PLUGIN_NAME = "{plugin_name}"
    PLUGIN_TYPE = "{plugin_type}"
    PLUGIN_DESCRIPTION = "A {plugin_type} plugin for iLEAPP LLM integration"
    PLUGIN_VERSION = "0.1.0"
    
    def __init__(self):
        """Initialize the plugin."""
        pass
    
    # Add your plugin methods here
    
'''
        
        with open(file_path, 'w') as f:
            f.write(template)
            
        logger.info(f"Created plugin template: {file_path}")
        return file_path


# Base class for plugins
class BasePlugin:
    """Base class for all plugins."""
    
    PLUGIN_NAME = "Base Plugin"
    PLUGIN_TYPE = "base"
    PLUGIN_DESCRIPTION = "Base plugin class"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the plugin."""
        self.logger = logging.getLogger(f"plugin.{self.PLUGIN_TYPE}.{self.PLUGIN_NAME}")
        
    def get_info(self):
        """Get plugin information."""
        return {
            "name": self.PLUGIN_NAME,
            "type": self.PLUGIN_TYPE,
            "description": self.PLUGIN_DESCRIPTION,
            "version": self.PLUGIN_VERSION
        }


# Example usage
if __name__ == "__main__":
    # Initialize the integration manager
    manager = LLMIntegrationManager()
    manager.initialize()
    
    # Create a plugin template
    template_path = manager.create_plugin_template(
        "analyzer", 
        "Location History Analyzer"
    )
    print(f"Created template at: {template_path}")
    
    # Update version
    new_version = manager.version_manager.update_version("minor")
    print(f"Updated version to: {new_version}")
