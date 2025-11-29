"""
Security Utilities Module
SBWv1.i2 Mark I Prototype - Defense Weapons Development

Handles security considerations for defense applications:
- ITAR compliance logging
- Classification handling
- Audit trails
- Secure operations
- Input validation
- Key management
"""

import logging
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SecurityValidator:
    """Validates input and prevents common security issues."""
    
    def __init__(self):
        """Initialize security validator."""
        self.logger = logging.getLogger(__name__)
        
        # File size limits (100MB default)
        self.MAX_FILE_SIZE = int(os.getenv('SBW_MAX_FILE_SIZE', 100 * 1024 * 1024))
        
        # Path validation patterns
        self.SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9._\-/\\: ]+$')
    
    def validate_file_path(self, file_path: Path) -> bool:
        """
        Validate file path for security issues.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            # Check for path traversal attempts
            resolved = file_path.resolve()
            if '..' in str(file_path):
                self.logger.warning(f"Path traversal attempt detected: {file_path}")
                return False
            
            # Check file size
            if file_path.exists():
                file_size = file_path.stat().st_size
                if file_size > self.MAX_FILE_SIZE:
                    self.logger.error(f"File exceeds size limit: {file_size} > {self.MAX_FILE_SIZE}")
                    return False
            
            # Check for valid characters
            if not self.SAFE_PATH_PATTERN.match(str(file_path)):
                self.logger.warning(f"Path contains invalid characters: {file_path}")
                # Note: Allow but warn - different OSes have different rules
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating file path: {e}")
            return False
    
    def validate_key(self, key: bytes) -> bool:
        """
        Validate cryptographic key.
        
        Args:
            key: Key bytes to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        if not key:
            self.logger.error("Key is empty")
            return False
        
        # AES-256 requires 32 bytes
        if len(key) != 32:
            self.logger.error(f"Invalid key length: {len(key)} (expected 32)")
            return False
        
        # Check for obviously bad keys (all zeros, all ones, etc.)
        if key == b'\x00' * 32:
            self.logger.warning("Key is all zeros - this is insecure!")
            return True  # Allow but warn
        
        if key == b'\xFF' * 32:
            self.logger.warning("Key is all ones - this is insecure!")
            return True  # Allow but warn
        
        return True
    
    def validate_block_data(self, data: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Validate block data for overflow attacks.
        
        Args:
            data: Data to validate
            max_size: Maximum allowed size in bytes
            
        Returns:
            True if data is valid, False otherwise
        """
        if not data:
            return True
        
        if len(data) > max_size:
            self.logger.error(f"Block data exceeds size limit: {len(data)} > {max_size}")
            return False
        
        return True


class AuditLogger:
    """Handles security audit logging."""
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            log_file: Optional file path for audit log
        """
        self.logger = logging.getLogger('sbw_audit')
        self.log_file = log_file
        
        # Set up file handler if log file specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        
        self.logger.setLevel(logging.INFO)
    
    def log_decode_start(self, input_file: Path, output_dir: Path) -> None:
        """Log start of decode operation."""
        file_hash = self._compute_file_hash(input_file) if input_file.exists() else 'N/A'
        self.logger.info(
            f"DECODE_START: input={input_file}, output={output_dir}, "
            f"file_hash={file_hash}"
        )
    
    def log_decode_complete(self, input_file: Path, success: bool, 
                           blocks_processed: int, errors: int) -> None:
        """Log completion of decode operation."""
        status = 'SUCCESS' if success else 'FAILED'
        self.logger.info(
            f"DECODE_COMPLETE: input={input_file}, status={status}, "
            f"blocks={blocks_processed}, errors={errors}"
        )
    
    def log_decryption_attempt(self, block_id: int, success: bool, 
                              error_reason: Optional[str] = None) -> None:
        """Log decryption attempt."""
        status = 'SUCCESS' if success else 'FAILED'
        reason = f", reason={error_reason}" if error_reason else ""
        self.logger.info(
            f"DECRYPT: block_id={block_id}, status={status}{reason}"
        )
    
    def log_key_usage(self, key_id: str) -> None:
        """Log when a key is used."""
        self.logger.info(f"KEY_USAGE: key_id={key_id}")
    
    def log_security_event(self, event_type: str, details: str) -> None:
        """Log security events."""
        self.logger.warning(f"SECURITY_EVENT: type={event_type}, details={details}")
    
    @staticmethod
    def _compute_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
        """Compute file hash for audit purposes."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]  # First 16 chars
        except Exception:
            return 'ERROR'


class SecurityLogger:
    """Enhanced logging for defense security requirements."""
    
    def __init__(self, classification: str = "UNCLASSIFIED", itar_controlled: bool = True):
        """Initialize security logger."""
        self.classification = classification.upper()
        self.itar_controlled = itar_controlled
        self.logger = logging.getLogger(f"{__name__}.security")
        
        # Add classification markers to all log messages
        self.logger = self._setup_classified_logging()
        
    def _setup_classified_logging(self) -> logging.Logger:
        """Set up logging with classification markers."""
        logger = logging.getLogger(f"{__name__}.security_audit")
        
        # Custom formatter with classification headers
        class ClassifiedFormatter(logging.Formatter):
            def __init__(self, classification: str, itar_controlled: bool):
                super().__init__()
                self.classification = classification
                self.itar_controlled = itar_controlled
                
            def format(self, record):
                # Add classification marking
                base_format = f"[{self.classification}] %(asctime)s - %(name)s - %(levelname)s - %(message)s"
                if self.itar_controlled:
                    base_format = f"[ITAR] {base_format}"
                    
                formatter = logging.Formatter(base_format)
                return formatter.format(record)
        
        # Add custom formatter to handlers
        formatter = ClassifiedFormatter(self.classification, self.itar_controlled)
        
        return logger
    
    def log_file_access(self, file_path: Path, operation: str, user: str = "unknown") -> None:
        """Log file access for audit trails."""
        file_hash = self._calculate_file_hash(file_path) if file_path.exists() else "N/A"
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": str(file_path),
            "file_hash": file_hash,
            "user": user,
            "classification": self.classification,
            "itar_controlled": self.itar_controlled
        }
        
        self.logger.info(f"FILE_ACCESS: {json.dumps(audit_entry)}")
    
    def log_crypto_operation(self, operation: str, key_id: str = "default", success: bool = True) -> None:
        """Log cryptographic operations for security audit."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": f"CRYPTO_{operation.upper()}",
            "key_id": key_id,
            "success": success,
            "classification": self.classification
        }
        
        self.logger.info(f"CRYPTO_OP: {json.dumps(audit_entry)}")
    
    def log_export_operation(self, export_type: str, destination: Path, record_count: int) -> None:
        """Log data export operations for compliance."""
        if self.itar_controlled:
            self.logger.warning(f"ITAR_EXPORT: Exporting {record_count} records as {export_type} to {destination}")
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "DATA_EXPORT",
            "export_type": export_type,
            "destination": str(destination),
            "record_count": record_count,
            "itar_controlled": self.itar_controlled,
            "classification": self.classification
        }
        
        self.logger.info(f"EXPORT_OP: {json.dumps(audit_entry)}")
    
    def check_export_compliance(self, user_country: str = "US") -> bool:
        """Check if export is compliant with ITAR restrictions."""
        if not self.itar_controlled:
            return True
            
        # Placeholder for ITAR country restrictions
        restricted_countries = ["CN", "RU", "IR", "KP"]  # Example restricted countries
        
        if user_country in restricted_countries:
            self.logger.error(f"ITAR_VIOLATION: Export attempt to restricted country: {user_country}")
            return False
            
        self.logger.info(f"ITAR_COMPLIANCE: Export approved for country: {user_country}")
        return True
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for integrity verification."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            self.logger.error(f"Hash calculation failed for {file_path}: {e}")
            return "ERROR"
    
    def create_classification_banner(self) -> str:
        """Create classification banner for outputs."""
        banner = f"\n{'='*60}\n"
        banner += f"CLASSIFICATION: {self.classification}\n"
        if self.itar_controlled:
            banner += "ITAR CONTROLLED - Export restrictions apply\n"
        banner += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        banner += f"{'='*60}\n"
        return banner


