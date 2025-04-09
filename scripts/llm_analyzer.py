import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.openrouter_client import OpenRouterClient
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class LLMAnalyzer:
    """
    Base class for LLM-enhanced artifact analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if api_key is None:
                raise ValueError("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set")
        
        self.client = OpenRouterClient(api_key)
    
    def analyze_artifact(self, 
                        artifact_data: Union[List[Dict], pd.DataFrame], 
                        artifact_type: str,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze an artifact using LLM.
        
        Args:
            artifact_data: Data from the artifact
            artifact_type: Type of artifact (e.g., "sms", "app_usage")
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(artifact_data, pd.DataFrame):
            data = artifact_data.to_dict(orient="records")
        else:
            data = artifact_data
        
        # Create analysis prompt based on artifact type
        prompt = self._create_analysis_prompt(artifact_type, data, context)
        
        # Select appropriate model based on artifact type and data size
        model = self._select_model(artifact_type, data)
        
        # Analyze with LLM
        response = self.client.analyze_structured_data(
            data={"artifact_data": data[:100], "artifact_type": artifact_type, "context": context},
            instructions=prompt,
            model=model
        )
        
        # Extract and process results
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error processing LLM response: {e}")
            return {"error": str(e), "raw_response": response}
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from analysis results.
        
        Args:
            analysis_results: Results from analyze_artifact
            
        Returns:
            Dictionary containing insights
        """
        prompt = """
        Based on the analysis results, generate key insights that would be valuable for a digital forensics investigation.
        Focus on patterns, anomalies, and potentially significant findings.
        """
        
        response = self.client.analyze_text(
            text=f"{prompt}\n\nAnalysis Results:\n{json.dumps(analysis_results, indent=2)}",
            model="anthropic/claude-3-haiku",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return {"insights": content}
        except KeyError as e:
            logfunc(f"Error extracting insights from LLM response: {e}")
            return {"error": str(e), "raw_response": response}
    
    def _create_analysis_prompt(self, 
                               artifact_type: str, 
                               data: List[Dict], 
                               context: Optional[Dict[str, Any]]) -> str:
        """
        Create a prompt for artifact analysis based on the artifact type.
        
        Args:
            artifact_type: Type of artifact
            data: Artifact data
            context: Additional context
            
        Returns:
            Prompt string
        """
        base_prompt = "Analyze the following iOS artifact data from a digital forensics perspective."
        
        type_specific_prompts = {
            "sms": """
            This data contains SMS and iMessage communications.
            Analyze the conversations for:
            1. Key contacts and frequency of communication
            2. Temporal patterns (time of day, day of week)
            3. Sentiment analysis of messages
            4. Important topics or themes
            5. Any potentially suspicious or unusual patterns
            """,
            
            "app_usage": """
            This data contains app usage information.
            Analyze the usage patterns for:
            1. Most frequently used apps
            2. Usage patterns by time
            3. Correlations between app usage
            4. Changes in usage patterns over time
            5. Any potentially suspicious or unusual patterns
            """,
            
            "itunes_music": """
            This data contains iTunes music listening history.
            Analyze the listening patterns for:
            1. Favorite artists, genres, and tracks
            2. Listening patterns by time
            3. Changes in music preferences over time
            4. Any insights about the user's interests or activities
            """,
            
            "chrome_history": """
            This data contains Chrome browsing history.
            Analyze the browsing patterns for:
            1. Most visited domains and categories
            2. Search queries and interests
            3. Browsing patterns by time
            4. Any potentially suspicious or unusual browsing activity
            """,
        }
        
        prompt = base_prompt
        if artifact_type in type_specific_prompts:
            prompt += type_specific_prompts[artifact_type]
        else:
            prompt += f"\nThis is a {artifact_type} artifact. Provide a comprehensive analysis."
        
        if context:
            prompt += f"\n\nAdditional context: {json.dumps(context, indent=2)}"
        
        prompt += """
        Format your response as a JSON object with the following structure:
        {
            "summary": "Brief summary of the analysis",
            "key_findings": ["List of key findings"],
            "patterns": {
                "temporal": "Analysis of temporal patterns",
                "behavioral": "Analysis of behavioral patterns"
            },
            "entities": {
                "key_entities": ["List of important entities identified"],
                "relationships": ["Identified relationships between entities"]
            },
            "anomalies": ["Any anomalies or unusual patterns detected"],
            "recommendations": ["Recommendations for further investigation"]
        }
        """
        
        return prompt
    
    def _select_model(self, artifact_type: str, data: List[Dict]) -> str:
        """
        Select appropriate model based on artifact type and data size.
        
        Args:
            artifact_type: Type of artifact
            data: Artifact data
            
        Returns:
            Model identifier string
        """
        data_size = len(data)
        
        # For large datasets, use a more efficient model
        if data_size > 500:
            return "anthropic/claude-3-haiku"
        
        # For complex artifacts that need deeper analysis
        if artifact_type in ["sms", "chrome_history"]:
            return "anthropic/claude-3-sonnet"
        
        # Default to a balanced model
        return "anthropic/claude-3-haiku"
