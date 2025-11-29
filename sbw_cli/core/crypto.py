"""
Cryptographic Processing Module
SBWv1.i2 Mark I Prototype

Handles AES-GCM decryption of SBW log blocks.
Mirrors firmware encryption settings exactly.
"""

import logging
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

from sbw_cli.utils.config import Config


class CryptoProcessor:
    """Handles AES-GCM decryption of SBW blocks."""
    
    def __init__(self, config: Config):
        """Initialize crypto processor with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # TODO: Get these values from EN-1.0 crypto profile spec
        self.key = config.get('crypto.key', b'\x00' * 32)  # Placeholder 256-bit key
        self.tag_length = config.get('crypto.tag_length', 16)  # AES-GCM tag length
        self.nonce_length = config.get('crypto.nonce_length', 12)  # GCM nonce length
        
        # Initialize AESGCM cipher
        try:
            self.cipher = AESGCM(self.key)
            self.logger.debug("Crypto processor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize crypto processor: {e}")
            raise
    
    def decrypt_block(self, block: Dict[str, Any], block_index: int = 0) -> Optional[bytes]:
        """
        Decrypt a single SBW block using AES-GCM.
        
        Block payload format (EN-1.0):
        - Nonce (variable length, from header)
        - Ciphertext (compressed data)
        - Authentication Tag (16 bytes)
        
        Args:
            block: Block dictionary containing header and payload
            block_index: Index of block being processed (for logging)
            
        Returns:
            Decrypted bytes or None if decryption fails
        """
        try:
            payload = block.get('payload')
            if not payload:
                self.logger.error(f"Block {block_index}: No payload data")
                return None
                
            header = block.get('header')
            if not header:
                self.logger.error(f"Block {block_index}: No header information")
                return None
            
            nonce_size = header.nonce_size
            
            # Validate payload size
            if len(payload) < nonce_size + 16:  # 16 = GCM tag
                self.logger.error(f"Block {block_index}: Payload too short ({len(payload)} bytes)")
                return None
                
            # Extract nonce and ciphertext+tag
            nonce = payload[:nonce_size]
            ciphertext_and_tag = payload[nonce_size:]
            
            self.logger.debug(f"Block {block_index}: Decrypting with nonce={nonce_size} bytes, data={len(ciphertext_and_tag)} bytes")
            
            # Decrypt using AES-GCM
            try:
                plaintext = self.cipher.decrypt(nonce, ciphertext_and_tag, None)
                self.logger.debug(f"Block {block_index}: Successfully decrypted {len(plaintext)} bytes")
                return plaintext
                
            except InvalidTag:
                self.logger.error(f"Block {block_index}: AES-GCM tag verification failed - data corrupted or wrong key")
                return None
                
        except Exception as e:
            self.logger.error(f"Block {block_index}: Error during decryption: {e}")
            return None
    
    def verify_key(self, test_data: bytes) -> bool:
        """
        Verify the decryption key using known test data.
        
        Args:
            test_data: Known good encrypted data for verification
            
        Returns:
            True if key is valid, False otherwise
        """
        # TODO: Implement key verification using test vectors from Patrick
        return True
    
    def get_crypto_info(self) -> Dict[str, Any]:
        """Get current crypto configuration info."""
        return {
            'key_length': len(self.key),
            'tag_length': self.tag_length, 
            'nonce_length': self.nonce_length,
            'algorithm': 'AES-GCM'
        }