#!/usr/bin/env python3
"""
Demo Showcase for iLEAPP AI Integration
This module provides interactive demonstrations of the AI-enhanced forensic capabilities.
"""

import os
import sys
import json
import argparse
import webbrowser
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add the parent directory to the path to import from scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from openrouter_client import OpenRouterClient
from llm_analyzer import LLMAnalyzer
from message_analyzer import MessageAnalyzer
from app_usage_analyzer import AppUsageAnalyzer
from chrome_history_analyzer import ChromeHistoryAnalyzer
from itunes_music_analyzer import iTunesMusicAnalyzer
from forensic_pipeline import ForensicPipeline

class DemoShowcase:
    """
    Interactive demonstration of iLEAPP AI integration capabilities
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the demo showcase
        
        Args:
            api_key (str, optional): OpenRouter API key. If not provided, will look for 
                                     OPENROUTER_API_KEY environment variable
        """
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            print("Warning: No OpenRouter API key provided. Some features will be limited.")
            print("Set your API key with: export OPENROUTER_API_KEY='your_key_here'")
        
        self.client = None
        if self.api_key:
            self.client = OpenRouterClient(api_key=self.api_key)
        
        # Create output directory for demo results
        self.output_dir = Path("./demo_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load sample data
        self.sample_data_dir = Path("./demo/sample_data")
        if not self.sample_data_dir.exists():
            self.sample_data_dir = Path("./scripts/demo/sample_data")
            if not self.sample_data_dir.exists():
                print(f"Sample data directory not found at {self.sample_data_dir}")
                print("Creating sample data directory and generating sample data...")
                self.sample_data_dir.mkdir(exist_ok=True, parents=True)
                self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample data for demonstrations"""
        # Generate sample messages data
        messages_data = [
            {"timestamp": "2025-03-01 08:15:23", "sender": "John Doe", "recipient": "Jane Smith", 
             "content": "Hey, can you send me those files we discussed yesterday?"},
            {"timestamp": "2025-03-01 08:17:45", "sender": "Jane Smith", "recipient": "John Doe", 
             "content": "Sure, I'll email them to you in a few minutes."},
            {"timestamp": "2025-03-01 09:30:12", "sender": "John Doe", "recipient": "Jane Smith", 
             "content": "Thanks! Also, don't forget about our meeting at 2pm."},
            {"timestamp": "2025-03-01 09:32:05", "sender": "Jane Smith", "recipient": "John Doe", 
             "content": "I've added it to my calendar. See you then!"},
            {"timestamp": "2025-03-01 14:05:33", "sender": "John Doe", "recipient": "Jane Smith", 
             "content": "Running a few minutes late. Start without me if needed."},
            {"timestamp": "2025-03-01 14:06:22", "sender": "Jane Smith", "recipient": "John Doe", 
             "content": "No problem, we'll wait for you."},
            {"timestamp": "2025-03-01 17:45:10", "sender": "John Doe", "recipient": "Jane Smith", 
             "content": "Great meeting today. I'll send you the summary tomorrow."},
            {"timestamp": "2025-03-01 17:50:27", "sender": "Jane Smith", "recipient": "John Doe", 
             "content": "Agreed! Looking forward to the summary. Have a good evening."},
            {"timestamp": "2025-03-02 09:15:33", "sender": "John Doe", "recipient": "Jane Smith", 
             "content": "Here's the meeting summary as promised. Let me know if you have any questions."},
            {"timestamp": "2025-03-02 09:30:45", "sender": "Jane Smith", "recipient": "John Doe", 
             "content": "Got it, thanks! I'll review it and get back to you if I have any feedback."}
        ]
        
        # Generate sample app usage data
        app_usage_data = [
            {"timestamp": "2025-03-01 07:30:15", "app_name": "Messages", "duration_seconds": 120},
            {"timestamp": "2025-03-01 07:35:45", "app_name": "Mail", "duration_seconds": 300},
            {"timestamp": "2025-03-01 08:00:12", "app_name": "Calendar", "duration_seconds": 60},
            {"timestamp": "2025-03-01 08:30:05", "app_name": "Safari", "duration_seconds": 900},
            {"timestamp": "2025-03-01 09:45:33", "app_name": "Notes", "duration_seconds": 450},
            {"timestamp": "2025-03-01 10:30:22", "app_name": "Photos", "duration_seconds": 180},
            {"timestamp": "2025-03-01 11:00:10", "app_name": "Messages", "duration_seconds": 300},
            {"timestamp": "2025-03-01 12:15:27", "app_name": "Maps", "duration_seconds": 600},
            {"timestamp": "2025-03-01 13:30:33", "app_name": "Calendar", "duration_seconds": 120},
            {"timestamp": "2025-03-01 14:00:45", "app_name": "Zoom", "duration_seconds": 3600},
            {"timestamp": "2025-03-01 15:30:15", "app_name": "Mail", "duration_seconds": 240},
            {"timestamp": "2025-03-01 16:00:45", "app_name": "Safari", "duration_seconds": 1200},
            {"timestamp": "2025-03-01 17:30:12", "app_name": "Messages", "duration_seconds": 180},
            {"timestamp": "2025-03-01 18:00:05", "app_name": "Photos", "duration_seconds": 300},
            {"timestamp": "2025-03-01 19:45:33", "app_name": "YouTube", "duration_seconds": 1800},
            {"timestamp": "2025-03-01 20:30:22", "app_name": "Netflix", "duration_seconds": 5400},
            {"timestamp": "2025-03-02 08:00:10", "app_name": "Mail", "duration_seconds": 360},
            {"timestamp": "2025-03-02 08:45:27", "app_name": "Calendar", "duration_seconds": 120},
            {"timestamp": "2025-03-02 09:00:33", "app_name": "Messages", "duration_seconds": 240},
            {"timestamp": "2025-03-02 09:30:45", "app_name": "Notes", "duration_seconds": 900}
        ]
        
        # Generate sample Chrome history data
        chrome_history_data = [
            {"timestamp": "2025-03-01 08:30:15", "url": "https://www.google.com", "title": "Google", "visit_count": 5},
            {"timestamp": "2025-03-01 08:32:45", "url": "https://mail.google.com", "title": "Gmail", "visit_count": 3},
            {"timestamp": "2025-03-01 08:45:12", "url": "https://www.nytimes.com", "title": "The New York Times", "visit_count": 1},
            {"timestamp": "2025-03-01 09:00:05", "url": "https://www.github.com", "title": "GitHub", "visit_count": 2},
            {"timestamp": "2025-03-01 09:15:33", "url": "https://www.stackoverflow.com", "title": "Stack Overflow", "visit_count": 4},
            {"timestamp": "2025-03-01 10:30:22", "url": "https://www.youtube.com", "title": "YouTube", "visit_count": 2},
            {"timestamp": "2025-03-01 11:00:10", "url": "https://www.linkedin.com", "title": "LinkedIn", "visit_count": 1},
            {"timestamp": "2025-03-01 13:15:27", "url": "https://www.amazon.com", "title": "Amazon.com", "visit_count": 3},
            {"timestamp": "2025-03-01 14:30:33", "url": "https://www.wikipedia.org", "title": "Wikipedia", "visit_count": 2},
            {"timestamp": "2025-03-01 16:00:45", "url": "https://www.reddit.com", "title": "Reddit", "visit_count": 4},
            {"timestamp": "2025-03-01 16:30:15", "url": "https://www.twitter.com", "title": "Twitter", "visit_count": 2},
            {"timestamp": "2025-03-01 17:00:45", "url": "https://www.facebook.com", "title": "Facebook", "visit_count": 1},
            {"timestamp": "2025-03-01 17:30:12", "url": "https://www.instagram.com", "title": "Instagram", "visit_count": 2},
            {"timestamp": "2025-03-01 18:00:05", "url": "https://www.netflix.com", "title": "Netflix", "visit_count": 1},
            {"timestamp": "2025-03-02 08:45:33", "url": "https://www.google.com/maps", "title": "Google Maps", "visit_count": 1}
        ]
        
        # Generate sample iTunes music history data
        itunes_music_data = [
            {"timestamp": "2025-03-01 07:45:15", "artist": "The Beatles", "song": "Hey Jude", "duration_seconds": 431},
            {"timestamp": "2025-03-01 07:52:45", "artist": "Queen", "song": "Bohemian Rhapsody", "duration_seconds": 354},
            {"timestamp": "2025-03-01 08:00:12", "artist": "Led Zeppelin", "song": "Stairway to Heaven", "duration_seconds": 482},
            {"timestamp": "2025-03-01 08:08:05", "artist": "Pink Floyd", "song": "Comfortably Numb", "duration_seconds": 382},
            {"timestamp": "2025-03-01 08:15:33", "artist": "The Rolling Stones", "song": "Paint It Black", "duration_seconds": 202},
            {"timestamp": "2025-03-01 18:30:22", "artist": "David Bowie", "song": "Space Oddity", "duration_seconds": 315},
            {"timestamp": "2025-03-01 18:35:10", "artist": "Fleetwood Mac", "song": "Dreams", "duration_seconds": 254},
            {"timestamp": "2025-03-01 18:40:27", "artist": "The Eagles", "song": "Hotel California", "duration_seconds": 391},
            {"timestamp": "2025-03-01 18:47:33", "artist": "Elton John", "song": "Rocket Man", "duration_seconds": 282},
            {"timestamp": "2025-03-01 18:52:45", "artist": "Bob Dylan", "song": "Like a Rolling Stone", "duration_seconds": 373},
            {"timestamp": "2025-03-01 19:00:15", "artist": "The Beatles", "song": "Let It Be", "duration_seconds": 243},
            {"timestamp": "2025-03-01 19:04:45", "artist": "Queen", "song": "We Will Rock You", "duration_seconds": 122},
            {"timestamp": "2025-03-01 19:07:12", "artist": "Led Zeppelin", "song": "Kashmir", "duration_seconds": 329},
            {"timestamp": "2025-03-01 19:12:05", "artist": "Pink Floyd", "song": "Wish You Were Here", "duration_seconds": 334},
            {"timestamp": "2025-03-01 19:18:33", "artist": "The Rolling Stones", "song": "Satisfaction", "duration_seconds": 224}
        ]
        
        # Save sample data to files
        with open(self.sample_data_dir / "messages.json", "w") as f:
            json.dump(messages_data, f, indent=2)
        
        with open(self.sample_data_dir / "app_usage.json", "w") as f:
            json.dump(app_usage_data, f, indent=2)
        
        with open(self.sample_data_dir / "chrome_history.json", "w") as f:
            json.dump(chrome_history_data, f, indent=2)
        
        with open(self.sample_data_dir / "itunes_music.json", "w") as f:
            json.dump(itunes_music_data, f, indent=2)
        
        print("Sample data generated successfully.")
    
    def run_message_analysis_demo(self):
        """Run a demonstration of message analysis capabilities"""
        print("\n=== Message Analysis Demo ===")
        
        # Load sample messages data
        with open(self.sample_data_dir / "messages.json", "r") as f:
            messages_data = json.load(f)
        
        # Create DataFrame for visualization
        df = pd.DataFrame(messages_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display basic statistics
        print(f"Total messages: {len(df)}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Unique senders: {df['sender'].nunique()}")
        print(f"Unique recipients: {df['recipient'].nunique()}")
        
        # Create message analyzer
        analyzer = MessageAnalyzer(client=self.client)
        
        # Analyze without AI
        print("\nBasic Analysis (without AI):")
        basic_results = {
            "message_count": len(df),
            "date_range": f"{df['timestamp'].min()} to {df['timestamp'].max()}",
            "unique_senders": df['sender'].nunique(),
            "unique_recipients": df['recipient'].nunique(),
            "avg_message_length": df['content'].str.len().mean(),
            "max_message_length": df['content'].str.len().max(),
            "min_message_length": df['content'].str.len().min()
        }
        
        for key, value in basic_results.items():
            print(f"  {key}: {value}")
        
        # Analyze with AI if available
        if self.client:
            print("\nEnhanced Analysis (with AI):")
            
            # Convert messages to format expected by analyzer
            formatted_messages = []
            for _, row in df.iterrows():
                formatted_messages.append({
                    "timestamp": row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    "sender": row['sender'],
                    "recipient": row['recipient'],
                    "content": row['content']
                })
            
            # Analyze messages
            ai_results = analyzer.analyze_conversation(formatted_messages)
            
            # Display AI analysis results
            print("  Conversation Summary:")
            print(f"    {ai_results.get('summary', 'No summary available')}")
            
            print("\n  Sentiment Analysis:")
            print(f"    {ai_results.get('sentiment_analysis', 'No sentiment analysis available')}")
            
            print("\n  Key Topics:")
            topics = ai_results.get('key_topics', [])
            if topics:
                for topic in topics:
                    print(f"    - {topic}")
            else:
                print("    No topics identified")
            
            print("\n  Relationship Assessment:")
            print(f"    {ai_results.get('relationship_assessment', 'No relationship assessment available')}")
            
            # Save AI analysis results
            output_file = self.output_dir / "message_analysis_results.json"
            with open(output_file, "w") as f:
                json.dump({
                    "basic_analysis": basic_results,
                    "ai_analysis": ai_results
                }, f, indent=2)
            
            print(f"\nResults saved to {output_file}")
        else:
            print("\nAI analysis not available. Set OPENROUTER_API_KEY to enable enhanced analysis.")
        
        # Create visualization
        self._create_message_visualization(df)
    
    def _create_message_visualization(self, df):
        """Create visualizations for message analysis"""
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 1, figsize=(10, 12))
        
        # Plot 1: Message frequency by hour
        df['hour'] = df['timestamp'].dt.hour
        hour_counts = df.groupby('hour').size()
        axs[0].bar(hour_counts.index, hour_counts.values)
        axs[0].set_title('Message Frequency by Hour')
        axs[0].set_xlabel('Hour of Day')
        axs[0].set_ylabel('Number of Messages')
        axs[0].set_xticks(range(0, 24, 2))
        
        # Plot 2: Message length distribution
        df['message_length'] = df['content'].str.len()
        axs[1].hist(df['message_length'], bins=10, alpha=0.7)
        axs[1].set_title('Message Length Distribution')
        axs[1].set_xlabel('Message Length (characters)')
        axs[1].set_ylabel('Frequency')
        
        # Save figure
        plt.tight_layout()
        output_file = self.output_dir / "message_analysis_visualization.png"
        plt.savefig(output_file)
        plt.close()
        
        print(f"Visualization saved to {output_file}")
    
    def run_app_usage_analysis_demo(self):
        """Run a demonstration of app usage analysis capabilities"""
        print("\n=== App Usage Analysis Demo ===")
        
        # Load sample app usage data
        with open(self.sample_data_dir / "app_usage.json", "r") as f:
            app_usage_data = json.load(f)
        
        # Create DataFrame for visualization
        df = pd.DataFrame(app_usage_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display basic statistics
        print(f"Total app usage records: {len(df)}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Unique apps: {df['app_name'].nunique()}")
        
        # Create app usage analyzer
        analyzer = AppUsageAnalyzer(client=self.client)
        
        # Analyze without AI
        print("\nBasic Analysis (without AI):")
        
        # Calculate total usage time by app
        app_usage_times = df.groupby('app_name')['duration_seconds'].sum().sort_values(ascending=False)
        print("  Top apps by usage time:")
        for app, duration in app_usage_times.head(5).items():
            hours = duration / 3600
            print(f"    - {app}: {hours:.2f} hours")
        
        # Calculate average session duration by app
        avg_session_duration = df.groupby('app_name')['duration_seconds'].mean().sort_values(ascending=False)
        print("\n  Average session duration by app:")
        for app, duration in avg_session_duration.head(5).items():
            minutes = duration / 60
            print(f"    - {app}: {minutes:.2f} minutes")
        
        # Analyze with AI if available
        if self.client:
            print("\nEnhanced Analysis (with AI):")
            
            # Convert app usage data to format expected by analyzer
            formatted_app_usage = []
            for _, row in df.iterrows():
                formatted_app_usage.append({
                    "timestamp": row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    "app_name": row['app_name'],
                    "duration_seconds": row['duration_seconds']
                })
            
            # Analyze app usage
            ai_results = analyzer.analyze_app_usage(formatted_app_usage)
            
            # Display AI analysis results
            print("  Usage Pattern Summary:")
            print(f"    {ai_results.get('usage_pattern_summary', 'No summary available')}")
            
            print("\n  Behavioral Insights:")
            print(f"    {ai_results.get('behavioral_insights', 'No insights available')}")
            
            print("\n  Productivity Assessment:")
            print(f"    {ai_results.get('productivity_assessment', 'No assessment available')}")
            
            print("\n  Recommendations:")
            recommendations = ai_results.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    print(f"    - {rec}")
            else:
                print("    No recommendations available")
            
            # Save AI analysis results
            output_file = self.output_dir / "app_usage_analysis_results.json"
            with open(output_file, "w") as f:
                json.dump({
                    "basic_analysis": {
                        "top_apps_by_usage": app_usage_times.head(5).to_dict(),
                        "avg_session_duration": avg_session_duration.head(5).to_dict()
                    },
                    "ai_analysis": ai_results
                }, f, indent=2)
            
            print(f"\nResults saved to {output_file}")
        else:
            print("\nAI analysis not available. Set OPENROUTER_API_KEY to enable enhanced analysis.")
        
        # Create visualization
        self._create_app_usage_visualization(df)
    
    def _create_app_usage_visualization(self, df):
        """Create visualizations for app usage analysis"""
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 1, figsize=(12, 14))
        
        # Plot 1: Total usage time by app
        app_usage = df.groupby('app_name')['duration_seconds'].sum().sort_values(ascending=False)
        app_usage_hours = app_usage / 3600  # Convert to hours
        axs[0].bar(app_usage_hours.index, app_usage_hours.values)
        axs[0].set_title('Total App Usage Time')
        axs[0].set_xlabel('App')
        axs[0].set_ylabel('Usage Time (hours)')
        axs[0].set_xticklabels(app_usage_hours.index, rotation=45, ha='right')
        
        # Plot 2: App usage by hour of day
        df['hour'] = df['timestamp'].dt.hour
        hourly_usage = df.groupby(['hour', 'app_name'])['duration_seconds'].sum().unstack().fillna(0) / 60  # Convert to minutes
        hourly_usage.plot(kind='bar', stacked=True, ax=axs[1])
        axs[1].set_title('App Usage by Hour of Day')
        axs[1].set_xlabel('Hour of Day')
        axs[1].set_ylabel('Usage Time (minutes)')
        axs[1].legend(title='App', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Save figure
        plt.tight_layout()
        output_file = self.output_dir / "app_usage_analysis_visualization.png"
        plt.savefig(output_file)
        plt.close()
        
        print(f"Visualization saved to {output_file}")
    
    def run_chrome_history_analysis_demo(self):
        """Run a demonstration of Chrome history analysis capabilities"""
        print("\n=== Chrome History Analysis Demo ===")
        
        # Load sample Chrome history data
        with open(self.sample_data_dir / "chrome_history.json", "r") as f:
            chrome_history_data = json.load(f)
        
        # Create DataFrame for visualization
        df = pd.DataFrame(chrome_history_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display basic statistics
        print(f"Total browsing records: {len(df)}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Unique websites: {df['url'].nunique()}")
        
        # Create Chrome history analyzer
        analyzer = ChromeHistoryAnalyzer(client=self.client)
        
        # Analyze without AI
        print("\nBasic Analysis (without AI):")
        
        # Most visited sites
        most_visited = df.groupby('title')['visit_count'].sum().sort_values(ascending=False)
        print("  Most visited sites:")
        for site, count in most_visited.head(5).items():
            print(f"    - {site}: {count} visits")
        
        # Extract domains from URLs
        df['domain'] = df['url'].apply(lambda x: x.split('/')[2] if len(x.split('/')) > 2 else x)
        domain_visits = df.groupby('domain')['visit_count'].sum().sort_values(ascending=False)
        print("\n  Most visited domains:")
        for domain, count in domain_visits.head(5).items():
            print(f"    - {domain}: {count} visits")
        
        # Analyze with AI if available
        if self.client:
            print("\nEnhanced Analysis (with AI):")
            
            # Convert Chrome history data to format expected by analyzer
            formatted_history = []
            for _, row in df.iterrows():
                formatted_history.append({
                    "timestamp": row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    "url": row['url'],
                    "title": row['title'],
                    "visit_count": row['visit_count']
                })
            
            # Analyze Chrome history
            ai_results = analyzer.analyze_browsing_history(formatted_history)
            
            # Display AI analysis results
            print("  Browsing Pattern Summary:")
            print(f"    {ai_results.get('browsing_pattern_summary', 'No summary available')}")
            
            print("\n  Interest Categories:")
            categories = ai_results.get('interest_categories', [])
            if categories:
                for category in categories:
                    print(f"    - {category}")
            else:
                print("    No categories identified")
            
            print("\n  Security Assessment:")
            print(f"    {ai_results.get('security_assessment', 'No assessment available')}")
            
            print("\n  Behavioral Insights:")
            print(f"    {ai_results.get('behavioral_insights', 'No insights available')}")
            
            # Save AI analysis results
            output_file = self.output_dir / "chrome_history_analysis_results.json"
            with open(output_file, "w") as f:
                json.dump({
                    "basic_analysis": {
                        "most_visited_sites": most_visited.head(5).to_dict(),
                        "most_visited_domains": domain_visits.head(5).to_dict()
                    },
                    "ai_analysis": ai_results
                }, f, indent=2)
            
            print(f"\nResults saved to {output_file}")
        else:
            print("\nAI analysis not available. Set OPENROUTER_API_KEY to enable enhanced analysis.")
        
        # Create visualization
        self._create_chrome_history_visualization(df)
    
    def _create_chrome_history_visualization(self, df):
        """Create visualizations for Chrome history analysis"""
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 1, figsize=(12, 14))
        
        # Plot 1: Most visited sites
        site_visits = df.groupby('title')['visit_count'].sum().sort_values(ascending=False).head(10)
        axs[0].bar(site_visits.index, site_visits.values)
        axs[0].set_title('Most Visited Sites')
        axs[0].set_xlabel('Site')
        axs[0].set_ylabel('Visit Count')
        axs[0].set_xticklabels(site_visits.index, rotation=45, ha='right')
        
        # Plot 2: Browsing activity by hour of day
        df['hour'] = df['timestamp'].dt.hour
        hourly_activity = df.groupby('hour')['visit_count'].sum()
        axs[1].bar(hourly_activity.index, hourly_activity.values)
        axs[1].set_title('Browsing Activity by Hour of Day')
        axs[1].set_xlabel('Hour of Day')
        axs[1].set_ylabel('Visit Count')
        axs[1].set_xticks(range(0, 24, 2))
        
        # Save figure
        plt.tight_layout()
        output_file = self.output_dir / "chrome_history_analysis_visualization.png"
        plt.savefig(output_file)
        plt.close()
        
        print(f"Visualization saved to {output_file}")
    
    def run_itunes_music_analysis_demo(self):
        """Run a demonstration of iTunes music history analysis capabilities"""
        print("\n=== iTunes Music Analysis Demo ===")
        
        # Load sample iTunes music data
        with open(self.sample_data_dir / "itunes_music.json", "r") as f:
            itunes_music_data = json.load(f)
        
        # Create DataFrame for visualization
        df = pd.DataFrame(itunes_music_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display basic statistics
        print(f"Total music records: {len(df)}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Unique artists: {df['artist'].nunique()}")
        print(f"Unique songs: {df['song'].nunique()}")
        
        # Create iTunes music analyzer
        analyzer = iTunesMusicAnalyzer(client=self.client)
        
        # Analyze without AI
        print("\nBasic Analysis (without AI):")
        
        # Most played artists
        artist_plays = df.groupby('artist').size().sort_values(ascending=False)
        print("  Most played artists:")
        for artist, count in artist_plays.head(5).items():
            print(f"    - {artist}: {count} plays")
        
        # Most played songs
        song_plays = df.groupby('song').size().sort_values(ascending=False)
        print("\n  Most played songs:")
        for song, count in song_plays.head(5).items():
            print(f"    - {song}: {count} plays")
        
        # Total listening time
        total_duration = df['duration_seconds'].sum()
        hours = total_duration / 3600
        print(f"\n  Total listening time: {hours:.2f} hours")
        
        # Analyze with AI if available
        if self.client:
            print("\nEnhanced Analysis (with AI):")
            
            # Convert iTunes music data to format expected by analyzer
            formatted_music_history = []
            for _, row in df.iterrows():
                formatted_music_history.append({
                    "timestamp": row['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                    "artist": row['artist'],
                    "song": row['song'],
                    "duration_seconds": row['duration_seconds']
                })
            
            # Analyze iTunes music history
            ai_results = analyzer.analyze_music_history(formatted_music_history)
            
            # Display AI analysis results
            print("  Music Taste Summary:")
            print(f"    {ai_results.get('music_taste_summary', 'No summary available')}")
            
            print("\n  Genre Preferences:")
            genres = ai_results.get('genre_preferences', [])
            if genres:
                for genre in genres:
                    print(f"    - {genre}")
            else:
                print("    No genre preferences identified")
            
            print("\n  Listening Pattern Insights:")
            print(f"    {ai_results.get('listening_pattern_insights', 'No insights available')}")
            
            print("\n  Music Recommendations:")
            recommendations = ai_results.get('music_recommendations', [])
            if recommendations:
                for rec in recommendations:
                    print(f"    - {rec}")
            else:
                print("    No recommendations available")
            
            # Save AI analysis results
            output_file = self.output_dir / "itunes_music_analysis_results.json"
            with open(output_file, "w") as f:
                json.dump({
                    "basic_analysis": {
                        "most_played_artists": artist_plays.head(5).to_dict(),
                        "most_played_songs": song_plays.head(5).to_dict(),
                        "total_listening_time_hours": hours
                    },
                    "ai_analysis": ai_results
                }, f, indent=2)
            
            print(f"\nResults saved to {output_file}")
        else:
            print("\nAI analysis not available. Set OPENROUTER_API_KEY to enable enhanced analysis.")
        
        # Create visualization
        self._create_itunes_music_visualization(df)
    
    def _create_itunes_music_visualization(self, df):
        """Create visualizations for iTunes music analysis"""
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 1, figsize=(12, 14))
        
        # Plot 1: Most played artists
        artist_plays = df.groupby('artist').size().sort_values(ascending=False).head(10)
        axs[0].bar(artist_plays.index, artist_plays.values)
        axs[0].set_title('Most Played Artists')
        axs[0].set_xlabel('Artist')
        axs[0].set_ylabel('Play Count')
        axs[0].set_xticklabels(artist_plays.index, rotation=45, ha='right')
        
        # Plot 2: Listening activity by hour of day
        df['hour'] = df['timestamp'].dt.hour
        hourly_activity = df.groupby('hour').size()
        axs[1].bar(hourly_activity.index, hourly_activity.values)
        axs[1].set_title('Listening Activity by Hour of Day')
        axs[1].set_xlabel('Hour of Day')
        axs[1].set_ylabel('Play Count')
        axs[1].set_xticks(range(0, 24, 2))
        
        # Save figure
        plt.tight_layout()
        output_file = self.output_dir / "itunes_music_analysis_visualization.png"
        plt.savefig(output_file)
        plt.close()
        
        print(f"Visualization saved to {output_file}")
    
    def run_full_pipeline_demo(self):
        """Run a demonstration of the full forensic analysis pipeline"""
        print("\n=== Full Forensic Analysis Pipeline Demo ===")
        
        # Create forensic pipeline
        pipeline = ForensicPipeline(client=self.client)
        
        # Load all sample data
        with open(self.sample_data_dir / "messages.json", "r") as f:
            messages_data = json.load(f)
        
        with open(self.sample_data_dir / "app_usage.json", "r") as f:
            app_usage_data = json.load(f)
        
        with open(self.sample_data_dir / "chrome_history.json", "r") as f:
            chrome_history_data = json.load(f)
        
        with open(self.sample_data_dir / "itunes_music.json", "r") as f:
            itunes_music_data = json.load(f)
        
        # Prepare data for pipeline
        forensic_data = {
            "messages": messages_data,
            "app_usage": app_usage_data,
            "chrome_history": chrome_history_data,
            "itunes_music": itunes_music_data
        }
        
        print("Running full forensic analysis pipeline...")
        print("This may take a few minutes if using AI analysis.")
        
        # Run pipeline
        if self.client:
            results = pipeline.analyze(forensic_data)
            
            # Display summary of results
            print("\nForensic Analysis Summary:")
            print(f"  {results.get('summary', 'No summary available')}")
            
            print("\nKey Findings:")
            findings = results.get('key_findings', [])
            if findings:
                for i, finding in enumerate(findings, 1):
                    print(f"  {i}. {finding}")
            else:
                print("  No key findings available")
            
            print("\nTimeline Highlights:")
            timeline = results.get('timeline_highlights', [])
            if timeline:
                for event in timeline:
                    print(f"  - {event}")
            else:
                print("  No timeline highlights available")
            
            print("\nRecommendations:")
            recommendations = results.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            else:
                print("  No recommendations available")
            
            # Save results
            output_file = self.output_dir / "full_forensic_analysis_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"\nFull results saved to {output_file}")
            
            # Generate HTML report
            self._generate_html_report(results, forensic_data)
        else:
            print("\nFull pipeline analysis requires OpenRouter API key.")
            print("Set OPENROUTER_API_KEY environment variable to enable this feature.")
    
    def _generate_html_report(self, results, forensic_data):
        """Generate an HTML report from the forensic analysis results"""
        # Create report directory
        report_dir = self.output_dir / "report"
        report_dir.mkdir(exist_ok=True)
        
        # Copy visualizations to report directory
        import shutil
        for viz_file in self.output_dir.glob("*_visualization.png"):
            shutil.copy(viz_file, report_dir)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Forensic Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                header {{
                    background-color: #4a69bd;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                h1, h2, h3 {{
                    color: #4a69bd;
                }}
                .section {{
                    margin-bottom: 40px;
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 5px;
                }}
                .finding {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-left: 4px solid #4a69bd;
                }}
                .timeline-item {{
                    margin-bottom: 10px;
                    padding-left: 20px;
                    position: relative;
                }}
                .timeline-item:before {{
                    content: "";
                    position: absolute;
                    left: 0;
                    top: 8px;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background-color: #4a69bd;
                }}
                .recommendation {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-left: 4px solid #1565c0;
                }}
                .visualization {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .visualization img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                }}
                footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>iOS Forensic Analysis Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </header>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <p>{results.get('summary', 'No summary available')}</p>
                </div>
                
                <div class="section">
                    <h2>Key Findings</h2>
        """
        
        # Add key findings
        findings = results.get('key_findings', [])
        if findings:
            for finding in findings:
                html_content += f'<div class="finding"><p>{finding}</p></div>\n'
        else:
            html_content += '<p>No key findings available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>Timeline Analysis</h2>
        """
        
        # Add timeline
        timeline = results.get('timeline_highlights', [])
        if timeline:
            for event in timeline:
                html_content += f'<div class="timeline-item"><p>{event}</p></div>\n'
        else:
            html_content += '<p>No timeline highlights available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>Message Analysis</h2>
        """
        
        # Add message analysis
        message_analysis = results.get('message_analysis', {})
        if message_analysis:
            html_content += f'<p><strong>Conversation Summary:</strong> {message_analysis.get("summary", "Not available")}</p>\n'
            html_content += f'<p><strong>Sentiment Analysis:</strong> {message_analysis.get("sentiment_analysis", "Not available")}</p>\n'
            
            html_content += '<p><strong>Key Topics:</strong></p>\n<ul>\n'
            topics = message_analysis.get('key_topics', [])
            if topics:
                for topic in topics:
                    html_content += f'<li>{topic}</li>\n'
            else:
                html_content += '<li>No topics identified</li>\n'
            html_content += '</ul>\n'
            
            html_content += f'<p><strong>Relationship Assessment:</strong> {message_analysis.get("relationship_assessment", "Not available")}</p>\n'
            
            html_content += '<div class="visualization">\n'
            html_content += '<h3>Message Analysis Visualization</h3>\n'
            html_content += '<img src="message_analysis_visualization.png" alt="Message Analysis Visualization">\n'
            html_content += '</div>\n'
        else:
            html_content += '<p>No message analysis available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>App Usage Analysis</h2>
        """
        
        # Add app usage analysis
        app_usage_analysis = results.get('app_usage_analysis', {})
        if app_usage_analysis:
            html_content += f'<p><strong>Usage Pattern Summary:</strong> {app_usage_analysis.get("usage_pattern_summary", "Not available")}</p>\n'
            html_content += f'<p><strong>Behavioral Insights:</strong> {app_usage_analysis.get("behavioral_insights", "Not available")}</p>\n'
            html_content += f'<p><strong>Productivity Assessment:</strong> {app_usage_analysis.get("productivity_assessment", "Not available")}</p>\n'
            
            html_content += '<p><strong>Recommendations:</strong></p>\n<ul>\n'
            recommendations = app_usage_analysis.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    html_content += f'<li>{rec}</li>\n'
            else:
                html_content += '<li>No recommendations available</li>\n'
            html_content += '</ul>\n'
            
            html_content += '<div class="visualization">\n'
            html_content += '<h3>App Usage Analysis Visualization</h3>\n'
            html_content += '<img src="app_usage_analysis_visualization.png" alt="App Usage Analysis Visualization">\n'
            html_content += '</div>\n'
        else:
            html_content += '<p>No app usage analysis available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>Web Browsing Analysis</h2>
        """
        
        # Add Chrome history analysis
        chrome_analysis = results.get('chrome_history_analysis', {})
        if chrome_analysis:
            html_content += f'<p><strong>Browsing Pattern Summary:</strong> {chrome_analysis.get("browsing_pattern_summary", "Not available")}</p>\n'
            html_content += f'<p><strong>Security Assessment:</strong> {chrome_analysis.get("security_assessment", "Not available")}</p>\n'
            html_content += f'<p><strong>Behavioral Insights:</strong> {chrome_analysis.get("behavioral_insights", "Not available")}</p>\n'
            
            html_content += '<p><strong>Interest Categories:</strong></p>\n<ul>\n'
            categories = chrome_analysis.get('interest_categories', [])
            if categories:
                for category in categories:
                    html_content += f'<li>{category}</li>\n'
            else:
                html_content += '<li>No categories identified</li>\n'
            html_content += '</ul>\n'
            
            html_content += '<div class="visualization">\n'
            html_content += '<h3>Web Browsing Analysis Visualization</h3>\n'
            html_content += '<img src="chrome_history_analysis_visualization.png" alt="Web Browsing Analysis Visualization">\n'
            html_content += '</div>\n'
        else:
            html_content += '<p>No web browsing analysis available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>Music Listening Analysis</h2>
        """
        
        # Add iTunes music analysis
        music_analysis = results.get('itunes_music_analysis', {})
        if music_analysis:
            html_content += f'<p><strong>Music Taste Summary:</strong> {music_analysis.get("music_taste_summary", "Not available")}</p>\n'
            html_content += f'<p><strong>Listening Pattern Insights:</strong> {music_analysis.get("listening_pattern_insights", "Not available")}</p>\n'
            
            html_content += '<p><strong>Genre Preferences:</strong></p>\n<ul>\n'
            genres = music_analysis.get('genre_preferences', [])
            if genres:
                for genre in genres:
                    html_content += f'<li>{genre}</li>\n'
            else:
                html_content += '<li>No genre preferences identified</li>\n'
            html_content += '</ul>\n'
            
            html_content += '<p><strong>Music Recommendations:</strong></p>\n<ul>\n'
            recommendations = music_analysis.get('music_recommendations', [])
            if recommendations:
                for rec in recommendations:
                    html_content += f'<li>{rec}</li>\n'
            else:
                html_content += '<li>No recommendations available</li>\n'
            html_content += '</ul>\n'
            
            html_content += '<div class="visualization">\n'
            html_content += '<h3>Music Listening Analysis Visualization</h3>\n'
            html_content += '<img src="itunes_music_analysis_visualization.png" alt="Music Listening Analysis Visualization">\n'
            html_content += '</div>\n'
        else:
            html_content += '<p>No music listening analysis available.</p>\n'
        
        html_content += """
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
        """
        
        # Add recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                html_content += f'<div class="recommendation"><p><strong>Recommendation {i}:</strong> {rec}</p></div>\n'
        else:
            html_content += '<p>No recommendations available.</p>\n'
        
        html_content += """
                </div>
                
                <footer>
                    <p>Generated by iLEAPP AI Integration</p>
                    <p>Powered by OpenRouter API and Large Language Models</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Write HTML report to file
        report_file = report_dir / "index.html"
        with open(report_file, "w") as f:
            f.write(html_content)
        
        print(f"\nHTML report generated at {report_file}")
        print(f"Open this file in a web browser to view the full report.")
        
        # Try to open the report in the default web browser
        try:
            webbrowser.open(f"file://{report_file.absolute()}")
        except:
            pass
    
    def run_all_demos(self):
        """Run all demonstration modules"""
        print("=== iLEAPP AI Integration Demo Showcase ===")
        print("Running all demonstration modules...")
        
        self.run_message_analysis_demo()
        self.run_app_usage_analysis_demo()
        self.run_chrome_history_analysis_demo()
        self.run_itunes_music_analysis_demo()
        self.run_full_pipeline_demo()
        
        print("\n=== Demo Showcase Complete ===")
        print(f"All results saved to {self.output_dir}")
        
        # Try to open the report in the default web browser
        report_file = self.output_dir / "report" / "index.html"
        if report_file.exists():
            try:
                webbrowser.open(f"file://{report_file.absolute()}")
                print(f"\nOpened HTML report in web browser: {report_file}")
            except:
                print(f"\nHTML report available at: {report_file}")
                print("Open this file in a web browser to view the full report.")

def main():
    """Main function to run the demo showcase"""
    parser = argparse.ArgumentParser(description="iLEAPP AI Integration Demo Showcase")
    parser.add_argument("--api-key", help="OpenRouter API key (if not set in environment)")
    parser.add_argument("--demo", choices=["messages", "app-usage", "chrome", "itunes", "pipeline", "all"], 
                        default="all", help="Specific demo to run (default: all)")
    
    args = parser.parse_args()
    
    # Create demo showcase
    showcase = DemoShowcase(api_key=args.api_key)
    
    # Run selected demo
    if args.demo == "messages":
        showcase.run_message_analysis_demo()
    elif args.demo == "app-usage":
        showcase.run_app_usage_analysis_demo()
    elif args.demo == "chrome":
        showcase.run_chrome_history_analysis_demo()
    elif args.demo == "itunes":
        showcase.run_itunes_music_analysis_demo()
    elif args.demo == "pipeline":
        showcase.run_full_pipeline_demo()
    else:
        showcase.run_all_demos()

if __name__ == "__main__":
    main()
