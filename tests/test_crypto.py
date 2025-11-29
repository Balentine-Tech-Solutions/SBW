"""
Tests for Cryptographic Processing Module
SBWv1.i2 Mark I Prototype
"""

import pytest
from pathlib import Path
import struct

from sbw_cli.core.crypto import CryptoProcessor
from sbw_cli.utils.config import Config


class TestCryptoProcessor:
    """Test cases for crypto processor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config.default()
        self.processor = CryptoProcessor(self.config)
    
    def test_crypto_initialization(self):
        """Test crypto processor initializes correctly."""
        assert self.processor is not None
        assert self.processor.key is not None
        assert self.processor.tag_length == 16
        assert self.processor.nonce_length == 12
        assert self.processor.cipher is not None
    
    def test_crypto_info(self):
        """Test getting crypto configuration info."""
        info = self.processor.get_crypto_info()
        
        assert info['key_length'] == 32
        assert info['tag_length'] == 16
        assert info['nonce_length'] == 12
        assert info['algorithm'] == 'AES-GCM'
    
    def test_decrypt_block_missing_payload(self):
        """Test decrypt block with missing payload."""
        block = {
            'header': None,
            'payload': None
        }
        
        result = self.processor.decrypt_block(block)
        assert result is None
    
    def test_decrypt_block_missing_header(self):
        """Test decrypt block with missing header."""
        block = {
            'header': None,
            'payload': b'test data'
        }
        
        result = self.processor.decrypt_block(block)
        assert result is None
    
    def test_decrypt_block_short_payload(self):
        """Test decrypt block with payload too short."""
        class MockHeader:
            nonce_size = 12
        
        block = {
            'header': MockHeader(),
            'payload': b'short'
        }
        
        result = self.processor.decrypt_block(block)
        assert result is None
    
    def test_decrypt_block_invalid_tag(self):
        """Test decrypt block with invalid authentication tag."""
        class MockHeader:
            nonce_size = 12
        
        # Create invalid encrypted data with correct size but wrong tag
        nonce = b'\x00' * 12
        ciphertext = b'\x00' * 16
        invalid_block = {
            'header': MockHeader(),
            'payload': nonce + ciphertext
        }
        
        result = self.processor.decrypt_block(invalid_block)
        # Should return None due to tag verification failure
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
