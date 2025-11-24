"""
Security Utilities Module
SBWv1.i2 Mark I Prototype - Defense Weapons Development

Handles security considerations for defense applications:
- ITAR compliance logging
- Classification handling
- Audit trails
- Secure operations
"""

import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


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