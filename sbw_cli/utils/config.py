"""
Configuration Management Module
SBWv1.i2 Mark I Prototype

Manages configuration settings for the SBW CLI tool.
Supports loading from files and providing defaults.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union


class Config:
    """Configuration manager for SBW CLI tool."""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        """Initialize configuration with provided data."""
        self._config = config_data or {}
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def default(cls) -> "Config":
        """Create configuration with default settings."""
        default_config = {
            # Crypto settings (placeholders until EN-1.0 spec is provided)
            'crypto': {
                'key': b'\x00' * 32,  # 256-bit key placeholder
                'algorithm': 'AES-GCM',
                'tag_length': 16,
                'nonce_length': 12
            },
            
            # Compression settings
            'compression': {
                'algorithm': 'lz4',  # or 'heatshrink'
                'level': 'default'
            },
            
            # TLV parsing settings (placeholders until TL-1.0 spec is provided)
            'tlv': {
                'version': '1.0',
                'byte_order': 'little',  # or 'big'
                'alignment': 4
            },
            
            # Export settings
            'export': {
                'timestamp_format': '%Y-%m-%d %H:%M:%S.%f',
                'csv_delimiter': ',',
                'json_indent': 2
            },
            
            # Visualization settings
            'visualization': {
                'figure_size': (12, 8),
                'dpi': 300,
                'style': 'default'
            },
            
            # Logging settings
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_logging': False,
                'log_file': 'sbw_cli.log'
            }
        }
        
        return cls(default_config)
    
    @classmethod
    def load(cls, config_path: Path) -> "Config":
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
            
        Returns:
            Config instance with loaded settings
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    try:
                        import yaml
                        config_data = yaml.safe_load(f)
                    except ImportError:
                        raise ImportError("PyYAML required for YAML config files. Install with: pip install pyyaml")
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
                    
            # Merge with defaults
            default_instance = cls.default()
            merged_config = default_instance._merge_configs(default_instance._config, config_data)
            
            return cls(merged_config)
            
        except Exception as e:
            raise RuntimeError(f"Error loading configuration from {config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'crypto.key')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'crypto.key')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
        """
        self._config = self._merge_configs(self._config, updates)
    
    def save(self, config_path: Path) -> None:
        """
        Save configuration to a file.
        
        Args:
            config_path: Path where to save the configuration
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(self._config, f, indent=2, default=str)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    try:
                        import yaml
                        yaml.safe_dump(self._config, f, default_flow_style=False)
                    except ImportError:
                        raise ImportError("PyYAML required for YAML config files. Install with: pip install pyyaml")
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
                    
        except Exception as e:
            raise RuntimeError(f"Error saving configuration to {config_path}: {e}")
    
    def _merge_configs(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        merged = base.copy()
        
        for key, value in updates.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
    
    def __repr__(self) -> str:
        return f"Config({self._config})"