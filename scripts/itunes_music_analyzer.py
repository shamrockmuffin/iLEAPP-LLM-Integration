import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.llm_analyzer import LLMAnalyzer
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

class iTunesMusicAnalyzer(LLMAnalyzer):
    """
    LLM-enhanced analyzer for iTunes music history artifacts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the iTunes music analyzer.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
        """
        super().__init__(api_key)
    
    def analyze_music_history(self, 
                             music_data: Union[List[Dict], pd.DataFrame], 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze iTunes music history data using LLM.
        
        Args:
            music_data: Music history data
            context: Additional context for the analysis
            
        Returns:
            Dictionary containing analysis results
        """
        return self.analyze_artifact(music_data, "itunes_music", context)
    
    def analyze_genre_distribution(self, 
                                 music_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze the distribution of music genres.
        
        Args:
            music_data: Music history data
            
        Returns:
            Dictionary containing genre distribution analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(music_data, pd.DataFrame):
            data = music_data.to_dict(orient="records")
        else:
            data = music_data
        
        # Create prompt for genre distribution analysis
        prompt = """
        Analyze the distribution of music genres in the provided iTunes music history data.
        Identify:
        1. Most common genres
        2. Genre preferences by time of day or day of week
        3. Changes in genre preferences over time
        4. Correlations between genres
        
        Format your response as a JSON object with the following structure:
        {
            "genre_distribution": [{"genre": "genre_name", "count": count, "percentage": percent}],
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "top_genres": ["genre1", "genre2"]}],
                "by_day": [{"day": "day_name", "top_genres": ["genre1", "genre2"]}]
            },
            "trend_analysis": [{"period": "time_period", "trending_genres": ["genre1", "genre2"]}],
            "genre_correlations": [{"genre1": "genre_name", "genre2": "genre_name", "correlation": correlation}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"music_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing genre distribution: {e}")
            return {}
    
    def analyze_artist_preferences(self, 
                                 music_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze artist preferences.
        
        Args:
            music_data: Music history data
            
        Returns:
            Dictionary containing artist preference analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(music_data, pd.DataFrame):
            data = music_data.to_dict(orient="records")
        else:
            data = music_data
        
        # Create prompt for artist preference analysis
        prompt = """
        Analyze artist preferences in the provided iTunes music history data.
        Identify:
        1. Most frequently played artists
        2. Artist preferences by time
        3. Changes in artist preferences over time
        4. Artist groupings or clusters
        
        Format your response as a JSON object with the following structure:
        {
            "top_artists": [{"artist": "artist_name", "play_count": count, "percentage": percent}],
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "top_artists": ["artist1", "artist2"]}],
                "by_day": [{"day": "day_name", "top_artists": ["artist1", "artist2"]}]
            },
            "trend_analysis": [{"period": "time_period", "trending_artists": ["artist1", "artist2"]}],
            "artist_clusters": [{"cluster_name": "description", "artists": ["artist1", "artist2"]}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"music_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-haiku",
            temperature=0.2
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing artist preferences: {e}")
            return {}
    
    def analyze_listening_patterns(self, 
                                 music_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze listening patterns.
        
        Args:
            music_data: Music history data
            
        Returns:
            Dictionary containing listening pattern analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(music_data, pd.DataFrame):
            data = music_data.to_dict(orient="records")
        else:
            data = music_data
        
        # Create prompt for listening pattern analysis
        prompt = """
        Analyze listening patterns in the provided iTunes music history data.
        Identify:
        1. Listening frequency by time of day and day of week
        2. Duration of listening sessions
        3. Patterns in song selection (e.g., playlists, shuffling)
        4. Repeat listening behaviors
        
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
            "selection_patterns": {"description": "pattern description", "evidence": "explanation"},
            "repeat_behaviors": [{"track": "track_name", "play_count": count, "pattern": "description"}]
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"music_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-sonnet",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing listening patterns: {e}")
            return {}
    
    def analyze_mood_patterns(self, 
                            music_data: Union[List[Dict], pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze mood patterns based on music choices.
        
        Args:
            music_data: Music history data
            
        Returns:
            Dictionary containing mood pattern analysis
        """
        # Convert DataFrame to list of dicts if needed
        if isinstance(music_data, pd.DataFrame):
            data = music_data.to_dict(orient="records")
        else:
            data = music_data
        
        # Create prompt for mood pattern analysis
        prompt = """
        Analyze mood patterns based on music choices in the provided iTunes music history data.
        Consider:
        1. Emotional characteristics of genres and songs
        2. Changes in mood based on music selection over time
        3. Correlations between mood and time of day/day of week
        4. Potential emotional states based on music choices
        
        Format your response as a JSON object with the following structure:
        {
            "mood_distribution": [{"mood": "mood_name", "percentage": percent, "evidence": "explanation"}],
            "temporal_patterns": {
                "by_hour": [{"hour": hour, "dominant_mood": "mood_name"}],
                "by_day": [{"day": "day_name", "dominant_mood": "mood_name"}]
            },
            "mood_transitions": [{"from": "mood1", "to": "mood2", "frequency": count}],
            "emotional_analysis": {"description": "analysis description", "evidence": "explanation"}
        }
        """
        
        response = self.client.analyze_structured_data(
            data={"music_history": data[:200]},
            instructions=prompt,
            model="anthropic/claude-3-opus",
            temperature=0.3
        )
        
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)
            return results
        except (KeyError, json.JSONDecodeError) as e:
            logfunc(f"Error analyzing mood patterns: {e}")
            return {}
    
    def generate_music_report(self, 
                            analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report from music history analysis results.
        
        Args:
            analysis_results: Results from various analysis methods
            
        Returns:
            HTML report content
        """
        template = """
        Create a comprehensive digital forensics report based on the iTunes music history analysis results.
        The report should include:
        
        1. Executive Summary
           - Brief overview of the analysis
           - Key findings and their significance
        
        2. Music Preferences
           - Genre distribution
           - Artist preferences
           - Favorite tracks
        
        3. Listening Patterns
           - Temporal patterns (time of day, day of week)
           - Listening session characteristics
           - Changes in preferences over time
        
        4. Mood Analysis
           - Emotional patterns based on music choices
           - Correlations between mood and time
        
        5. Points of Interest
           - Unusual patterns or behaviors
           - Potentially significant music choices
        
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
            logfunc(f"Error generating music report: {e}")
            return f"<h1>Error Generating Report</h1><p>Error: {e}</p>"
