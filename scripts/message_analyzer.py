import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.llm_analyzer import LLMAnalyzer
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class MessageAnalyzer(LLMAnalyzer):
    """
    LLM-enhanced analyzer for message artifacts (SMS, iMessage, and third-party messaging apps).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the message analyzer.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        super().__init__(api_key)
    
    def analyze_messages(self, 
                        messages: Union[List[Dict], pd.DataFrame], 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze message data using LLM.
        
        Args:
            messages: Message data
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        return self.analyze_artifact(messages, "sms", context)
    
    def extract_conversation_threads(self, 
                                    messages: Union[List[Dict], pd.DataFrame]) -> Dict[str, List[Dict]]:
        """
        Extract conversation threads from messages.
        
        Args:
            messages: Message data
            
        Returns:
            Dictionary mapping conversation IDs to lists of messages
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(messages, pd.DataFrame):
            data = messages.to_dict(orient="records")
        else:
            data = messages
        
        # Create prompt for thread extraction
        prompt = """
        Extract conversation threads from the provided messages.
        Group messages by conversation and arrange them chronologically.
        Identify the participants in each conversation.
        """
        
        response = self.client.analyze_structured_data(
            data={"messages": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results.get("threads", {})
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error extracting conversation threads: {e}")
            return {}
    
    def analyze_sentiment(self, 
                         messages: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze sentiment in messages.
        
        Args:
            messages: Message data
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(messages, pd.DataFrame):
            data = messages.to_dict(orient="records")
        else:
            data = messages
        
        # Create prompt for sentiment analysis
        prompt = """
        Analyze the sentiment in the provided messages.
        Provide an overall sentiment score for each conversation.
        Identify any significant emotional patterns or changes.
        """
        
        response = self.client.analyze_structured_data(
            data={"messages": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results.get("sentiment", {})
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing sentiment: {e}")
            return {}
    
    def extract_entities(self, 
                        messages: Union[List[Dict], pd.DataFrame]) -> Dict[str, List[Dict]]:
        """
        Extract entities (people, places, organizations) from messages.
        
        Args:
            messages: Message data
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(messages, pd.DataFrame):
            data = messages.to_dict(orient="records")
        else:
            data = messages
        
        # Create prompt for entity extraction
        prompt = """
        Extract entities from the provided messages.
        Identify people, places, organizations, dates, and other relevant entities.
        Group entities by type and provide context for each entity.
        """
        
        response = self.client.analyze_structured_data(
            data={"messages": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results.get("entities", {})
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error extracting entities: {e}")
            return {}
    
    def identify_topics(self, 
                       messages: Union[List[Dict], pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Identify main topics in messages.
        
        Args:
            messages: Message data
            
        Returns:
            List of topics with details
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(messages, pd.DataFrame):
            data = messages.to_dict(orient="records")
        else:
            data = messages
        
        # Create prompt for topic identification
        prompt = """
        Identify the main topics discussed in the provided messages.
        For each topic, provide:
        1. A descriptive name
        2. Key messages related to the topic
        3. Participants involved in the discussion
        4. Timeframe of the discussion
        """
        
        response = self.client.analyze_structured_data(
            data={"messages": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results.get("topics", [])
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error identifying topics: {e}")
            return []
    
    def detect_anomalies(self, 
                        messages: Union[List[Dict], pd.DataFrame]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in message patterns.
        
        Args:
            messages: Message data
            
        Returns:
            List of detected anomalies with details
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(messages, pd.DataFrame):
            data = messages.to_dict(orient="records")
        else:
            data = messages
        
        # Create prompt for anomaly detection
        prompt = """
        Detect any anomalies or unusual patterns in the provided messages.
        Consider:
        1. Unusual timing or frequency of messages
        2. Sudden changes in communication patterns
        3. Unusual language or content
        4. Suspicious requests or instructions
        5. Any other potentially concerning patterns
        
        For each anomaly, provide:
        1. A description of the anomaly
        2. The messages involved
        3. Why it's considered unusual
        4. Potential implications for the investigation
        """
        
        response = self.client.analyze_structured_data(
            data={"messages": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results.get("anomalies", [])
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error detecting anomalies: {e}")
            return []
    
    def generate_message_report(self, 
                              analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report from message analysis results.
        
        Args:
            analysis_results: Results from various analysis methods
            
        Returns:
            HTML report content
        """
        template = """
        Create a comprehensive digital forensics report based on the message analysis results.
        The report should include:
        
        1. Executive Summary
           - Brief overview of the analysis
           - Key findings and their significance
        
        2. Conversation Analysis
           - Overview of communication patterns
           - Key contacts and their significance
           - Temporal patterns (time of day, day of week)
        
        3. Content Analysis
           - Main topics of discussion
           - Sentiment analysis
           - Key entities mentioned (people, places, organizations)
        
        4. Anomalies and Points of Interest
           - Unusual patterns or behaviors
           - Potentially significant messages
        
        5. Recommendations
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
            logfunc(f"Error generating message report: {e}")
            return f"<h1>Error Generating Report</h1><p>Error: {e}</p>"
