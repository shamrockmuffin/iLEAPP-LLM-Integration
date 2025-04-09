import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.llm_analyzer import LLMAnalyzer
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class AppendicesGenerator(LLMAnalyzer):
    """
    LLM-enhanced generator for comprehensive appendices and reference materials.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the appendices generator.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        super().__init__(api_key)
    
    def generate_all_appendices(self, 
                              artifact_data: Dict[str, Any],
                              output_dir: str) -> Dict[str, str]:
        """
        Generate all types of appendices.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            output_dir: Directory to save appendices
            
        Returns:
            Dictionary mapping appendix names to file paths
        """
        appendix_files = {}
        
        # Generate technical appendices
        tech_appendices = self.generate_technical_appendices(artifact_data)
        tech_file = os.path.join(output_dir, "technical_appendices.html")
        with open(tech_file, 'w', encoding='utf-8') as f:
            f.write(tech_appendices)
        appendix_files["technical"] = tech_file
        
        # Generate timeline appendices
        timeline_appendices = self.generate_timeline_appendices(artifact_data)
        timeline_file = os.path.join(output_dir, "timeline_appendices.html")
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write(timeline_appendices)
        appendix_files["timeline"] = timeline_file
        
        # Generate statistical appendices
        statistical_appendices = self.generate_statistical_appendices(artifact_data)
        statistical_file = os.path.join(output_dir, "statistical_appendices.html")
        with open(statistical_file, 'w', encoding='utf-8') as f:
            f.write(statistical_appendices)
        appendix_files["statistical"] = statistical_file
        
        # Generate reference appendices
        reference_appendices = self.generate_reference_appendices(artifact_data)
        reference_file = os.path.join(output_dir, "reference_appendices.html")
        with open(reference_file, 'w', encoding='utf-8') as f:
            f.write(reference_appendices)
        appendix_files["reference"] = reference_file
        
        return appendix_files
    
    def generate_technical_appendices(self, 
                                    artifact_data: Dict[str, Any]) -> str:
        """
        Generate technical appendices with database structure, table schemas, and artifact types.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            
        Returns:
            HTML content for technical appendices
        """
        # Create prompt for technical appendices
        prompt = """
        Generate comprehensive technical appendices for iOS forensic data.
        Include:
        1. Database structure overview
        2. Table schemas and relationships
        3. Artifact types and their significance
        4. Data formats and encoding
        5. Technical glossary
        
        Format the appendices in HTML with appropriate headings, tables, and styling.
        Make it detailed, comprehensive, and suitable for technical reference.
        """
        
        # Prepare data for LLM
        technical_data = {
            "database_info": artifact_data.get("database_info", {}),
            "table_schemas": artifact_data.get("table_schemas", {}),
            "artifact_types": artifact_data.get("artifact_types", {})
        }
        
        response = self.client.generate_report(
            data=technical_data,
            template=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating technical appendices: {e}")
            return f"<h1>Error Generating Technical Appendices</h1><p>Error: {e}</p>"
    
    def generate_timeline_appendices(self, 
                                   artifact_data: Dict[str, Any]) -> str:
        """
        Generate timeline appendices with chronological sequences of events.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            
        Returns:
            HTML content for timeline appendices
        """
        # Create prompt for timeline appendices
        prompt = """
        Generate comprehensive timeline appendices for iOS forensic data.
        Include:
        1. Master timeline of all events
        2. Timeline by artifact type
        3. Key event sequences
        4. Temporal patterns and anomalies
        5. Timeline visualization guidance
        
        Format the appendices in HTML with appropriate headings, tables, and styling.
        Make it detailed, chronological, and suitable for investigative reference.
        """
        
        # Prepare data for LLM
        timeline_data = {
            "events": artifact_data.get("events", []),
            "artifact_timelines": artifact_data.get("artifact_timelines", {}),
            "key_sequences": artifact_data.get("key_sequences", [])
        }
        
        response = self.client.generate_report(
            data=timeline_data,
            template=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating timeline appendices: {e}")
            return f"<h1>Error Generating Timeline Appendices</h1><p>Error: {e}</p>"
    
    def generate_statistical_appendices(self, 
                                      artifact_data: Dict[str, Any]) -> str:
        """
        Generate statistical appendices with detailed data summaries and distributions.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            
        Returns:
            HTML content for statistical appendices
        """
        # Create prompt for statistical appendices
        prompt = """
        Generate comprehensive statistical appendices for iOS forensic data.
        Include:
        1. Data volume statistics by artifact type
        2. Frequency distributions
        3. Temporal distributions
        4. Correlation analyses
        5. Statistical anomalies
        
        Format the appendices in HTML with appropriate headings, tables, charts, and styling.
        Make it detailed, data-driven, and suitable for analytical reference.
        """
        
        # Prepare data for LLM
        statistical_data = {
            "volume_stats": artifact_data.get("volume_stats", {}),
            "distributions": artifact_data.get("distributions", {}),
            "correlations": artifact_data.get("correlations", {})
        }
        
        response = self.client.generate_report(
            data=statistical_data,
            template=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating statistical appendices: {e}")
            return f"<h1>Error Generating Statistical Appendices</h1><p>Error: {e}</p>"
    
    def generate_reference_appendices(self, 
                                    artifact_data: Dict[str, Any]) -> str:
        """
        Generate reference appendices with lookup tables and explanations for forensic artifacts.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            
        Returns:
            HTML content for reference appendices
        """
        # Create prompt for reference appendices
        prompt = """
        Generate comprehensive reference appendices for iOS forensic data.
        Include:
        1. iOS artifact reference guide
        2. Common data formats and their interpretation
        3. Forensic significance of different artifacts
        4. Cross-reference tables
        5. Investigative context for different data types
        
        Format the appendices in HTML with appropriate headings, tables, and styling.
        Make it detailed, comprehensive, and suitable for investigative reference.
        """
        
        # Prepare data for LLM
        reference_data = {
            "artifact_reference": artifact_data.get("artifact_reference", {}),
            "data_formats": artifact_data.get("data_formats", {}),
            "forensic_significance": artifact_data.get("forensic_significance", {})
        }
        
        response = self.client.generate_report(
            data=reference_data,
            template=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating reference appendices: {e}")
            return f"<h1>Error Generating Reference Appendices</h1><p>Error: {e}</p>"
    
    def generate_case_summary(self, 
                            artifact_data: Dict[str, Any],
                            analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive case summary based on all artifacts and analysis results.
        
        Args:
            artifact_data: Dictionary containing all artifact data
            analysis_results: Results from various analysis methods
            
        Returns:
            HTML content for case summary
        """
        # Create prompt for case summary
        prompt = """
        Generate a comprehensive case summary based on the iOS forensic data and analysis results.
        The summary should include:
        
        1. Executive Summary
           - Brief overview of the case
           - Key findings and their significance
        
        2. Data Overview
           - Types and volume of data analyzed
           - Time period covered
           - Data sources and their reliability
        
        3. Key Findings
           - Most significant discoveries
           - Patterns and behaviors identified
           - Timeline of important events
        
        4. Analysis by Data Type
           - Communications analysis
           - App usage analysis
           - Web browsing analysis
           - Media consumption analysis
        
        5. Conclusions
           - Overall assessment
           - Confidence levels in findings
           - Potential alternative interpretations
        
        6. Recommendations
           - Suggestions for further investigation
           - Specific areas to focus on
        
        Format the summary in HTML with appropriate headings, paragraphs, and styling.
        Make it detailed, comprehensive, and suitable for investigative purposes.
        """
        
        # Combine data for LLM
        combined_data = {
            "artifact_data_summary": {k: "Data available" for k in artifact_data.keys()},
            "analysis_results": analysis_results
        }
        
        response = self.client.generate_report(
            data=combined_data,
            template=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating case summary: {e}")
            return f"<h1>Error Generating Case Summary</h1><p>Error: {e}</p>"
