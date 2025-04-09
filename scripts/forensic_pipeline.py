import os
import sys
import json
import logging
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from scripts.ilapfuncs import logfunc, is_platform_windows, open_sqlite_db_readonly
from scripts.artifact_report import ArtifactHtmlReport
from scripts.openrouter_integration import OpenRouterIntegration

class ForensicAnalysisPipeline:
    """
    Automated pipeline for enhancing iLEAPP forensic analysis with LLM capabilities.
    This class integrates with iLEAPP's workflow to provide AI-enhanced analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None, log_level: int = logging.INFO):
        """
        Initialize the forensic analysis pipeline.
        
        Args:
            api_key: OpenRouter API key. If None, will try to get from environment variable.
            log_level: Logging level
        """
        # Set up logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("forensic_pipeline.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ForensicAnalysisPipeline")
        
        # Initialize OpenRouter integration
        try:
            self.integration = OpenRouterIntegration(api_key)
            self.logger.info("Forensic analysis pipeline initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing OpenRouter integration: {e}")
            raise
        
        # Initialize storage for analysis results
        self.analysis_results = {}
        self.reports = {}
        self.appendices = {}
        self.case_summary = None
    
    def process_artifact(self, 
                        artifact_type: str, 
                        files_found: List[str], 
                        report_folder: str, 
                        seeker: Any, 
                        wrap_text: bool, 
                        timezone_offset: str) -> None:
        """
        Process an artifact with LLM enhancement.
        This method is designed to be called from iLEAPP's artifact processing system.
        
        Args:
            artifact_type: Type of artifact (e.g., "sms", "app_usage", "itunes_music", "chrome_history")
            files_found: List of files found for the artifact
            report_folder: Folder to save reports
            seeker: iLEAPP seeker object
            wrap_text: Whether to wrap text in reports
            timezone_offset: Timezone offset for timestamps
        """
        self.logger.info(f"Processing artifact: {artifact_type}")
        
        try:
            # Extract data from artifact
            artifact_data = self._extract_artifact_data(artifact_type, files_found, timezone_offset)
            
            if not artifact_data:
                self.logger.warning(f"No data extracted for artifact: {artifact_type}")
                return
            
            # Analyze with LLM
            analysis_results = self.integration.analyze_artifact(artifact_type, artifact_data)
            
            # Store results
            self.analysis_results[artifact_type] = analysis_results
            
            # Generate enhanced report
            report_html = self.integration.generate_report(artifact_type, analysis_results)
            self.reports[artifact_type] = report_html
            
            # Save enhanced report
            ai_report_folder = os.path.join(report_folder, "AI_Enhanced")
            os.makedirs(ai_report_folder, exist_ok=True)
            
            report_path = os.path.join(ai_report_folder, f"{artifact_type}_ai_enhanced.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            self.logger.info(f"Enhanced report saved to: {report_path}")
            
            # Create link in original report
            self._add_ai_report_link(report_folder, artifact_type, report_path)
            
        except Exception as e:
            self.logger.error(f"Error processing artifact {artifact_type}: {e}")
    
    def generate_case_materials(self, report_folder: str, all_artifact_data: Dict[str, Any]) -> None:
        """
        Generate comprehensive case materials including appendices and case summary.
        
        Args:
            report_folder: Folder to save reports
            all_artifact_data: Dictionary containing all artifact data
        """
        self.logger.info("Generating comprehensive case materials")
        
        try:
            # Create AI enhanced folder
            ai_report_folder = os.path.join(report_folder, "AI_Enhanced")
            os.makedirs(ai_report_folder, exist_ok=True)
            
            # Generate appendices
            appendices_folder = os.path.join(ai_report_folder, "Appendices")
            os.makedirs(appendices_folder, exist_ok=True)
            
            self.appendices = self.integration.generate_appendices(all_artifact_data, appendices_folder)
            
            # Generate case summary
            self.case_summary = self.integration.generate_case_summary(all_artifact_data, self.analysis_results)
            
            summary_path = os.path.join(ai_report_folder, "case_summary.html")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(self.case_summary)
            
            self.logger.info(f"Case summary saved to: {summary_path}")
            
            # Create index page for AI enhanced reports
            self._create_ai_index_page(ai_report_folder)
            
            # Add link to main index
            self._add_ai_section_to_main_index(report_folder, ai_report_folder)
            
        except Exception as e:
            self.logger.error(f"Error generating case materials: {e}")
    
    def _extract_artifact_data(self, 
                             artifact_type: str, 
                             files_found: List[str], 
                             timezone_offset: str) -> Union[List[Dict], Dict[str, Any]]:
        """
        Extract data from artifact files.
        
        Args:
            artifact_type: Type of artifact
            files_found: List of files found for the artifact
            timezone_offset: Timezone offset for timestamps
            
        Returns:
            Extracted artifact data
        """
        self.logger.info(f"Extracting data for artifact: {artifact_type}")
        
        try:
            # Map artifact types to extraction methods
            extraction_methods = {
                "sms": self._extract_sms_data,
                "app_usage": self._extract_app_usage_data,
                "itunes_music": self._extract_itunes_music_data,
                "chrome_history": self._extract_chrome_history_data
            }
            
            # Use specific extraction method if available, otherwise use generic
            if artifact_type in extraction_methods:
                return extraction_methods[artifact_type](files_found, timezone_offset)
            else:
                return self._extract_generic_data(files_found, artifact_type)
                
        except Exception as e:
            self.logger.error(f"Error extracting data for artifact {artifact_type}: {e}")
            return []
    
    def _extract_sms_data(self, files_found: List[str], timezone_offset: str) -> List[Dict]:
        """
        Extract SMS data from database.
        
        Args:
            files_found: List of files found for the artifact
            timezone_offset: Timezone offset for timestamps
            
        Returns:
            List of SMS messages
        """
        # Find SMS database
        db_file = None
        for file in files_found:
            if file.endswith('sms.db'):
                db_file = file
                break
        
        if not db_file:
            self.logger.warning("SMS database not found")
            return []
        
        try:
            # Query SMS database
            db = open_sqlite_db_readonly(db_file)
            
            query = """
            SELECT 
                message.rowid as msg_id,
                datetime(message.date + 978307200, 'unixepoch') as message_date,
                message.text as message_text,
                message.is_from_me as is_from_me,
                handle.id as contact_id,
                chat.chat_identifier as chat_id
            FROM message
            LEFT JOIN chat_message_join ON chat_message_join.message_id = message.rowid
            LEFT JOIN chat ON chat.rowid = chat_message_join.chat_id
            LEFT JOIN handle ON handle.rowid = message.handle_id
            ORDER BY message.date
            """
            
            cursor = db.cursor()
            cursor.execute(query)
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = dict(zip(columns, row))
                messages.append(message)
            
            db.close()
            return messages
            
        except Exception as e:
            self.logger.error(f"Error extracting SMS data: {e}")
            return []
    
    def _extract_app_usage_data(self, files_found: List[str], timezone_offset: str) -> List[Dict]:
        """
        Extract app usage data from database.
        
        Args:
            files_found: List of files found for the artifact
            timezone_offset: Timezone offset for timestamps
            
        Returns:
            List of app usage records
        """
        # Find knowledgeC database (contains app usage data)
        db_file = None
        for file in files_found:
            if 'knowledgeC.db' in file:
                db_file = file
                break
        
        if not db_file:
            self.logger.warning("App usage database not found")
            return []
        
        try:
            # Query app usage data
            db = open_sqlite_db_readonly(db_file)
            
            query = """
            SELECT 
                datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') as start_time,
                datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') as end_time,
                ZOBJECT.ZVALUESTRING as app_name,
                ZOBJECT.ZSTREAMNAME as activity_type,
                (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) as duration_seconds
            FROM ZOBJECT
            WHERE ZSTREAMNAME IS NOT NULL AND ZSTREAMNAME = 'app.usage'
            ORDER BY ZOBJECT.ZSTARTDATE
            """
            
            cursor = db.cursor()
            cursor.execute(query)
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            app_usage = []
            for row in rows:
                usage = dict(zip(columns, row))
                app_usage.append(usage)
            
            db.close()
            return app_usage
            
        except Exception as e:
            self.logger.error(f"Error extracting app usage data: {e}")
            return []
    
    def _extract_itunes_music_data(self, files_found: List[str], timezone_offset: str) -> List[Dict]:
        """
        Extract iTunes music history data from database.
        
        Args:
            files_found: List of files found for the artifact
            timezone_offset: Timezone offset for timestamps
            
        Returns:
            List of music history records
        """
        # Find iTunes database
        db_file = None
        for file in files_found:
            if 'iTunes' in file and file.endswith('.db'):
                db_file = file
                break
        
        if not db_file:
            self.logger.warning("iTunes database not found")
            return []
        
        try:
            # Query iTunes music history
            db = open_sqlite_db_readonly(db_file)
            
            query = """
            SELECT 
                item.title as track_name,
                item.artist as artist_name,
                item.album as album_name,
                item.genre as genre,
                datetime(item.date_added, 'unixepoch') as date_added,
                item.play_count as play_count,
                datetime(item.last_played_date, 'unixepoch') as last_played
            FROM item
            WHERE item.media_kind = 1
            ORDER BY item.last_played_date DESC
            """
            
            cursor = db.cursor()
            cursor.execute(query)
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            music_history = []
            for row in rows:
                track = dict(zip(columns, row))
                music_history.append(track)
            
            db.close()
            return music_history
            
        except Exception as e:
            self.logger.error(f"Error extracting iTunes music data: {e}")
            return []
    
    def _extract_chrome_history_data(self, files_found: List[str], timezone_offset: str) -> List[Dict]:
        """
        Extract Chrome browser history data from database.
        
        Args:
            files_found: List of files found for the artifact
            timezone_offset: Timezone offset for timestamps
            
        Returns:
            List of browser history records
        """
        # Find Chrome history database
        db_file = None
        for file in files_found:
            if 'History' in file and 'Chrome' in file:
                db_file = file
                break
        
        if not db_file:
            self.logger.warning("Chrome history database not found")
            return []
        
        try:
            # Query Chrome history
            db = open_sqlite_db_readonly(db_file)
            
            query = """
            SELECT 
                urls.url as url,
                urls.title as title,
                datetime(urls.last_visit_time/1000000-11644473600, 'unixepoch') as visit_time,
                urls.visit_count as visit_count,
                urls.typed_count as typed_count
            FROM urls
            ORDER BY urls.last_visit_time DESC
            """
            
            cursor = db.cursor()
            cursor.execute(query)
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                visit = dict(zip(columns, row))
                history.append(visit)
            
            db.close()
            return history
            
        except Exception as e:
            self.logger.error(f"Error extracting Chrome history data: {e}")
            return []
    
    def _extract_generic_data(self, files_found: List[str], artifact_type: str) -> List[Dict]:
        """
        Generic data extraction for unsupported artifact types.
        
        Args:
            files_found: List of files found for the artifact
            artifact_type: Type of artifact
            
        Returns:
            List of generic data records
        """
        self.logger.info(f"Using generic extraction for artifact type: {artifact_type}")
        
        data = []
        
        # Try to extract from SQLite databases
        for file in files_found:
            if file.endswith('.db') or file.endswith('.sqlite'):
                try:
                    db = open_sqlite_db_readonly(file)
                    
                    # Get list of tables
                    cursor = db.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    # Extract data from each table
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
                        
                        columns = [description[0] for description in cursor.description]
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            record = dict(zip(columns, row))
                            record['_table'] = table_name
                            record['_file'] = os.path.basename(file)
                            data.append(record)
                    
                    db.close()
                except Exception as e:
                    self.logger.error(f"Error extracting from database {file}: {e}")
        
        return data
    
    def _add_ai_report_link(self, report_folder: str, artifact_type: str, ai_report_path: str) -> None:
        """
        Add a link to the AI-enhanced report in the original report.
        
        Args:
            report_folder: Folder containing reports
            artifact_type: Type of artifact
            ai_report_path: Path to AI-enhanced report
        """
        # Find the original report file
        original_report = None
        for root, dirs, files in os.walk(report_folder):
            for file in files:
                if file.endswith('.html') and artifact_type.lower() in file.lower():
                    original_report = os.path.join(root, file)
                    break
            if original_report:
                break
        
        if not original_report:
            self.logger.warning(f"Original report for {artifact_type} not found")
            return
        
        try:
            # Read the original report
            with open(original_report, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add link to AI-enhanced report
            ai_link = f"""
            <div style="margin-top: 20px; padding: 10px; background-color: #f0f7ff; border: 1px solid #007bff; border-radius: 5px;">
                <h4 style="color: #007bff;">AI-Enhanced Analysis Available</h4>
                <p>An AI-enhanced analysis of this artifact is available with additional insights and patterns.</p>
                <a href="{os.path.relpath(ai_report_path, os.path.dirname(original_report))}" class="btn btn-primary" target="_blank">
                    View AI-Enhanced Analysis
                </a>
            </div>
            """
            
            # Insert before the closing body tag
            modified_content = content.replace('</body>', f'{ai_link}</body>')
            
            # Write back the modified report
            with open(original_report, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            self.logger.info(f"Added AI report link to {original_report}")
            
        except Exception as e:
            self.logger.error(f"Error adding AI report link: {e}")
    
    def _create_ai_index_page(self, ai_report_folder: str) -> None:
        """
        Create an index page for AI-enhanced reports.
        
        Args:
            ai_report_folder: Folder containing AI-enhanced reports
        """
        try:
            # Create index HTML
            index_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI-Enhanced Forensic Analysis</title>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                <style>
                    body { padding: 20px; }
                    .card { margin-bottom: 20px; }
                    .card-header { background-color: #f0f7ff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="mb-4">AI-Enhanced Forensic Analysis</h1>
                    <p class="lead">This section contains AI-enhanced analysis of the forensic artifacts, providing deeper insights and patterns.</p>
                    
                    <div class="card mb-4">
                        <div class="card-header">
                            <h2>Case Summary</h2>
                        </div>
                        <div class="card-body">
                            <p>Comprehensive analysis of all artifacts with key findings and patterns.</p>
                            <a href="case_summary.html" class="btn btn-primary">View Case Summary</a>
                        </div>
                    </div>
                    
                    <h2 class="mb-3">Artifact Analysis</h2>
                    <div class="row">
            """
            
            # Add cards for each artifact report
            for artifact_type, report_html in self.reports.items():
                report_filename = f"{artifact_type}_ai_enhanced.html"
                
                artifact_names = {
                    "sms": "Messages (SMS & iMessage)",
                    "app_usage": "App Usage",
                    "itunes_music": "iTunes Music History",
                    "chrome_history": "Chrome Browser History"
                }
                
                display_name = artifact_names.get(artifact_type, artifact_type.replace("_", " ").title())
                
                index_html += f"""
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>{display_name}</h3>
                        </div>
                        <div class="card-body">
                            <p>AI-enhanced analysis of {display_name.lower()} data.</p>
                            <a href="{report_filename}" class="btn btn-primary">View Analysis</a>
                        </div>
                    </div>
                </div>
                """
            
            # Add appendices section
            index_html += """
                    </div>
                    
                    <h2 class="mb-3 mt-4">Appendices</h2>
                    <div class="row">
            """
            
            # Add cards for each appendix
            appendix_names = {
                "technical": "Technical Appendices",
                "timeline": "Timeline Appendices",
                "statistical": "Statistical Appendices",
                "reference": "Reference Appendices"
            }
            
            for appendix_type, appendix_path in self.appendices.items():
                if appendix_type == "error":
                    continue
                    
                display_name = appendix_names.get(appendix_type, appendix_type.replace("_", " ").title())
                relative_path = os.path.relpath(appendix_path, ai_report_folder)
                
                index_html += f"""
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>{display_name}</h3>
                        </div>
                        <div class="card-body">
                            <p>Comprehensive reference materials and detailed information.</p>
                            <a href="{relative_path}" class="btn btn-primary">View Appendix</a>
                        </div>
                    </div>
                </div>
                """
            
            # Close HTML
            index_html += """
                    </div>
                </div>
                
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
            </html>
            """
            
            # Write index file
            index_path = os.path.join(ai_report_folder, "index.html")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_html)
                
            self.logger.info(f"Created AI index page at {index_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating AI index page: {e}")
    
    def _add_ai_section_to_main_index(self, report_folder: str, ai_report_folder: str) -> None:
        """
        Add a section for AI-enhanced analysis to the main index page.
        
        Args:
            report_folder: Main report folder
            ai_report_folder: Folder containing AI-enhanced reports
        """
        try:
            # Find the main index file
            main_index = os.path.join(report_folder, "index.html")
            
            if not os.path.exists(main_index):
                self.logger.warning("Main index file not found")
                return
            
            # Read the main index
            with open(main_index, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create AI section HTML
            ai_section = f"""
            <div class="card mb-4">
                <div class="card-header">
                    <h2>AI-Enhanced Analysis</h2>
                </div>
                <div class="card-body">
                    <p>Comprehensive AI-enhanced analysis of the forensic artifacts, providing deeper insights and patterns.</p>
                    <a href="{os.path.relpath(os.path.join(ai_report_folder, 'index.html'), report_folder)}" class="btn btn-primary">
                        View AI-Enhanced Analysis
                    </a>
                </div>
            </div>
            """
            
            # Insert before the closing div.container
            modified_content = content.replace('</div>\n</body>', f'{ai_section}</div>\n</body>')
            
            # Write back the modified index
            with open(main_index, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            self.logger.info(f"Added AI section to main index {main_index}")
            
        except Exception as e:
            self.logger.error(f"Error adding AI section to main index: {e}")


# Function to integrate with iLEAPP's artifact processing system
def process_artifact_with_ai(artifact_type, files_found, report_folder, seeker, wrap_text, timezone_offset):
    """
    Wrapper function to process artifacts with AI enhancement.
    This function is designed to be used with iLEAPP's artifact_processor decorator.
    
    Args:
        artifact_type: Type of artifact
        files_found: List of files found for the artifact
        report_folder: Folder to save reports
        seeker: iLEAPP seeker object
        wrap_text: Whether to wrap text in reports
        timezone_offset: Timezone offset for timestamps
    """
    # Get or create the pipeline
    global _pipeline
    if '_pipeline' not in globals():
        try:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            _pipeline = ForensicAnalysisPipeline(api_key)
        except Exception as e:
            logfunc(f"Error initializing AI pipeline: {e}")
            return
    
    # Process with AI
    try:
        _pipeline.process_artifact(artifact_type, files_found, report_folder, seeker, wrap_text, timezone_offset)
    except Exception as e:
        logfunc(f"Error in AI processing: {e}")
