"""
Decompression Processing Module
SBWv1.i2 Mark I Prototype

Handles decompression of SBW log blocks using LZ4 or Heatshrink.
Mirrors firmware compression settings exactly.
"""

import logging
from typing import Optional, Dict, Any

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False
    
from sbw_cli.utils.config import Config


class CompressionProcessor:
    """Handles decompression of SBW blocks."""
    
    def __init__(self, config: Config):
        """Initialize compression processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get compression algorithm from config
        self.algorithm = config.get('compression.algorithm', 'lz4')
        
        # Validate algorithm availability
        if self.algorithm == 'lz4' and not LZ4_AVAILABLE:
            raise RuntimeError("LZ4 library not available. Install with: pip install lz4")
            
        self.logger.debug(f"Compression processor initialized with {self.algorithm}")
    
    def decompress_block(self, compressed_data: bytes) -> Optional[bytes]:
        """
        Decompress a single SBW block.
        
        Args:
            compressed_data: Compressed bytes from decryption
            
        Returns:
            Decompressed bytes or None if decompression fails
        """
        try:
            if not compressed_data:
                self.logger.error("No data to decompress")
                return None
                
            self.logger.debug(f"Decompressing {len(compressed_data)} bytes using {self.algorithm}")
            
            if self.algorithm == 'lz4':
                return self._decompress_lz4(compressed_data)
            elif self.algorithm == 'heatshrink':
                return self._decompress_heatshrink(compressed_data)
            else:
                self.logger.error(f"Unsupported compression algorithm: {self.algorithm}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error during decompression: {e}")
            return None
    
    def _decompress_lz4(self, data: bytes) -> Optional[bytes]:
        """Decompress LZ4 compressed data."""
        try:
            decompressed = lz4.frame.decompress(data)
            self.logger.debug(f"LZ4 decompression: {len(data)} -> {len(decompressed)} bytes")
            return decompressed
        except Exception as e:
            self.logger.error(f"LZ4 decompression failed: {e}")
            return None
    
    def _decompress_heatshrink(self, data: bytes) -> Optional[bytes]:
        """Decompress Heatshrink compressed data."""
        # TODO: Implement Heatshrink decompression
        # This will require either:
        # 1. Python bindings for Heatshrink library
        # 2. Custom implementation based on firmware settings
        self.logger.warning("Heatshrink decompression not yet implemented")
        
        # For now, assume data is not compressed if using Heatshrink
        return data
    
    def detect_compression(self, data: bytes) -> str:
        """
        Detect compression algorithm used in data.
        
        Args:
            data: Raw data to analyze
            
        Returns:
            Detected compression algorithm name
        """
        # TODO: Implement compression detection based on block headers/magic bytes
        return self.algorithm
    
    def get_compression_info(self) -> Dict[str, Any]:
        """Get current compression configuration info."""
        return {
            'algorithm': self.algorithm,
            'lz4_available': LZ4_AVAILABLE
        }