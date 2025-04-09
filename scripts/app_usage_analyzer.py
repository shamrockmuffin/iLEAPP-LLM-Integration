import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.llm_analyzer import LLMAnalyzer
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class AppUsageAnalyzer(LLMAnalyzer):
    """
    LLM-enhanced analyzer for app usage artifacts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the app usage analyzer.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        super().__init__(api_key)
    
    def analyze_app_usage(self, 
                         usage_data: Union[List[Dict], pd.DataFrame], 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze app usage data using LLM.
        
        Args:
            usage_data: App usage data
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        return self.analyze_artifact(usage_data, "app_usage", context)
    
    def identify_usage_patterns(self, 
                              usage_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Identify patterns in app usage.
        
        Args:
            usage_data: App usage data
            
        Returns:
            Dictionary containing usage pattern analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(usage_data, pd.DataFrame):
            data = usage_data.to_dict(orient="records")
        else:
            data = usage_data
        
        # Create prompt for pattern identification
        prompt = """
        Identify patterns in the provided app usage data.
        Analyze:
        1. Most frequently used apps
        2. Usage patterns by time of day and day of week
        3. Sequential patterns (which apps are used in sequence)
        4. Duration patterns (how long apps are used)
        5. Changes in usage patterns over time
        
        Format your response as a JSON object with the following structure:
        {
            "frequent_apps": [{"app": "app_name", "frequency": count, "percentage": percent}],
            "time_patterns": {
                "by_hour": [{"hour": hour, "top_apps": ["app1", "app2"]}],
                "by_day": [{"day": "day_name", "top_apps": ["app1", "app2"]}]
            },
            "sequential_patterns": [{"sequence": ["app1", "app2"], "frequency": count}],
            "duration_patterns": [{"app": "app_name", "avg_duration": minutes, "pattern": "description"}],
            "trend_analysis": {"increasing": ["app1"], "decreasing": ["app2"], "stable": ["app3"]}
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"app_usage": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error identifying app usage patterns: {e}")
            return {}
    
    def analyze_screen_time(self, 
                          usage_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze screen time patterns.
        
        Args:
            usage_data: App usage data
            
        Returns:
            Dictionary containing screen time analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(usage_data, pd.DataFrame):
            data = usage_data.to_dict(orient="records")
        else:
            data = usage_data
        
        # Create prompt for screen time analysis
        prompt = """
        Analyze screen time patterns in the provided app usage data.
        Calculate:
        1. Total screen time per day
        2. Screen time distribution by app category
        3. Peak usage times
        4. Patterns in screen time duration
        5. Potential screen time anomalies
        
        Format your response as a JSON object with the following structure:
        {
            "daily_screen_time": [{"date": "YYYY-MM-DD", "total_minutes": minutes, "top_apps": ["app1", "app2"]}],
            "category_distribution": [{"category": "category_name", "minutes": minutes, "percentage": percent}],
            "peak_times": [{"time_range": "HH:MM-HH:MM", "average_minutes": minutes}],
            "duration_patterns": {"description": "pattern description", "details": [...]},
            "anomalies": [{"date": "YYYY-MM-DD", "description": "anomaly description", "significance": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"app_usage": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing screen time: {e}")
            return {}
    
    def analyze_app_transitions(self, 
                              usage_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze transitions between apps.
        
        Args:
            usage_data: App usage data
            
        Returns:
            Dictionary containing app transition analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(usage_data, pd.DataFrame):
            data = usage_data.to_dict(orient="records")
        else:
            data = usage_data
        
        # Create prompt for app transition analysis
        prompt = """
        Analyze transitions between apps in the provided usage data.
        Identify:
        1. Common app sequences
        2. Transition probabilities between apps
        3. App usage workflows
        4. Unusual transition patterns
        
        Format your response as a JSON object with the following structure:
        {
            "common_sequences": [{"sequence": ["app1", "app2", "app3"], "frequency": count}],
            "transition_matrix": [{"from": "app1", "to": "app2", "probability": probability}],
            "workflows": [{"name": "workflow_name", "apps": ["app1", "app2"], "description": "description"}],
            "unusual_transitions": [{"from": "app1", "to": "app2", "reason": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"app_usage": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing app transitions: {e}")
            return {}
    
    def create_behavioral_profile(self, 
                                usage_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Create a behavioral profile based on app usage.
        
        Args:
            usage_data: App usage data
            
        Returns:
            Dictionary containing behavioral profile
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(usage_data, pd.DataFrame):
            data = usage_data.to_dict(orient="records")
        else:
            data = usage_data
        
        # Create prompt for behavioral profiling
        prompt = """
        Create a behavioral profile based on the provided app usage data.
        Consider:
        1. User interests based on app categories
        2. Daily routines and habits
        3. Productivity vs. entertainment patterns
        4. Social connectivity patterns
        5. Changes in behavior over time
        
        Format your response as a JSON object with the following structure:
        {
            "interests": [{"category": "category_name", "confidence": confidence, "evidence": "explanation"}],
            "routines": [{"time": "time_description", "activity": "activity_description", "confidence": confidence}],
            "productivity": {"assessment": "assessment_description", "evidence": "explanation"},
            "social_connectivity": {"assessment": "assessment_description", "evidence": "explanation"},
            "behavioral_changes": [{"period": "time_period", "change": "change_description", "significance": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"app_usage": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error creating behavioral profile: {e}")
            return {}
    
    def generate_app_usage_report(self, 
                                analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report from app usage analysis results.
        
        Args:
            analysis_results: Results from various analysis methods
            
        Returns:
            HTML report content
        """
        template = """
        Create a comprehensive digital forensics report based on the app usage analysis results.
        The report should include:
        
        1. Executive Summary
           - Brief overview of the analysis
           - Key findings and their significance
        
        2. App Usage Patterns
           - Most frequently used apps
           - Usage patterns by time
           - App category distribution
        
        3. Screen Time Analysis
           - Overall screen time patterns
           - Peak usage times
           - Screen time by app category
        
        4. Behavioral Analysis
           - User interests and habits
           - Daily routines
           - Changes in behavior over time
        
        5. Points of Interest
           - Unusual patterns or behaviors
           - Potentially significant usage patterns
        
        6. Recommendations
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
        
        try:
            content = response["choices"][0]["message"]["content"]
            return content
        except KeyError as e:
            logfunc(f"Error generating app usage report: {e}")
            return f"<h1>Error Generating Report</h1><p>Error: {e}</p>"
