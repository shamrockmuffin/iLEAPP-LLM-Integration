import os
import sys
import logging
import argparse
from scripts.sample_data_generator import SampleDataGenerator
from scripts.forensic_pipeline import ForensicAnalysisPipeline

# Test script for the LLM-enhanced forensic analysis capabilities
def main():
    """
    Main function to test the LLM-enhanced forensic analysis capabilities.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Test LLM-enhanced forensic analysis capabilities')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--output-dir', default='test_output', help='Directory to save test output')
    parser.add_argument('--sample-data-dir', default='sample_data', help='Directory containing sample data')
    parser.add_argument('--generate-data', action='store_true', help='Generate sample data')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("test_forensic_analysis.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("TestForensicAnalysis")
    
    # Get API key
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OpenRouter API key not provided. Use --api-key or set OPENROUTER_API_KEY environment variable.")
        sys.exit(1)
    
    # Create output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Generate or use existing sample data
    sample_data_dir = os.path.abspath(args.sample_data_dir)
    if args.generate_data or not os.path.exists(sample_data_dir):
        logger.info("Generating sample data...")
        generator = SampleDataGenerator(sample_data_dir)
        generator.generate_all_sample_data()
    else:
        logger.info(f"Using existing sample data from {sample_data_dir}")
    
    # Initialize the forensic analysis pipeline
    try:
        logger.info("Initializing forensic analysis pipeline...")
        pipeline = ForensicAnalysisPipeline(api_key, log_level)
        
        # Process SMS data
        logger.info("Processing SMS data...")
        sms_files = [os.path.join(sample_data_dir, "sms", "sms.db")]
        if os.path.exists(sms_files[0]):
            pipeline.process_artifact("sms", sms_files, output_dir, None, True, "0")
        else:
            logger.warning(f"SMS database not found at {sms_files[0]}")
        
        # Process app usage data
        logger.info("Processing app usage data...")
        app_usage_files = [os.path.join(sample_data_dir, "app_usage", "knowledgeC.db")]
        if os.path.exists(app_usage_files[0]):
            pipeline.process_artifact("app_usage", app_usage_files, output_dir, None, True, "0")
        else:
            logger.warning(f"App usage database not found at {app_usage_files[0]}")
        
        # Process iTunes music data
        logger.info("Processing iTunes music data...")
        itunes_files = [os.path.join(sample_data_dir, "itunes_music", "iTunes.db")]
        if os.path.exists(itunes_files[0]):
            pipeline.process_artifact("itunes_music", itunes_files, output_dir, None, True, "0")
        else:
            logger.warning(f"iTunes database not found at {itunes_files[0]}")
        
        # Process Chrome history data
        logger.info("Processing Chrome history data...")
        chrome_files = [os.path.join(sample_data_dir, "chrome_history", "History")]
        if os.path.exists(chrome_files[0]):
            pipeline.process_artifact("chrome_history", chrome_files, output_dir, None, True, "0")
        else:
            logger.warning(f"Chrome history database not found at {chrome_files[0]}")
        
        # Generate case materials
        logger.info("Generating case materials...")
        all_artifact_data = {
            "sms": pipeline.analysis_results.get("sms", {}),
            "app_usage": pipeline.analysis_results.get("app_usage", {}),
            "itunes_music": pipeline.analysis_results.get("itunes_music", {}),
            "chrome_history": pipeline.analysis_results.get("chrome_history", {})
        }
        pipeline.generate_case_materials(output_dir, all_artifact_data)
        
        logger.info(f"Testing completed successfully. Results saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
