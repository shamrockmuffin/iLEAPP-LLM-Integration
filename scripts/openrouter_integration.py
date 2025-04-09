import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from scripts.openrouter_client import OpenRouterClient
from scripts.message_analyzer import MessageAnalyzer
from scripts.app_usage_analyzer import AppUsageAnalyzer
from scripts.itunes_music_analyzer import iTunesMusicAnalyzer
from scripts.chrome_history_analyzer import ChromeHistoryAnalyzer
from scripts.appendices_generator import AppendicesGenerator

class OpenRouterIntegration:
    """
    Main integration class for connecting iLEAPP with OpenRouter API.
    This class orchestrates the analysis of different artifact types using LLM capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None, log_level: int = logging.INFO):
        """
        Initialize the OpenRouter integration.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
            log_level: Logging level
        """
        # Set up logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("openrouter_integration.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("OpenRouterIntegration")
        
        # Get API key
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if api_key is None:
                self.logger.error("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set")
                raise ValueError("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set")
        
        self.api_key = api_key
        
        # Initialize analyzers
        self.message_analyzer = MessageAnalyzer(api_key)
        self.app_usage_analyzer = AppUsageAnalyzer(api_key)
        self.itunes_music_analyzer = iTunesMusicAnalyzer(api_key)
        self.chrome_history_analyzer = ChromeHistoryAnalyzer(api_key)
        self.appendices_generator = AppendicesGenerator(api_key)
        
        # Initialize direct client for custom queries
        self.client = OpenRouterClient(api_key)
        
        self.logger.info("OpenRouter integration initialized successfully")
    
    def analyze_artifact(self, 
                        artifact_type: str, 
                        artifact_data: Union[List[Dict], Dict[str, Any]],
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze an artifact using the appropriate analyzer.
        
        Args:
            artifact_type: Type of artifact (e.g., "sms", "app_usage", "itunes_music", "chrome_history")
            artifact_data: Data from the artifact
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info(f"Analyzing artifact of type: {artifact_type}")
        
        try:
            if artifact_type == "sms":
                return self.message_analyzer.analyze_messages(artifact_data, context)
            elif artifact_type == "app_usage":
                return self.app_usage_analyzer.analyze_app_usage(artifact_data, context)
            elif artifact_type == "itunes_music":
                return self.itunes_music_analyzer.analyze_music_history(artifact_data, context)
            elif artifact_type == "chrome_history":
                return self.chrome_history_analyzer.analyze_browser_history(artifact_data, context)
            else:
                self.logger.warning(f"Unknown artifact type: {artifact_type}. Using generic analysis.")
                # Use the base analyzer from any of the specialized analyzers
                return self.message_analyzer.analyze_artifact(artifact_data, artifact_type, context)
        except Exception as e:
            self.logger.error(f"Error analyzing artifact: {e}")
            return {"error": str(e)}
    
    def generate_report(self, 
                       artifact_type: str, 
                       analysis_results: Dict[str, Any]) -> str:
        """
        Generate a report for an artifact based on analysis results.
        
        Args:
            artifact_type: Type of artifact
            analysis_results: Results from analyze_artifact
            
        Returns:
            HTML report content
        """
        self.logger.info(f"Generating report for artifact type: {artifact_type}")
        
        try:
            if artifact_type == "sms":
                return self.message_analyzer.generate_message_report(analysis_results)
            elif artifact_type == "app_usage":
                return self.app_usage_analyzer.generate_app_usage_report(analysis_results)
            elif artifact_type == "itunes_music":
                return self.itunes_music_analyzer.generate_music_report(analysis_results)
            elif artifact_type == "chrome_history":
                return self.chrome_history_analyzer.generate_browser_report(analysis_results)
            else:
                self.logger.warning(f"Unknown artifact type for report generation: {artifact_type}. Using generic template.")
                # Create a generic report template
                template = f"""
                Create a comprehensive digital forensics report for {artifact_type} artifact.
                The report should include:
                
                1. Executive Summary
                   - Brief overview of the analysis
                   - Key findings and their significance
                
                2. Analysis Details
                   - Detailed findings from the analysis
                   - Patterns and behaviors identified
                   - Significant data points
                
                3. Recommendations
                   - Suggestions for further investigation
                   - Specific areas to focus on
                
                Format the report in HTML with appropriate headings, paragraphs, and styling.
                """
                
                response = self.client.generate_report(
                    data=analysis_results,
                    template=template,
                    model="anthropic/claude-3-sonnet",
                    temperature=0.4
                )
                
                content = response["choices"][0]["message"]["content"]
                return content
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return f"<h1>Error Generating Report</h1><p>Error: {e}</p>"
    
    def generate_appendices(self, 
                          all_artifact_data: Dict[str, Any],
                          output_dir: str) -> Dict[str, str]:
        """
        Generate appendices for all artifacts.
        
        Args:
            all_artifact_data: Dictionary containing all artifact data
            output_dir: Directory to save appendices
            
        Returns:
            Dictionary mapping appendix names to file paths
        """
        self.logger.info("Generating appendices")
        
        try:
            return self.appendices_generator.generate_all_appendices(all_artifact_data, output_dir)
        except Exception as e:
            self.logger.error(f"Error generating appendices: {e}")
            return {"error": str(e)}
    
    def generate_case_summary(self, 
                            all_artifact_data: Dict[str, Any],
                            all_analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive case summary based on all artifacts and analysis results.
        
        Args:
            all_artifact_data: Dictionary containing all artifact data
            all_analysis_results: Dictionary containing all analysis results
            
        Returns:
            HTML content for case summary
        """
        self.logger.info("Generating case summary")
        
        try:
            return self.appendices_generator.generate_case_summary(all_artifact_data, all_analysis_results)
        except Exception as e:
            self.logger.error(f"Error generating case summary: {e}")
            return f"<h1>Error Generating Case Summary</h1><p>Error: {e}</p>"
    
    def custom_query(self, 
                   query: str, 
                   data: Optional[Dict[str, Any]] = None,
                   model: str = "anthropic/claude-3-sonnet") -> Dict[str, Any]:
        """
        Send a custom query to the OpenRouter API.
        
        Args:
            query: Query text
            data: Optional data to include with the query
            model: Model to use for the query
            
        Returns:
            Dictionary containing the model's response
        """
        self.logger.info(f"Sending custom query to model: {model}")
        
        try:
            if data:
                data_str = json.dumps(data, indent=2)
                full_query = f"{query}\n\nHere is the data:\n```json\n{data_str}\n```"
            else:
                full_query = query
            
            response = self.client.analyze_text(
                text=full_query,
                model=model,
                temperature=0.7
            )
            
            return response
        except Exception as e:
            self.logger.error(f"Error sending custom query: {e}")
            return {"error": str(e)}
