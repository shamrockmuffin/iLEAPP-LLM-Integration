import os
import requests
import json
from typing import Dict, List, Any, Optional, Union

class OpenRouterClient:
    """
    Client for interacting with the OpenRouter API to access various LLM models.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            base_url: Base URL for the OpenRouter API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://ileapp-openrouter-integration.org",  # Identifies your app
            "X-Title": "iLEAPP OpenRouter Integration",  # Sets your app's title
            "Content-Type": "application/json"
        }
    
    def analyze_text(self, 
                    text: str, 
                    model: str = "openai/gpt-4o", 
                    temperature: float = 0.7,
                    max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Analyze text using the specified LLM model.
        
        Args:
            text: Text to analyze
            model: Model to use for analysis
            temperature: Temperature parameter for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary containing the model's response
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a digital forensics expert analyzing iOS artifacts."},
                {"role": "user", "content": text}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error from OpenRouter API: {response.status_code} - {response.text}")
    
    def analyze_structured_data(self, 
                               data: Dict[str, Any], 
                               instructions: str,
                               model: str = "anthropic/claude-3-opus",
                               temperature: float = 0.2) -> Dict[str, Any]:
        """
        Analyze structured data using the specified LLM model.
        
        Args:
            data: Structured data to analyze
            instructions: Instructions for the analysis
            model: Model to use for analysis
            temperature: Temperature parameter for generation
            
        Returns:
            Dictionary containing the model's response
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        # Convert data to a formatted string
        data_str = json.dumps(data, indent=2)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a digital forensics expert analyzing iOS artifacts. Provide detailed analysis of the data."},
                {"role": "user", "content": f"{instructions}\n\nHere is the data to analyze:\n```json\n{data_str}\n```"}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error from OpenRouter API: {response.status_code} - {response.text}")
    
    def generate_report(self, 
                       data: Dict[str, Any], 
                       template: str,
                       model: str = "anthropic/claude-3-sonnet",
                       temperature: float = 0.5) -> Dict[str, Any]:
        """
        Generate a report based on the provided data and template.
        
        Args:
            data: Data to include in the report
            template: Template for the report
            model: Model to use for report generation
            temperature: Temperature parameter for generation
            
        Returns:
            Dictionary containing the model's response with the generated report
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        # Convert data to a formatted string
        data_str = json.dumps(data, indent=2)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a digital forensics expert creating detailed reports from iOS artifacts."},
                {"role": "user", "content": f"{template}\n\nHere is the data to include in the report:\n```json\n{data_str}\n```"}
            ],
            "temperature": temperature
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error from OpenRouter API: {response.status_code} - {response.text}")
