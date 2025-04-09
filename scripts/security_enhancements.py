"""
Security enhancements for iLEAPP LLM integration.

This module provides security features including:
- Encryption for sensitive data
- Chain-of-custody tracking
- Audit logging for AI-assisted analyses
"""

import os
import json
import hashlib
import logging
import datetime
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class ForensicSecurity:
    """Main class for handling security features in the LLM-enhanced iLEAPP."""
    
    def __init__(self, case_id=None, investigator=None):
        """Initialize the security module.
        
        Args:
            case_id (str): Unique identifier for the case
            investigator (str): Name or ID of the investigator
        """
        self.case_id = case_id or self._generate_case_id()
        self.investigator = investigator
        self.audit_logger = self._setup_audit_logging()
        self.chain_of_custody = []
        self.encryption_key = None
        
    def _generate_case_id(self):
        """Generate a unique case ID based on timestamp and random value."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = os.urandom(4).hex()
        return f"CASE-{timestamp}-{random_suffix}"
    
    def _setup_audit_logging(self):
        """Configure audit logging for the case."""
        logger = logging.getLogger(f"forensic_audit_{self.case_id}")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        log_file = os.path.join(log_dir, f"audit_{self.case_id}.log")
        file_handler = logging.FileHandler(log_file)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def initialize_encryption(self, password=None):
        """Initialize encryption with a password or generate a key.
        
        Args:
            password (str, optional): Password for encryption. If None, a key is generated.
            
        Returns:
            str: Base64 encoded key that should be securely stored
        """
        if password:
            # Derive key from password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            # Store salt securely for later use
            self._store_salt(salt)
        else:
            # Generate a random key
            key = Fernet.generate_key()
            
        self.encryption_key = key
        return key.decode()
    
    def _store_salt(self, salt):
        """Store salt securely for password-based encryption."""
        salt_file = os.path.join(os.getcwd(), "logs", f"salt_{self.case_id}.bin")
        with open(salt_file, 'wb') as f:
            f.write(salt)
        
        # Log the salt storage
        self.audit_logger.info(f"Encryption salt stored at {salt_file}")
        
    def encrypt_data(self, data):
        """Encrypt sensitive data.
        
        Args:
            data (bytes or str): Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        if not self.encryption_key:
            raise ValueError("Encryption not initialized. Call initialize_encryption first.")
            
        if isinstance(data, str):
            data = data.encode()
            
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(data)
        
        # Log encryption event
        data_hash = hashlib.sha256(data).hexdigest()
        self.audit_logger.info(f"Data encrypted: SHA256 hash of original data: {data_hash}")
        
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        """Decrypt encrypted data.
        
        Args:
            encrypted_data (bytes): Encrypted data to decrypt
            
        Returns:
            bytes: Decrypted data
        """
        if not self.encryption_key:
            raise ValueError("Encryption not initialized. Call initialize_encryption first.")
            
        fernet = Fernet(self.encryption_key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Log decryption event
        self.audit_logger.info("Data decryption performed")
        
        return decrypted_data
    
    def add_custody_event(self, action, description, actor=None):
        """Add an event to the chain of custody.
        
        Args:
            action (str): The action performed (e.g., "extract", "analyze", "export")
            description (str): Description of the action
            actor (str, optional): Person performing the action. Defaults to investigator.
        """
        actor = actor or self.investigator
        timestamp = datetime.datetime.now().isoformat()
        
        event = {
            "timestamp": timestamp,
            "action": action,
            "description": description,
            "actor": actor,
            "case_id": self.case_id
        }
        
        # Add event to chain
        self.chain_of_custody.append(event)
        
        # Log the event
        self.audit_logger.info(f"Chain of custody: {action} by {actor}: {description}")
        
        # Save updated chain of custody
        self._save_chain_of_custody()
        
    def _save_chain_of_custody(self):
        """Save the chain of custody to a file."""
        custody_file = os.path.join(os.getcwd(), "logs", f"custody_{self.case_id}.json")
        
        with open(custody_file, 'w') as f:
            json.dump(self.chain_of_custody, f, indent=2)
    
    def log_ai_analysis(self, artifact_type, query, model_used, confidence_score=None):
        """Log an AI-assisted analysis event.
        
        Args:
            artifact_type (str): Type of artifact analyzed
            query (str): The query sent to the AI
            model_used (str): The AI model used
            confidence_score (float, optional): Confidence score if available
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "artifact_type": artifact_type,
            "query": query,
            "model_used": model_used,
            "confidence_score": confidence_score,
            "investigator": self.investigator,
            "case_id": self.case_id
        }
        
        # Log the AI analysis
        self.audit_logger.info(
            f"AI Analysis: {artifact_type} using {model_used} - "
            f"Confidence: {confidence_score or 'N/A'}"
        )
        
        # Add to chain of custody
        self.add_custody_event(
            "ai_analysis",
            f"AI analysis of {artifact_type} using {model_used}",
            self.investigator
        )
        
        # Save detailed AI log
        ai_log_file = os.path.join(os.getcwd(), "logs", f"ai_analysis_{self.case_id}.json")
        
        # Append to existing log if it exists
        if os.path.exists(ai_log_file):
            with open(ai_log_file, 'r') as f:
                try:
                    ai_logs = json.load(f)
                except json.JSONDecodeError:
                    ai_logs = []
        else:
            ai_logs = []
            
        ai_logs.append(log_entry)
        
        with open(ai_log_file, 'w') as f:
            json.dump(ai_logs, f, indent=2)
    
    def generate_integrity_hash(self, file_path):
        """Generate integrity hash for a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: SHA-256 hash of the file
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read and update hash in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        file_hash = sha256_hash.hexdigest()
        
        # Log the hash generation
        self.audit_logger.info(f"Integrity hash generated for {file_path}: {file_hash}")
        
        return file_hash
    
    def verify_integrity(self, file_path, expected_hash):
        """Verify the integrity of a file against an expected hash.
        
        Args:
            file_path (str): Path to the file
            expected_hash (str): Expected SHA-256 hash
            
        Returns:
            bool: True if the hash matches, False otherwise
        """
        current_hash = self.generate_integrity_hash(file_path)
        is_valid = current_hash == expected_hash
        
        # Log the verification
        if is_valid:
            self.audit_logger.info(f"Integrity verified for {file_path}")
        else:
            self.audit_logger.warning(
                f"Integrity check failed for {file_path}. "
                f"Expected: {expected_hash}, Got: {current_hash}"
            )
            
        return is_valid
    
    def export_audit_trail(self, output_path=None):
        """Export the complete audit trail.
        
        Args:
            output_path (str, optional): Path to save the audit trail
            
        Returns:
            str: Path to the exported audit trail
        """
        if not output_path:
            output_path = os.path.join(os.getcwd(), "reports", f"audit_trail_{self.case_id}.json")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Collect all audit information
        audit_data = {
            "case_id": self.case_id,
            "investigator": self.investigator,
            "chain_of_custody": self.chain_of_custody,
            "timestamp": datetime.datetime.now().isoformat(),
            "audit_log_path": os.path.join(os.getcwd(), "logs", f"audit_{self.case_id}.log")
        }
        
        # Write audit trail
        with open(output_path, 'w') as f:
            json.dump(audit_data, f, indent=2)
            
        # Log the export
        self.audit_logger.info(f"Audit trail exported to {output_path}")
        
        return output_path


# Example usage
if __name__ == "__main__":
    # Initialize security for a case
    security = ForensicSecurity(investigator="John Doe")
    
    # Initialize encryption
    key = security.initialize_encryption("secure_password")
    print(f"Encryption key: {key}")
    
    # Add custody events
    security.add_custody_event("extract", "Initial extraction of iPhone data")
    security.add_custody_event("analyze", "Analysis of Messages database")
    
    # Log AI analysis
    security.log_ai_analysis(
        "messages", 
        "Find conversations about meeting locations", 
        "OpenRouter-Claude-3-Opus",
        0.92
    )
    
    # Encrypt sensitive data
    sensitive_data = "Confidential investigation notes"
    encrypted = security.encrypt_data(sensitive_data)
    print(f"Encrypted data: {encrypted}")
    
    # Decrypt data
    decrypted = security.decrypt_data(encrypted)
    print(f"Decrypted data: {decrypted.decode()}")
    
    # Export audit trail
    audit_path = security.export_audit_trail()
    print(f"Audit trail exported to: {audit_path}")
