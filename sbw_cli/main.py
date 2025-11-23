"""
Main CLI Entry Point for SBW CLI Tool
SBWv1.i2 Mark I Prototype

Usage: 
    sbw-cli decode input.sbw --out output_dir [--csv] [--json] [--plots]
    decode input.sbw --out output_dir [--csv] [--json] [--plots]
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from sbw_cli.core.decoder import SBWDecoder
from sbw_cli.utils.logger import setup_logging
from sbw_cli.utils.config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="sbw-cli",
        description="SBW CLI Tool for decoding, decrypting, and visualizing SBW log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sbw-cli decode input.sbw --out decoded_data/
  sbw-cli decode input.sbw --out results/ --csv --json --plots
  sbw-cli decode input.sbw --out analysis/ --verbose
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Decode command
    decode_parser = subparsers.add_parser(
        "decode", 
        help="Decode an SBW log file"
    )
    decode_parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the SBW log file (.sbw)"
    )
    decode_parser.add_argument(
        "--out", "-o",
        type=Path,
        required=True,
        help="Output directory for decoded data"
    )
    decode_parser.add_argument(
        "--csv",
        action="store_true",
        help="Export data to CSV format"
    )
    decode_parser.add_argument(
        "--json", 
        action="store_true",
        help="Export data to JSON format"
    )
    decode_parser.add_argument(
        "--plots",
        action="store_true", 
        help="Generate visualization plots"
    )
    decode_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    decode_parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to configuration file"
    )
    
    return parser


def validate_input_file(input_file: Path) -> bool:
    """Validate the input SBW file."""
    if not input_file.exists():
        logging.error(f"Input file does not exist: {input_file}")
        return False
        
    if input_file.suffix.lower() != ".sbw":
        logging.warning(f"Input file does not have .sbw extension: {input_file}")
        
    if input_file.stat().st_size == 0:
        logging.error(f"Input file is empty: {input_file}")
        return False
        
    return True


def create_output_directory(output_dir: Path) -> bool:
    """Create output directory if it doesn't exist."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create output directory {output_dir}: {e}")
        return False


def decode_command(args) -> int:
    """Execute the decode command."""
    # Validate input file
    if not validate_input_file(args.input_file):
        return 1
        
    # Create output directory
    if not create_output_directory(args.out):
        return 1
    
    try:
        logging.info(f"Starting decode operation...")
        logging.info(f"Input file: {args.input_file}")
        logging.info(f"Output directory: {args.out}")
        
        # Load configuration
        config = Config.load(args.config) if args.config else Config.default()
        
        # Initialize decoder
        decoder = SBWDecoder(config)
        
        # Perform decoding
        result = decoder.decode_file(
            input_file=args.input_file,
            output_dir=args.out,
            export_csv=args.csv,
            export_json=args.json, 
            generate_plots=args.plots
        )
        
        if result.success:
            logging.info("Decode operation completed successfully!")
            logging.info(f"Processed {result.blocks_processed} blocks")
            logging.info(f"Generated {result.files_created} output files")
            
            if result.errors:
                logging.warning(f"Encountered {len(result.errors)} non-fatal errors:")
                for error in result.errors:
                    logging.warning(f"  - {error}")
                    
            return 0
        else:
            logging.error("Decode operation failed!")
            for error in result.errors:
                logging.error(f"  - {error}")
            return 1
            
    except Exception as e:
        logging.exception(f"Unexpected error during decode operation: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO
    setup_logging(level=log_level)
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "decode":
        return decode_command(args)
    else:
        logging.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())