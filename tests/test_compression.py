"""
Tests for Compression Processing Module
SBWv1.i2 Mark I Prototype
"""

import pytest
from pathlib import Path

from sbw_cli.core.compression import CompressionProcessor
from sbw_cli.utils.config import Config


class TestCompressionProcessor:
    """Test cases for compression processor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config.default()
        self.processor = CompressionProcessor(self.config)
    
    def test_compression_initialization(self):
        """Test compression processor initializes correctly."""
        assert self.processor is not None
        assert self.processor.algorithm == 'lz4'
    
    def test_compression_info(self):
        """Test getting compression configuration info."""
        info = self.processor.get_compression_info()
        
        assert info['algorithm'] == 'lz4'
        assert 'lz4_available' in info
    
    def test_decompress_block_empty_data(self):
        """Test decompress with empty data."""
        result = self.processor.decompress_block(b'')
        assert result is None
    
    def test_decompress_block_none_data(self):
        """Test decompress with None data."""
        result = self.processor.decompress_block(None)
        assert result is None
    
    def test_decompress_block_invalid_lz4(self):
        """Test decompress with invalid LZ4 data."""
        # Invalid LZ4 data - should fail gracefully
        invalid_data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        result = self.processor.decompress_block(invalid_data)
        assert result is None
    
    def test_detect_compression(self):
        """Test compression algorithm detection."""
        algorithm = self.processor.detect_compression(b'test data')
        assert algorithm == 'lz4'


if __name__ == "__main__":
    pytest.main([__file__])
