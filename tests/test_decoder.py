"""
Tests for SBW Decoder Module
SBWv1.i2 Mark I Prototype
"""

import pytest
from pathlib import Path
import tempfile
import os

from sbw_cli.core.decoder import SBWDecoder, DecodeResult, BlockHeader
from sbw_cli.utils.config import Config


class TestSBWDecoder:
    """Test cases for SBW decoder functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config.default()
        self.decoder = SBWDecoder(self.config)
        
    def test_decoder_initialization(self):
        """Test decoder initializes correctly."""
        assert self.decoder is not None
        assert self.decoder.config is not None
        assert self.decoder.crypto_processor is not None
        assert self.decoder.compression_processor is not None
        assert self.decoder.tlv_parser is not None
        assert self.decoder.data_exporter is not None
        assert self.decoder.data_visualizer is not None
    
    def test_block_header_parsing(self):
        """Test block header parsing from bytes."""
        # Create test data
        test_data = b'\x00' * 100
        
        # Parse header
        header = BlockHeader.from_bytes(test_data)
        
        assert header is not None
        assert header.raw_size == len(test_data)
        assert header.compressed_size == len(test_data)
        assert header.nonce_size == 12
    
    def test_decode_file_nonexistent(self):
        """Test decode with non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "nonexistent.sbw"
            output_dir = Path(temp_dir) / "output"
            
            result = self.decoder.decode_file(input_file, output_dir)
            
            assert result.success is False
            assert len(result.errors) > 0
    
    def test_decode_file_empty(self):
        """Test decode with empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "empty.sbw"
            output_dir = Path(temp_dir) / "output"
            
            # Create empty file
            input_file.touch()
            
            result = self.decoder.decode_file(input_file, output_dir)
            
            assert result.success is False
            assert len(result.errors) > 0
    
    def test_decode_result_structure(self):
        """Test DecodeResult data structure."""
        result = DecodeResult(success=True)
        
        assert result.success is True
        assert result.blocks_processed == 0
        assert result.files_created == 0
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert len(result.errors) == 0
        assert len(result.warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__])