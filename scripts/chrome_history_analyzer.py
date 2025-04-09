import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.llm_analyzer import LLMAnalyzer
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class ChromeHistoryAnalyzer(LLMAnalyzer):
    """
    LLM-enhanced analyzer for Chrome browser history artifacts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Chrome history analyzer.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        super().__init__(api_key)
    
    def analyze_browser_history(self, 
                              history_data: Union[List[Dict], pd.DataFrame], 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze Chrome browser history data using LLM.
        
        Args:
            history_data: Browser history data
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        return self.analyze_artifact(history_data, "chrome_history", context)
    
    def analyze_domain_distribution(self, 
                                  history_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze the distribution of domains visited.
        
        Args:
            history_data: Browser history data
            
        Returns:
            Dictionary containing domain distribution analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(history_data, pd.DataFrame):
            data = history_data.to_dict(orient="records")
        else:
            data = history_data
        
        # Create prompt for domain distribution analysis
        prompt = """
        Analyze the distribution of domains visited in the provided Chrome browser history data.
        Identify:
        1. Most frequently visited domains
        2. Domain categories (e.g., social media, news, shopping)
        3. Temporal patterns in domain visits
        4. Potentially significant or unusual domains
        
        Format your response as a JSON object with the following structure:
        {
            "domain_distribution": [{"domain": "domain_name", "visit_count": count, "percentage": percent}],
            "domain_categories": [{"category": "category_name", "domains": ["domain1", "domain2"], "percentage": percent}],
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "top_domains": ["domain1", "domain2"]}],
                "by_day": [{"day": "day_name", "top_domains": ["domain1", "domain2"]}]
            },
            "significant_domains": [{"domain": "domain_name", "reason": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"browser_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing domain distribution: {e}")
            return {}
    
    def analyze_search_queries(self, 
                             history_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze search queries from browser history.
        
        Args:
            history_data: Browser history data
            
        Returns:
            Dictionary containing search query analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(history_data, pd.DataFrame):
            data = history_data.to_dict(orient="records")
        else:
            data = history_data
        
        # Create prompt for search query analysis
        prompt = """
        Extract and analyze search queries from the provided Chrome browser history data.
        Identify:
        1. Common search terms and phrases
        2. Search categories and topics
        3. Temporal patterns in search behavior
        4. Potentially significant or unusual searches
        
        Format your response as a JSON object with the following structure:
        {
            "search_terms": [{"term": "search_term", "frequency": count}],
            "search_categories": [{"category": "category_name", "terms": ["term1", "term2"], "percentage": percent}],
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "common_searches": ["term1", "term2"]}],
                "by_day": [{"day": "day_name", "common_searches": ["term1", "term2"]}]
            },
            "significant_searches": [{"search": "search_query", "reason": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"browser_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing search queries: {e}")
            return {}
    
    def analyze_browsing_patterns(self, 
                                history_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze browsing patterns.
        
        Args:
            history_data: Browser history data
            
        Returns:
            Dictionary containing browsing pattern analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(history_data, pd.DataFrame):
            data = history_data.to_dict(orient="records")
        else:
            data = history_data
        
        # Create prompt for browsing pattern analysis
        prompt = """
        Analyze browsing patterns in the provided Chrome browser history data.
        Identify:
        1. Browsing frequency by time of day and day of week
        2. Duration of browsing sessions
        3. Navigation patterns (e.g., site-to-site transitions)
        4. Changes in browsing behavior over time
        
        Format your response as a JSON object with the following structure:
        {
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "frequency": count, "percentage": percent}],
                "by_day": [{"day": "day_name", "frequency": count, "percentage": percent}]
            },
            "session_analysis": {
                "average_duration": minutes,
                "session_distribution": [{"duration_range": "range", "count": count}]
            },
            "navigation_patterns": [{"from_domain": "domain1", "to_domain": "domain2", "frequency": count}],
            "behavioral_changes": [{"period": "time_period", "change": "description", "significance": "explanation"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"browser_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing browsing patterns: {e}")
            return {}
    
    def identify_interests(self, 
                         history_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Identify user interests based on browsing history.
        
        Args:
            history_data: Browser history data
            
        Returns:
            Dictionary containing interest analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(history_data, pd.DataFrame):
            data = history_data.to_dict(orient="records")
        else:
            data = history_data
        
        # Create prompt for interest identification
        prompt = """
        Identify user interests based on the provided Chrome browser history data.
        Consider:
        1. Topics and themes from visited websites
        2. Categories of content consumed
        3. Specific interests indicated by search queries
        4. Changes in interests over time
        
        Format your response as a JSON object with the following structure:
        {
            "interest_categories": [{"category": "category_name", "confidence": confidence, "evidence": "explanation"}],
            "specific_interests": [{"interest": "interest_name", "confidence": confidence, "evidence": "explanation"}],
            "temporal_trends": [{"period": "time_period", "interests": ["interest1", "interest2"]}],
            "interest_analysis": {"description": "analysis description", "significance": "explanation"}
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"browser_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error identifying interests: {e}")
            return {}
    
    def detect_suspicious_activity(self, 
                                 history_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Detect potentially suspicious browsing activity.
        
        Args:
            history_data: Browser history data
            
        Returns:
            Dictionary containing suspicious activity analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(history_data, pd.DataFrame):
            data = history_data.to_dict(orient="records")
        else:
            data = history_data
        
        # Create prompt for suspicious activity detection
        prompt = """
        Analyze the provided Chrome browser history data for potentially suspicious activity.
        Look for:
        1. Unusual browsing patterns or anomalies
        2. Potentially concerning search queries
        3. Visits to suspicious or dangerous websites
        4. Evidence of attempts to hide browsing activity
        5. Any other potentially suspicious behaviors
        
        Format your response as a JSON object with the following structure:
        {
            "suspicious_patterns": [{"pattern": "pattern_description", "evidence": "explanation", "severity": "low/medium/high"}],
            "concerning_searches": [{"search": "search_query", "reason": "explanation", "severity": "low/medium/high"}],
            "suspicious_domains": [{"domain": "domain_name", "reason": "explanation", "severity": "low/medium/high"}],
            "privacy_measures": [{"activity": "activity_description", "evidence": "explanation", "significance": "explanation"}],
            "overall_assessment": {"description": "assessment description", "recommendation": "recommendation"}
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"browser_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error detecting suspicious activity: {e}")
            return {}
    
    def generate_browser_report(self, 
                              analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report from browser history analysis results.
        
        Args:
            analysis_results: Results from various analysis methods
            
        Returns:
            HTML report content
        """
        template = """
        Create a comprehensive digital forensics report based on the Chrome browser history analysis results.
        The report should include:
        
        1. Executive Summary
           - Brief overview of the analysis
           - Key findings and their significance
        
        2. Browsing Patterns
           - Domain distribution and categories
           - Temporal patterns (time of day, day of week)
           - Session characteristics
        
        3. Search Analysis
           - Common search terms and topics
           - Search patterns and trends
           - Significant searches
        
        4. User Interests
           - Interest categories and specific interests
           - Changes in interests over time
        
        5. Points of Interest
           - Unusual patterns or behaviors
           - Potentially suspicious activity
           - Significant domains or searches
        
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
            logfunc(f"Error generating browser report: {e}")
            return f"<h1>Error Generating Report</h1><p>Error: {e}</p>"
