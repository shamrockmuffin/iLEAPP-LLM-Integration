"""
Integration of LLM capabilities into iLEAPP's GUI and CLI interfaces.

This module provides the integration points for LLM capabilities with iLEAPP's
existing user interfaces, both graphical and command-line.
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import argparse
import logging
from typing import Dict, List, Any, Optional, Tuple

# Import iLEAPP modules - adjust paths as needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.report as ileapp_report
import scripts.artifact_report as ileapp_artifact_report
import scripts.ilapfuncs as ilapfuncs

# Import LLM integration modules
from scripts.openrouter_client import OpenRouterClient
from scripts.llm_analyzer import LLMAnalyzer
from scripts.security_enhancements import ForensicSecurity
from scripts.modular_architecture import LLMIntegrationManager
from scripts.user_dashboard import UserDashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ileapp_llm_integration")

class LLMIntegrationCLI:
    """Command-line interface integration for LLM capabilities."""
    
    def __init__(self):
        """Initialize the CLI integration."""
        self.llm_manager = LLMIntegrationManager()
        self.llm_manager.initialize()
        self.security = None
        
    def extend_argument_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Extend iLEAPP's argument parser with LLM options.
        
        Args:
            parser: Existing argument parser
            
        Returns:
            Extended argument parser
        """
        # Add LLM integration argument group
        llm_group = parser.add_argument_group('LLM Integration Options')
        
        llm_group.add_argument('--enable-llm', action='store_true',
                              help='Enable LLM integration for enhanced analysis')
        
        llm_group.add_argument('--llm-provider', choices=['openrouter', 'local', 'anthropic', 'openai'],
                              default='openrouter',
                              help='LLM provider to use (default: openrouter)')
        
        llm_group.add_argument('--llm-api-key', 
                              help='API key for the LLM provider')
        
        llm_group.add_argument('--llm-model',
                              help='Specific LLM model to use')
        
        llm_group.add_argument('--llm-analyze-artifacts', nargs='+',
                              help='Specific artifacts to analyze with LLM (default: all)')
        
        llm_group.add_argument('--llm-security', action='store_true',
                              help='Enable security features for LLM integration')
        
        llm_group.add_argument('--llm-investigator',
                              help='Investigator name for chain of custody')
        
        llm_group.add_argument('--llm-case-id',
                              help='Case ID for forensic analysis')
        
        return parser
    
    def process_llm_arguments(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Process LLM-related command line arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Dictionary of LLM configuration
        """
        llm_config = {
            'enabled': args.enable_llm if hasattr(args, 'enable_llm') else False
        }
        
        if not llm_config['enabled']:
            return llm_config
        
        # Process provider
        llm_config['provider'] = args.llm_provider if hasattr(args, 'llm_provider') else 'openrouter'
        
        # Process API key
        if hasattr(args, 'llm_api_key') and args.llm_api_key:
            llm_config['api_key'] = args.llm_api_key
        else:
            # Try to get from environment variable
            env_var = f"{llm_config['provider'].upper()}_API_KEY"
            llm_config['api_key'] = os.environ.get(env_var)
            
            if not llm_config['api_key']:
                logger.warning(f"No API key provided for {llm_config['provider']}. "
                              f"Set --llm-api-key or {env_var} environment variable.")
        
        # Process model
        if hasattr(args, 'llm_model') and args.llm_model:
            llm_config['model'] = args.llm_model
        else:
            # Default models by provider
            defaults = {
                'openrouter': 'anthropic/claude-3-opus',
                'anthropic': 'claude-3-opus',
                'openai': 'gpt-4',
                'local': 'llama3'
            }
            llm_config['model'] = defaults.get(llm_config['provider'], 'anthropic/claude-3-opus')
        
        # Process artifacts to analyze
        if hasattr(args, 'llm_analyze_artifacts') and args.llm_analyze_artifacts:
            llm_config['analyze_artifacts'] = args.llm_analyze_artifacts
        else:
            llm_config['analyze_artifacts'] = 'all'
        
        # Process security options
        llm_config['security_enabled'] = args.llm_security if hasattr(args, 'llm_security') else False
        
        if llm_config['security_enabled']:
            llm_config['investigator'] = args.llm_investigator if hasattr(args, 'llm_investigator') else None
            llm_config['case_id'] = args.llm_case_id if hasattr(args, 'llm_case_id') else None
            
            # Initialize security
            self.security = ForensicSecurity(
                case_id=llm_config['case_id'],
                investigator=llm_config['investigator']
            )
            
            if llm_config.get('api_key'):
                # Initialize encryption with a derived key from API key
                # Note: In production, would use a separate secure password
                self.security.initialize_encryption(llm_config['api_key'][:16])
        
        return llm_config
    
    def initialize_llm_analyzer(self, llm_config: Dict[str, Any]) -> Optional[LLMAnalyzer]:
        """Initialize the LLM analyzer based on configuration.
        
        Args:
            llm_config: LLM configuration
            
        Returns:
            LLM analyzer instance or None if disabled
        """
        if not llm_config.get('enabled', False):
            return None
            
        if not llm_config.get('api_key'):
            logger.warning("LLM integration enabled but no API key provided")
            return None
            
        try:
            # Initialize client based on provider
            if llm_config['provider'] == 'openrouter':
                client = OpenRouterClient(
                    api_key=llm_config['api_key'],
                    model=llm_config['model']
                )
            else:
                # For other providers, would initialize appropriate client
                logger.warning(f"Provider {llm_config['provider']} not fully implemented yet")
                return None
                
            # Initialize analyzer
            analyzer = LLMAnalyzer(client, security=self.security)
            logger.info(f"LLM analyzer initialized with {llm_config['provider']} "
                       f"using model {llm_config['model']}")
            
            return analyzer
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM analyzer: {str(e)}")
            return None
    
    def extend_ileapp_processing(self, analyzer: LLMAnalyzer, 
                                extract_dir: str, 
                                report_folder: str,
                                artifacts_to_analyze: List[str] = None) -> None:
        """Extend iLEAPP processing with LLM analysis.
        
        Args:
            analyzer: LLM analyzer instance
            extract_dir: Directory with extracted artifacts
            report_folder: Directory for reports
            artifacts_to_analyze: List of artifacts to analyze (None for all)
        """
        if not analyzer:
            return
            
        logger.info("Extending iLEAPP processing with LLM analysis")
        
        # Create LLM analysis directory
        llm_analysis_dir = os.path.join(report_folder, "LLM_Analysis")
        os.makedirs(llm_analysis_dir, exist_ok=True)
        
        # Get list of processed artifacts
        processed_artifacts = self._get_processed_artifacts(report_folder)
        
        if not processed_artifacts:
            logger.warning("No processed artifacts found for LLM analysis")
            return
            
        # Filter artifacts if specified
        if artifacts_to_analyze and artifacts_to_analyze != 'all':
            artifacts_to_process = [a for a in processed_artifacts 
                                   if a['name'] in artifacts_to_analyze]
        else:
            artifacts_to_process = processed_artifacts
            
        logger.info(f"Analyzing {len(artifacts_to_process)} artifacts with LLM")
        
        # Process each artifact
        for artifact in artifacts_to_process:
            try:
                self._analyze_artifact_with_llm(
                    analyzer, 
                    artifact, 
                    extract_dir, 
                    report_folder, 
                    llm_analysis_dir
                )
            except Exception as e:
                logger.error(f"Error analyzing artifact {artifact['name']}: {str(e)}")
                
        # Generate summary report
        self._generate_llm_summary_report(
            analyzer, 
            artifacts_to_process, 
            report_folder, 
            llm_analysis_dir
        )
        
        # Add LLM analysis to index.html
        self._add_llm_section_to_report(report_folder, llm_analysis_dir)
    
    def _get_processed_artifacts(self, report_folder: str) -> List[Dict[str, Any]]:
        """Get list of processed artifacts from report folder.
        
        Args:
            report_folder: Directory containing reports
            
        Returns:
            List of artifact information dictionaries
        """
        artifacts = []
        
        # Look for artifact JSON files
        for root, _, files in os.walk(report_folder):
            for file in files:
                if file.endswith('_artifacts.json'):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            artifact_data = json.load(f)
                            
                            # Extract artifact name from filename
                            name = file.replace('_artifacts.json', '')
                            
                            artifacts.append({
                                'name': name,
                                'data': artifact_data,
                                'path': os.path.join(root, file)
                            })
                    except Exception as e:
                        logger.error(f"Error reading artifact file {file}: {str(e)}")
        
        return artifacts
    
    def _analyze_artifact_with_llm(self, 
                                  analyzer: LLMAnalyzer,
                                  artifact: Dict[str, Any],
                                  extract_dir: str,
                                  report_folder: str,
                                  llm_analysis_dir: str) -> None:
        """Analyze a single artifact with LLM.
        
        Args:
            analyzer: LLM analyzer instance
            artifact: Artifact information
            extract_dir: Directory with extracted artifacts
            report_folder: Directory for reports
            llm_analysis_dir: Directory for LLM analysis
        """
        artifact_name = artifact['name']
        logger.info(f"Analyzing artifact: {artifact_name}")
        
        # Log the analysis if security is enabled
        if self.security:
            self.security.log_ai_analysis(
                artifact_name,
                f"Analyze {artifact_name} artifact data",
                analyzer.client.model
            )
        
        # Perform analysis based on artifact type
        if artifact_name == 'sms':
            analysis = analyzer.analyze_messages(artifact['data'])
        elif artifact_name == 'appUsage':
            analysis = analyzer.analyze_app_usage(artifact['data'])
        elif artifact_name == 'iTunesMusic':
            analysis = analyzer.analyze_itunes_music(artifact['data'])
        elif artifact_name == 'chromeHistory':
            analysis = analyzer.analyze_chrome_history(artifact['data'])
        else:
            # Generic analysis for other artifact types
            analysis = analyzer.analyze_generic_artifact(artifact['data'], artifact_name)
        
        # Save analysis results
        analysis_file = os.path.join(llm_analysis_dir, f"{artifact_name}_llm_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
            
        # Generate HTML report for this artifact
        html_file = os.path.join(llm_analysis_dir, f"{artifact_name}_llm_analysis.html")
        self._generate_artifact_html_report(artifact_name, analysis, html_file)
        
        logger.info(f"Completed LLM analysis for {artifact_name}")
    
    def _generate_artifact_html_report(self, 
                                      artifact_name: str, 
                                      analysis: Dict[str, Any],
                                      output_file: str) -> None:
        """Generate HTML report for artifact analysis.
        
        Args:
            artifact_name: Name of the artifact
            analysis: Analysis results
            output_file: Output HTML file path
        """
        # Basic HTML template
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LLM Analysis: {artifact_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .analysis-section {{ margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .insight {{ margin-bottom: 10px; padding: 10px; background-color: #e9f7ef; border-left: 4px solid #27ae60; }}
                .pattern {{ margin-bottom: 10px; padding: 10px; background-color: #eaf2f8; border-left: 4px solid #3498db; }}
                .anomaly {{ margin-bottom: 10px; padding: 10px; background-color: #fdedec; border-left: 4px solid #e74c3c; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>LLM Analysis: {artifact_name}</h1>
        """
        
        # Add summary section
        if 'summary' in analysis:
            html += f"""
            <div class="analysis-section">
                <h2>Summary</h2>
                <p>{analysis['summary']}</p>
            </div>
            """
        
        # Add insights section
        if 'insights' in analysis and analysis['insights']:
            html += """
            <div class="analysis-section">
                <h2>Key Insights</h2>
            """
            
            for i, insight in enumerate(analysis['insights']):
                html += f"""
                <div class="insight">
                    <h3>Insight {i+1}</h3>
                    <p>{insight}</p>
                </div>
                """
                
            html += "</div>"
        
        # Add patterns section
        if 'patterns' in analysis and analysis['patterns']:
            html += """
            <div class="analysis-section">
                <h2>Detected Patterns</h2>
            """
            
            for i, pattern in enumerate(analysis['patterns']):
                html += f"""
                <div class="pattern">
                    <h3>Pattern {i+1}</h3>
                    <p>{pattern}</p>
                </div>
                """
                
            html += "</div>"
        
        # Add anomalies section
        if 'anomalies' in analysis and analysis['anomalies']:
            html += """
            <div class="analysis-section">
                <h2>Potential Anomalies</h2>
            """
            
            for i, anomaly in enumerate(analysis['anomalies']):
                html += f"""
                <div class="anomaly">
                    <h3>Anomaly {i+1}</h3>
                    <p>{anomaly}</p>
                </div>
                """
                
            html += "</div>"
        
        # Add timeline if present
        if 'timeline' in analysis and analysis['timeline']:
            html += """
            <div class="analysis-section">
                <h2>Timeline Analysis</h2>
                <table>
                    <tr>
                        <th>Date/Time</th>
                        <th>Event</th>
                        <th>Significance</th>
                    </tr>
            """
            
            for event in analysis['timeline']:
                html += f"""
                <tr>
                    <td>{event.get('datetime', 'N/A')}</td>
                    <td>{event.get('event', 'N/A')}</td>
                    <td>{event.get('significance', 'N/A')}</td>
                </tr>
                """
                
            html += """
                </table>
            </div>
            """
        
        # Add recommendations if present
        if 'recommendations' in analysis and analysis['recommendations']:
            html += """
            <div class="analysis-section">
                <h2>Investigation Recommendations</h2>
                <ul>
            """
            
            for rec in analysis['recommendations']:
                html += f"<li>{rec}</li>"
                
            html += """
                </ul>
            </div>
            """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)
    
    def _generate_llm_summary_report(self,
                                    analyzer: LLMAnalyzer,
                                    artifacts: List[Dict[str, Any]],
                                    report_folder: str,
                                    llm_analysis_dir: str) -> None:
        """Generate summary report of all LLM analyses.
        
        Args:
            analyzer: LLM analyzer instance
            artifacts: List of analyzed artifacts
            report_folder: Directory for reports
            llm_analysis_dir: Directory for LLM analysis
        """
        logger.info("Generating LLM analysis summary report")
        
        # Collect all analysis results
        analyses = {}
        for artifact in artifacts:
            artifact_name = artifact['name']
            analysis_file = os.path.join(llm_analysis_dir, f"{artifact_name}_llm_analysis.json")
            
            if os.path.exists(analysis_file):
                try:
                    with open(analysis_file, 'r') as f:
                        analyses[artifact_name] = json.load(f)
                except Exception as e:
                    logger.error(f"Error reading analysis file {analysis_file}: {str(e)}")
        
        # Generate cross-artifact analysis
        cross_analysis = analyzer.generate_cross_artifact_analysis(analyses)
        
        # Save cross-analysis
        cross_analysis_file = os.path.join(llm_analysis_dir, "cross_artifact_analysis.json")
        with open(cross_analysis_file, 'w') as f:
            json.dump(cross_analysis, f, indent=2)
        
        # Generate HTML summary report
        summary_html = os.path.join(llm_analysis_dir, "llm_analysis_summary.html")
        self._generate_summary_html_report(analyses, cross_analysis, summary_html)
        
        # Create index file
        index_html = os.path.join(llm_analysis_dir, "index.html")
        self._generate_llm_index_html(analyses, index_html)
        
        logger.info("LLM analysis summary report generated")
    
    def _generate_summary_html_report(self,
                                     analyses: Dict[str, Dict[str, Any]],
                                     cross_analysis: Dict[str, Any],
                                     output_file: str) -> None:
        """Generate HTML summary report.
        
        Args:
            analyses: Dictionary of analysis results by artifact
            cross_analysis: Cross-artifact analysis results
            output_file: Output HTML file path
        """
        # Basic HTML template
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LLM Analysis Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2, h3 { color: #2c3e50; }
                .analysis-section { margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
                .insight { margin-bottom: 10px; padding: 10px; background-color: #e9f7ef; border-left: 4px solid #27ae60; }
                .correlation { margin-bottom: 10px; padding: 10px; background-color: #ebf5fb; border-left: 4px solid #3498db; }
                .timeline { margin-bottom: 10px; padding: 10px; background-color: #fef9e7; border-left: 4px solid #f1c40f; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .artifact-link { margin-right: 10px; display: inline-block; padding: 5px 10px; background-color: #f2f2f2; border-radius: 3px; text-decoration: none; color: #333; }
                .artifact-link:hover { background-color: #ddd; }
            </style>
        </head>
        <body>
            <h1>LLM Analysis Summary</h1>
            
            <div class="analysis-section">
                <h2>Analyzed Artifacts</h2>
                <p>The following artifacts were analyzed:</p>
        """
        
        # Add artifact links
        for artifact_name in analyses.keys():
            html += f"""
            <a href="{artifact_name}_llm_analysis.html" class="artifact-link">{artifact_name}</a>
            """
            
        html += """
            </div>
        """
        
        # Add executive summary
        if 'executive_summary' in cross_analysis:
            html += f"""
            <div class="analysis-section">
                <h2>Executive Summary</h2>
                <p>{cross_analysis['executive_summary']}</p>
            </div>
            """
        
        # Add key findings
        if 'key_findings' in cross_analysis and cross_analysis['key_findings']:
            html += """
            <div class="analysis-section">
                <h2>Key Findings</h2>
                <ul>
            """
            
            for finding in cross_analysis['key_findings']:
                html += f"<li>{finding}</li>"
                
            html += """
                </ul>
            </div>
            """
        
        # Add correlations
        if 'correlations' in cross_analysis and cross_analysis['correlations']:
            html += """
            <div class="analysis-section">
                <h2>Cross-Artifact Correlations</h2>
            """
            
            for i, correlation in enumerate(cross_analysis['correlations']):
                html += f"""
                <div class="correlation">
                    <h3>Correlation {i+1}</h3>
                    <p>{correlation}</p>
                </div>
                """
                
            html += "</div>"
        
        # Add unified timeline if present
        if 'unified_timeline' in cross_analysis and cross_analysis['unified_timeline']:
            html += """
            <div class="analysis-section">
                <h2>Unified Timeline</h2>
                <table>
                    <tr>
                        <th>Date/Time</th>
                        <th>Artifact</th>
                        <th>Event</th>
                        <th>Significance</th>
                    </tr>
            """
            
            for event in cross_analysis['unified_timeline']:
                html += f"""
                <tr>
                    <td>{event.get('datetime', 'N/A')}</td>
                    <td>{event.get('artifact', 'N/A')}</td>
                    <td>{event.get('event', 'N/A')}</td>
                    <td>{event.get('significance', 'N/A')}</td>
                </tr>
                """
                
            html += """
                </table>
            </div>
            """
        
        # Add investigation recommendations
        if 'investigation_recommendations' in cross_analysis and cross_analysis['investigation_recommendations']:
            html += """
            <div class="analysis-section">
                <h2>Investigation Recommendations</h2>
                <ol>
            """
            
            for rec in cross_analysis['investigation_recommendations']:
                html += f"<li>{rec}</li>"
                
            html += """
                </ol>
            </div>
            """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)
    
    def _generate_llm_index_html(self,
                                analyses: Dict[str, Dict[str, Any]],
                                output_file: str) -> None:
        """Generate index HTML for LLM analysis.
        
        Args:
            analyses: Dictionary of analysis results by artifact
            output_file: Output HTML file path
        """
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LLM Analysis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #2c3e50; }
                .card { margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
                .card:hover { background-color: #e9ecef; }
                a { text-decoration: none; color: #3498db; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>LLM Analysis</h1>
            
            <div class="card">
                <h2><a href="llm_analysis_summary.html">Analysis Summary</a></h2>
                <p>Comprehensive summary of all artifact analyses with cross-artifact correlations and unified timeline.</p>
            </div>
            
            <h2>Individual Artifact Analyses</h2>
        """
        
        # Add card for each artifact
        for artifact_name in analyses.keys():
            html += f"""
            <div class="card">
                <h2><a href="{artifact_name}_llm_analysis.html">{artifact_name}</a></h2>
                <p>LLM analysis of {artifact_name} artifact data.</p>
            </div>
            """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)
    
    def _add_llm_section_to_report(self, report_folder: str, llm_analysis_dir: str) -> None:
        """Add LLM analysis section to main report.
        
        Args:
            report_folder: Directory for reports
            llm_analysis_dir: Directory for LLM analysis
        """
        index_file = os.path.join(report_folder, "index.html")
        
        if not os.path.exists(index_file):
            logger.warning(f"Main index.html not found at {index_file}")
            return
            
        try:
            # Read the index file
            with open(index_file, 'r') as f:
                content = f.read()
                
            # Find the position to insert our section (before closing body tag)
            insert_pos = content.rfind('</body>')
            
            if insert_pos == -1:
                logger.warning("Could not find </body> tag in index.html")
                return
                
            # Create LLM section HTML
            llm_section = f"""
            <div class="card bg-light mb-3">
                <div class="card-header">LLM Analysis</div>
                <div class="card-body">
                    <h5 class="card-title">AI-Enhanced Analysis</h5>
                    <p class="card-text">Advanced analysis of artifacts using Large Language Models.</p>
                    <a href="LLM_Analysis/index.html" class="btn btn-primary">View LLM Analysis</a>
                </div>
            </div>
            """
            
            # Insert our section
            new_content = content[:insert_pos] + llm_section + content[insert_pos:]
            
            # Write back to file
            with open(index_file, 'w') as f:
                f.write(new_content)
                
            logger.info("Added LLM section to main report")
            
        except Exception as e:
            logger.error(f"Error adding LLM section to report: {str(e)}")


class LLMIntegrationGUI:
    """Graphical user interface integration for LLM capabilities."""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """Initialize the GUI integration.
        
        Args:
            root: Tkinter root window (None to create new)
        """
        self.root = root
        self.llm_manager = LLMIntegrationManager()
        self.llm_manager.initialize()
        self.security = None
        self.llm_config = {
            'enabled': False,
            'provider': 'openrouter',
            'model': 'anthropic/claude-3-opus',
            'analyze_artifacts': 'all',
            'security_enabled': False
        }
        self.llm_frame = None
        self.dashboard = None
    
    def extend_ileapp_gui(self, parent_frame: ttk.Frame) -> ttk.Frame:
        """Extend iLEAPP GUI with LLM options.
        
        Args:
            parent_frame: Parent frame to add LLM options
            
        Returns:
            Frame containing LLM options
        """
        # Create LLM frame
        self.llm_frame = ttk.LabelFrame(parent_frame, text="LLM Integration")
        
        # Enable LLM checkbox
        self.llm_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.llm_frame, 
            text="Enable LLM Integration", 
            variable=self.llm_enabled_var,
            command=self._toggle_llm_options
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Provider selection
        ttk.Label(self.llm_frame, text="LLM Provider:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        
        self.provider_var = tk.StringVar(value="openrouter")
        provider_combo = ttk.Combobox(
            self.llm_frame, 
            textvariable=self.provider_var,
            values=["openrouter", "anthropic", "openai", "local"],
            state="readonly",
            width=15
        )
        provider_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        provider_combo.bind("<<ComboboxSelected>>", self._update_model_options)
        
        # API Key entry
        ttk.Label(self.llm_frame, text="API Key:").grid(
            row=2, column=0, sticky="w", padx=5, pady=2
        )
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            self.llm_frame, 
            textvariable=self.api_key_var,
            width=30,
            show="*"
        )
        self.api_key_entry.grid(row=2, column=1, columnspan=2, sticky="we", padx=5, pady=2)
        
        # Show/hide API key
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.llm_frame, 
            text="Show", 
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility
        ).grid(row=2, column=3, sticky="w", padx=0, pady=2)
        
        # Model selection
        ttk.Label(self.llm_frame, text="Model:").grid(
            row=3, column=0, sticky="w", padx=5, pady=2
        )
        
        self.model_var = tk.StringVar(value="anthropic/claude-3-opus")
        self.model_combo = ttk.Combobox(
            self.llm_frame, 
            textvariable=self.model_var,
            values=self._get_model_options("openrouter"),
            state="readonly",
            width=30
        )
        self.model_combo.grid(row=3, column=1, columnspan=2, sticky="we", padx=5, pady=2)
        
        # Security options
        self.security_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.llm_frame, 
            text="Enable Security Features", 
            variable=self.security_var,
            command=self._toggle_security_options
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Security frame (initially hidden)
        self.security_frame = ttk.Frame(self.llm_frame)
        self.security_frame.grid(row=5, column=0, columnspan=4, sticky="we", padx=5, pady=0)
        self.security_frame.grid_remove()  # Hide initially
        
        # Investigator name
        ttk.Label(self.security_frame, text="Investigator:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        
        self.investigator_var = tk.StringVar()
        ttk.Entry(
            self.security_frame, 
            textvariable=self.investigator_var,
            width=20
        ).grid(row=0, column=1, sticky="we", padx=5, pady=2)
        
        # Case ID
        ttk.Label(self.security_frame, text="Case ID:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        
        self.case_id_var = tk.StringVar()
        ttk.Entry(
            self.security_frame, 
            textvariable=self.case_id_var,
            width=20
        ).grid(row=1, column=1, sticky="we", padx=5, pady=2)
        
        # Advanced options button
        ttk.Button(
            self.llm_frame,
            text="Advanced Options",
            command=self._show_advanced_options
        ).grid(row=6, column=0, sticky="w", padx=5, pady=10)
        
        # Dashboard button
        ttk.Button(
            self.llm_frame,
            text="LLM Dashboard",
            command=self._show_dashboard
        ).grid(row=6, column=1, sticky="w", padx=5, pady=10)
        
        # Disable LLM options initially
        self._toggle_llm_options()
        
        return self.llm_frame
    
    def _toggle_llm_options(self) -> None:
        """Toggle LLM options based on enabled state."""
        enabled = self.llm_enabled_var.get()
        state = "normal" if enabled else "disabled"
        
        for child in self.llm_frame.winfo_children():
            if child.winfo_class() != 'TLabelframe' and child != self.security_frame:
                try:
                    child.configure(state=state)
                except:
                    pass  # Some widgets don't have state
        
        # Update config
        self.llm_config['enabled'] = enabled
    
    def _toggle_api_key_visibility(self) -> None:
        """Toggle API key visibility."""
        show = self.show_key_var.get()
        self.api_key_entry.configure(show="" if show else "*")
    
    def _toggle_security_options(self) -> None:
        """Toggle security options based on enabled state."""
        enabled = self.security_var.get()
        
        if enabled:
            self.security_frame.grid()
        else:
            self.security_frame.grid_remove()
            
        # Update config
        self.llm_config['security_enabled'] = enabled
    
    def _update_model_options(self, event=None) -> None:
        """Update model options based on selected provider."""
        provider = self.provider_var.get()
        models = self._get_model_options(provider)
        
        self.model_combo['values'] = models
        if models:
            self.model_var.set(models[0])
            
        # Update config
        self.llm_config['provider'] = provider
    
    def _get_model_options(self, provider: str) -> List[str]:
        """Get model options for a provider.
        
        Args:
            provider: LLM provider
            
        Returns:
            List of model options
        """
        if provider == "openrouter":
            return [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
                "openai/gpt-4o",
                "openai/gpt-4-turbo",
                "google/gemini-1.5-pro",
                "meta-llama/llama-3-70b-instruct"
            ]
        elif provider == "anthropic":
            return [
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku"
            ]
        elif provider == "openai":
            return [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4"
            ]
        elif provider == "local":
            return [
                "llama3",
                "mistral-7b",
                "phi-3"
            ]
        else:
            return []
    
    def _show_advanced_options(self) -> None:
        """Show advanced LLM options dialog."""
        advanced_window = tk.Toplevel(self.root)
        advanced_window.title("Advanced LLM Options")
        advanced_window.geometry("500x400")
        advanced_window.transient(self.root)
        advanced_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(advanced_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Artifacts tab
        artifacts_frame = ttk.Frame(notebook)
        notebook.add(artifacts_frame, text="Artifacts")
        
        ttk.Label(artifacts_frame, text="Select artifacts to analyze:").pack(anchor="w", padx=10, pady=5)
        
        # Artifact selection
        artifact_frame = ttk.Frame(artifacts_frame)
        artifact_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollable frame for artifacts
        canvas = tk.Canvas(artifact_frame)
        scrollbar = ttk.Scrollbar(artifact_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Artifact checkboxes
        artifacts = [
            "sms", "appUsage", "iTunesMusic", "chromeHistory", "locationData",
            "contacts", "calendar", "notes", "photos", "voiceMemos", "callHistory"
        ]
        
        self.artifact_vars = {}
        for i, artifact in enumerate(artifacts):
            var = tk.BooleanVar(value=True)
            self.artifact_vars[artifact] = var
            ttk.Checkbutton(
                scrollable_frame, 
                text=artifact, 
                variable=var
            ).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        # Select/Deselect All buttons
        button_frame = ttk.Frame(artifacts_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            button_frame,
            text="Select All",
            command=lambda: self._set_all_artifacts(True)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Deselect All",
            command=lambda: self._set_all_artifacts(False)
        ).pack(side="left", padx=5)
        
        # Model parameters tab
        params_frame = ttk.Frame(notebook)
        notebook.add(params_frame, text="Parameters")
        
        # Temperature
        ttk.Label(params_frame, text="Temperature:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        
        self.temperature_var = tk.DoubleVar(value=0.7)
        temperature_scale = ttk.Scale(
            params_frame,
            from_=0.0,
            to=1.0,
            variable=self.temperature_var,
            orient="horizontal",
            length=200
        )
        temperature_scale.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        ttk.Label(params_frame, textvariable=self.temperature_var).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # Max tokens
        ttk.Label(params_frame, text="Max Tokens:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        
        self.max_tokens_var = tk.IntVar(value=4000)
        ttk.Spinbox(
            params_frame,
            from_=100,
            to=32000,
            increment=100,
            textvariable=self.max_tokens_var,
            width=10
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Top P
        ttk.Label(params_frame, text="Top P:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )
        
        self.top_p_var = tk.DoubleVar(value=0.9)
        top_p_scale = ttk.Scale(
            params_frame,
            from_=0.0,
            to=1.0,
            variable=self.top_p_var,
            orient="horizontal",
            length=200
        )
        top_p_scale.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        
        ttk.Label(params_frame, textvariable=self.top_p_var).grid(
            row=2, column=2, padx=5, pady=5
        )
        
        # Output options tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        
        # Generate visualizations
        self.visualizations_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame, 
            text="Generate Visualizations", 
            variable=self.visualizations_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Include in main report
        self.include_in_report_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame, 
            text="Include in Main Report", 
            variable=self.include_in_report_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Generate timeline
        self.timeline_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame, 
            text="Generate Timeline", 
            variable=self.timeline_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Export format
        ttk.Label(output_frame, text="Export Format:").pack(anchor="w", padx=10, pady=5)
        
        self.export_format_var = tk.StringVar(value="html")
        ttk.Radiobutton(
            output_frame, 
            text="HTML", 
            variable=self.export_format_var,
            value="html"
        ).pack(anchor="w", padx=20, pady=2)
        
        ttk.Radiobutton(
            output_frame, 
            text="JSON", 
            variable=self.export_format_var,
            value="json"
        ).pack(anchor="w", padx=20, pady=2)
        
        ttk.Radiobutton(
            output_frame, 
            text="PDF", 
            variable=self.export_format_var,
            value="pdf"
        ).pack(anchor="w", padx=20, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(advanced_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="OK",
            command=advanced_window.destroy
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame,
            text="Apply",
            command=self._apply_advanced_options
        ).pack(side="right", padx=5)
    
    def _set_all_artifacts(self, value: bool) -> None:
        """Set all artifact checkboxes to a value.
        
        Args:
            value: Boolean value to set
        """
        for var in self.artifact_vars.values():
            var.set(value)
    
    def _apply_advanced_options(self) -> None:
        """Apply advanced options to configuration."""
        # Get selected artifacts
        selected_artifacts = [
            artifact for artifact, var in self.artifact_vars.items() 
            if var.get()
        ]
        
        if selected_artifacts:
            self.llm_config['analyze_artifacts'] = selected_artifacts
        else:
            self.llm_config['analyze_artifacts'] = 'all'
            messagebox.showwarning(
                "No Artifacts Selected",
                "No artifacts were selected. All artifacts will be analyzed."
            )
        
        # Get model parameters
        self.llm_config['temperature'] = self.temperature_var.get()
        self.llm_config['max_tokens'] = self.max_tokens_var.get()
        self.llm_config['top_p'] = self.top_p_var.get()
        
        # Get output options
        self.llm_config['generate_visualizations'] = self.visualizations_var.get()
        self.llm_config['include_in_report'] = self.include_in_report_var.get()
        self.llm_config['generate_timeline'] = self.timeline_var.get()
        self.llm_config['export_format'] = self.export_format_var.get()
    
    def _show_dashboard(self) -> None:
        """Show LLM dashboard."""
        if not self.dashboard:
            self.dashboard = UserDashboard(self.root, self.llm_manager)
        
        self.dashboard.show()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get current LLM configuration.
        
        Returns:
            Dictionary of LLM configuration
        """
        # Update config with current values
        self.llm_config['enabled'] = self.llm_enabled_var.get()
        self.llm_config['provider'] = self.provider_var.get()
        self.llm_config['api_key'] = self.api_key_var.get()
        self.llm_config['model'] = self.model_var.get()
        self.llm_config['security_enabled'] = self.security_var.get()
        
        if self.llm_config['security_enabled']:
            self.llm_config['investigator'] = self.investigator_var.get()
            self.llm_config['case_id'] = self.case_id_var.get()
        
        return self.llm_config
    
    def initialize_llm_analyzer(self) -> Optional[LLMAnalyzer]:
        """Initialize the LLM analyzer based on configuration.
        
        Returns:
            LLM analyzer instance or None if disabled
        """
        config = self.get_llm_config()
        
        if not config.get('enabled', False):
            return None
            
        if not config.get('api_key'):
            messagebox.showerror(
                "API Key Required",
                f"API key is required for {config['provider']}."
            )
            return None
            
        try:
            # Initialize security if enabled
            if config.get('security_enabled', False):
                self.security = ForensicSecurity(
                    case_id=config.get('case_id'),
                    investigator=config.get('investigator')
                )
                
                if config.get('api_key'):
                    # Initialize encryption with a derived key from API key
                    # Note: In production, would use a separate secure password
                    self.security.initialize_encryption(config['api_key'][:16])
            
            # Initialize client based on provider
            if config['provider'] == 'openrouter':
                client = OpenRouterClient(
                    api_key=config['api_key'],
                    model=config['model']
                )
            else:
                # For other providers, would initialize appropriate client
                messagebox.showwarning(
                    "Provider Not Implemented",
                    f"Provider {config['provider']} is not fully implemented yet."
                )
                return None
                
            # Initialize analyzer
            analyzer = LLMAnalyzer(
                client, 
                security=self.security,
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 4000),
                top_p=config.get('top_p', 0.9)
            )
            
            return analyzer
            
        except Exception as e:
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize LLM analyzer: {str(e)}"
            )
            return None


# Patch iLEAPP's main functions to integrate LLM capabilities
def patch_ileapp_cli():
    """Patch iLEAPP's CLI to integrate LLM capabilities."""
    # Original parse_args function
    original_parse_args = ilapfuncs.parse_args
    
    # LLM integration instance
    llm_integration = LLMIntegrationCLI()
    
    def patched_parse_args():
        """Patched argument parsing function."""
        parser = original_parse_args()
        return llm_integration.extend_argument_parser(parser)
    
    # Replace original function
    ilapfuncs.parse_args = patched_parse_args
    
    # Original process_artifact function
    original_process_artifact = ileapp_artifact_report.process_artifact
    
    def patched_process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder):
        """Patched artifact processing function."""
        # Call original function
        result = original_process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder)
        
        # Additional LLM processing could be added here if needed
        
        return result
    
    # Replace original function
    ileapp_artifact_report.process_artifact = patched_process_artifact
    
    # Original report generation function
    original_generate_report = ileapp_report.generate_report
    
    def patched_generate_report(report_folder, artifact_data, artifact_paths, seeker, all_artifacts):
        """Patched report generation function."""
        # Call original function
        result = original_generate_report(report_folder, artifact_data, artifact_paths, seeker, all_artifacts)
        
        # Get command line arguments
        args = ilapfuncs.args
        
        # Process LLM arguments
        llm_config = llm_integration.process_llm_arguments(args)
        
        # Initialize LLM analyzer if enabled
        analyzer = llm_integration.initialize_llm_analyzer(llm_config)
        
        # Extend processing with LLM if enabled
        if analyzer:
            extract_dir = seeker.directory
            llm_integration.extend_ileapp_processing(
                analyzer, 
                extract_dir, 
                report_folder,
                llm_config.get('analyze_artifacts')
            )
        
        return result
    
    # Replace original function
    ileapp_report.generate_report = patched_generate_report


def patch_ileapp_gui():
    """Patch iLEAPP's GUI to integrate LLM capabilities."""
    # This would be implemented to patch the GUI functions
    # For now, we'll just define the approach
    
    # The approach would be:
    # 1. Find the main GUI class in iLEAPP
    # 2. Extend it to add our LLM options
    # 3. Hook into the processing functions to add LLM analysis
    
    pass


# Example usage
if __name__ == "__main__":
    # Patch iLEAPP CLI
    patch_ileapp_cli()
    
    # Create a simple test GUI
    root = tk.Tk()
    root.title("iLEAPP LLM Integration Test")
    root.geometry("800x600")
    
    # Create LLM integration GUI
    llm_gui = LLMIntegrationGUI(root)
    
    # Create a frame for the LLM options
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)
    
    # Add LLM options to the frame
    llm_frame = llm_gui.extend_ileapp_gui(frame)
    llm_frame.pack(fill="x", padx=10, pady=10)
    
    # Add a test button
    ttk.Button(
        frame,
        text="Test LLM Integration",
        command=lambda: print(llm_gui.get_llm_config())
    ).pack(pady=10)
    
    root.mainloop()
