"""
Core SBW Decoder Module
SBWv1.i2 Mark I Prototype

Main decoder class that orchestrates the decoding pipeline:
Decode → Decrypt → Decompress → Parse TLV → Export/Visualize
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from sbw_cli.core.crypto import CryptoProcessor
from sbw_cli.core.compression import CompressionProcessor  
from sbw_cli.core.tlv_parser import TLVParser
from sbw_cli.core.exporter import DataExporter
from sbw_cli.core.visualizer import DataVisualizer
from sbw_cli.utils.config import Config


@dataclass
class DecodeResult:
    """Result of a decode operation."""
    success: bool
    blocks_processed: int = 0
    files_created: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class BlockHeader:
    """SBW block header information."""
    offset: int
    raw_size: int
    compressed_size: int
    flags: int
    nonce_size: int
    block_id: int
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "BlockHeader":
        """Parse block header from raw bytes (placeholder implementation)."""
        # TODO: Implement actual parsing based on LG-1.0 spec from Patrick
        return cls(
            offset=0,
            raw_size=len(data),
            compressed_size=len(data),
            flags=0,
            nonce_size=12,
            block_id=0
        )


class SBWDecoder:
    """Main SBW decoder class."""
    
    def __init__(self, config: Config):
        """Initialize the decoder with configuration."""
        self.config = config
        self.crypto_processor = CryptoProcessor(config)
        self.compression_processor = CompressionProcessor(config)
        self.tlv_parser = TLVParser(config)
        self.data_exporter = DataExporter(config)
        self.data_visualizer = DataVisualizer(config)
        
        self.logger = logging.getLogger(__name__)
        
    def decode_file(
        self,
        input_file: Path,
        output_dir: Path,
        export_csv: bool = False,
        export_json: bool = False,
        generate_plots: bool = False
    ) -> DecodeResult:
        """
        Decode an SBW log file through the complete pipeline.
        
        Args:
            input_file: Path to the .sbw file
            output_dir: Directory for output files
            export_csv: Whether to export CSV files
            export_json: Whether to export JSON files
            generate_plots: Whether to generate visualization plots
            
        Returns:
            DecodeResult with operation status and metrics
        """
        result = DecodeResult(success=False)
        
        try:
            self.logger.info(f"Starting decode of {input_file}")
            
            # Read the input file
            raw_data = self._read_file(input_file)
            if not raw_data:
                result.errors.append("Failed to read input file")
                return result
                
            # Parse blocks from the file
            blocks = self._parse_blocks(raw_data)
            if not blocks:
                result.errors.append("No valid blocks found in file")
                return result
                
            self.logger.info(f"Found {len(blocks)} blocks to process")
            
            # Process each block through the pipeline
            decoded_data = []
            processed_count = 0
            
            for i, block in enumerate(blocks):
                try:
                    self.logger.debug(f"Processing block {i+1}/{len(blocks)}")
                    
                    # Decrypt the block
                    decrypted_data = self.crypto_processor.decrypt_block(block)
                    if not decrypted_data:
                        result.errors.append(f"Failed to decrypt block {i+1}")
                        continue
                        
                    # Decompress the block
                    decompressed_data = self.compression_processor.decompress_block(decrypted_data)
                    if not decompressed_data:
                        result.errors.append(f"Failed to decompress block {i+1}")
                        continue
                        
                    # Parse TLV data
                    tlv_data = self.tlv_parser.parse_block(decompressed_data)
                    if tlv_data:
                        decoded_data.extend(tlv_data)
                        processed_count += 1
                    else:
                        result.warnings.append(f"No valid TLV data in block {i+1}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing block {i+1}: {e}")
                    result.errors.append(f"Block {i+1} processing failed: {str(e)}")
                    
            result.blocks_processed = processed_count
            
            if not decoded_data:
                result.errors.append("No data successfully decoded from any blocks")
                return result
                
            self.logger.info(f"Successfully decoded {len(decoded_data)} data records")
            
            # Export data if requested
            files_created = 0
            
            if export_csv:
                csv_files = self.data_exporter.export_csv(decoded_data, output_dir)
                files_created += len(csv_files)
                
            if export_json:
                json_files = self.data_exporter.export_json(decoded_data, output_dir)  
                files_created += len(json_files)
                
            # Generate plots if requested
            if generate_plots:
                plot_files = self.data_visualizer.generate_plots(decoded_data, output_dir)
                files_created += len(plot_files)
                
            result.files_created = files_created
            result.success = True
            
            self.logger.info(f"Decode operation completed successfully")
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during decode: {e}")
            result.errors.append(f"Unexpected error: {str(e)}")
            
        return result
    
    def _read_file(self, file_path: Path) -> Optional[bytes]:
        """Read the SBW file data."""
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return None
            
    def _parse_blocks(self, data: bytes) -> List[Dict[str, Any]]:
        """
        Parse blocks from raw SBW file data.
        
        This is a placeholder implementation that will be replaced
        with actual block parsing based on the LG-1.0 specification.
        """
        blocks = []
        
        # TODO: Implement actual block parsing based on LG-1.0 spec
        # For now, create a single block with all data
        if data:
            header = BlockHeader.from_bytes(data)
            blocks.append({
                "header": header,
                "data": data,
                "encrypted": True,
                "compressed": True
            })
            
        self.logger.debug(f"Parsed {len(blocks)} blocks from file")
        return blocks