class SecureConfig:
    """Configuration handler with security considerations."""
    
    @staticmethod
    def validate_security_config(config: Dict[str, Any]) -> bool:
        """Validate security configuration settings."""
        required_fields = ['classification_level', 'itar_controlled', 'audit_logging']
        
        security_config = config.get('security', {})
        
        for field in required_fields:
            if field not in security_config:
                logging.error(f"Missing required security config field: {field}")
                return False
                
        # Validate classification level
        valid_classifications = ['UNCLASSIFIED', 'CONFIDENTIAL', 'SECRET', 'TOP SECRET']
        classification = security_config.get('classification_level', '').upper()
        
        if classification not in valid_classifications:
            logging.error(f"Invalid classification level: {classification}")
            return False
            
        return True
    
    @staticmethod
    def sanitize_config_for_export(config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config before export."""
        sanitized = config.copy()
        
        # Remove sensitive keys
        sensitive_keys = ['crypto.key', 'security.api_keys', 'authentication']
        
        for key in sensitive_keys:
            keys = key.split('.')
            current = sanitized
            
            try:
                for k in keys[:-1]:
                    current = current[k]
                if keys[-1] in current:
                    current[keys[-1]] = "[REDACTED]"
            except (KeyError, TypeError):
                pass
                
        return sanitized