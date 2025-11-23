"""
Data Export Module
SBWv1.i2 Mark I Prototype

Exports parsed TLV data to CSV and JSON formats.
Well-structured, column-aligned, timestamped data output.
"""

import logging
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pandas as pd

from sbw_cli.core.tlv_parser import TLVRecord
from sbw_cli.utils.config import Config


class DataExporter:
    """Handles export of parsed TLV data to various formats."""
    
    def __init__(self, config: Config):
        """Initialize data exporter with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Export settings
        self.timestamp_format = config.get('export.timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
        self.csv_delimiter = config.get('export.csv_delimiter', ',')
        self.json_indent = config.get('export.json_indent', 2)
        
    def export_csv(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """
        Export TLV records to CSV files.
        
        Creates separate CSV files for each data type (IMU, Temperature, Health, etc.)
        
        Args:
            records: List of parsed TLV records
            output_dir: Directory for CSV output files
            
        Returns:
            List of created CSV file paths
        """
        created_files = []
        
        try:
            self.logger.info(f"Exporting {len(records)} records to CSV format")
            
            # Group records by data type
            grouped_data = self._group_records_by_type(records)
            
            for data_type, type_records in grouped_data.items():
                if not type_records:
                    continue
                    
                csv_file = output_dir / f"{data_type}_data.csv"
                
                if data_type == 'imu':
                    self._export_imu_csv(type_records, csv_file)
                elif data_type == 'temperature':
                    self._export_temperature_csv(type_records, csv_file)
                elif data_type == 'health':
                    self._export_health_csv(type_records, csv_file)
                else:
                    self._export_generic_csv(type_records, csv_file, data_type)
                    
                created_files.append(csv_file)
                self.logger.info(f"Created CSV file: {csv_file}")
                
        except Exception as e:
            self.logger.error(f"Error during CSV export: {e}")
            
        return created_files
    
    def export_json(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """
        Export TLV records to JSON files.
        
        Args:
            records: List of parsed TLV records
            output_dir: Directory for JSON output files
            
        Returns:
            List of created JSON file paths
        """
        created_files = []
        
        try:
            self.logger.info(f"Exporting {len(records)} records to JSON format")
            
            # Create complete export with all data
            all_data_file = output_dir / "sbw_data_complete.json"
            self._export_complete_json(records, all_data_file)
            created_files.append(all_data_file)
            
            # Group records by data type for separate files
            grouped_data = self._group_records_by_type(records)
            
            for data_type, type_records in grouped_data.items():
                if not type_records:
                    continue
                    
                json_file = output_dir / f"{data_type}_data.json"
                self._export_typed_json(type_records, json_file, data_type)
                created_files.append(json_file)
                self.logger.info(f"Created JSON file: {json_file}")
                
        except Exception as e:
            self.logger.error(f"Error during JSON export: {e}")
            
        return created_files
    
    def _group_records_by_type(self, records: List[TLVRecord]) -> Dict[str, List[TLVRecord]]:
        """Group TLV records by their data type."""
        grouped = {}
        
        for record in records:
            data_type = record.data_type
            if data_type not in grouped:
                grouped[data_type] = []
            grouped[data_type].append(record)
            
        return grouped
    
    def _export_imu_csv(self, records: List[TLVRecord], csv_file: Path) -> None:
        """Export IMU data to CSV format."""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.csv_delimiter)
            
            # Write header
            writer.writerow([
                'timestamp', 'accel_x', 'accel_y', 'accel_z',
                'gyro_x', 'gyro_y', 'gyro_z'
            ])
            
            # Write data rows
            for record in records:
                data = record.data
                writer.writerow([
                    record.timestamp.strftime(self.timestamp_format),
                    data.get('accel_x', 0.0),
                    data.get('accel_y', 0.0), 
                    data.get('accel_z', 0.0),
                    data.get('gyro_x', 0.0),
                    data.get('gyro_y', 0.0),
                    data.get('gyro_z', 0.0)
                ])
    
    def _export_temperature_csv(self, records: List[TLVRecord], csv_file: Path) -> None:
        """Export temperature data to CSV format."""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.csv_delimiter)
            
            # Write header
            writer.writerow(['timestamp', 'temperature', 'sensor_id'])
            
            # Write data rows
            for record in records:
                data = record.data
                writer.writerow([
                    record.timestamp.strftime(self.timestamp_format),
                    data.get('temperature', 0.0),
                    data.get('sensor_id', 0)
                ])
    
    def _export_health_csv(self, records: List[TLVRecord], csv_file: Path) -> None:
        """Export health data to CSV format."""
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.csv_delimiter)
            
            # Write header
            writer.writerow([
                'timestamp', 'battery_voltage', 'cpu_temperature', 
                'memory_usage', 'error_code'
            ])
            
            # Write data rows
            for record in records:
                data = record.data
                writer.writerow([
                    record.timestamp.strftime(self.timestamp_format),
                    data.get('battery_voltage', 0.0),
                    data.get('cpu_temperature', 0.0),
                    data.get('memory_usage', 0),
                    data.get('error_code', 0)
                ])
    
    def _export_generic_csv(self, records: List[TLVRecord], csv_file: Path, data_type: str) -> None:
        """Export generic data type to CSV format."""
        if not records:
            return
            
        # Get all possible keys from the data
        all_keys = set()
        for record in records:
            all_keys.update(record.data.keys())
            
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.csv_delimiter)
            
            # Write header
            header = ['timestamp'] + sorted(all_keys)
            writer.writerow(header)
            
            # Write data rows
            for record in records:
                row = [record.timestamp.strftime(self.timestamp_format)]
                for key in sorted(all_keys):
                    row.append(record.data.get(key, ''))
                writer.writerow(row)
    
    def _export_complete_json(self, records: List[TLVRecord], json_file: Path) -> None:
        """Export all records to a single comprehensive JSON file."""
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'total_records': len(records),
                'sbw_version': 'v1.i2',
                'format_version': '1.0'
            },
            'records': []
        }
        
        for record in records:
            record_data = {
                'timestamp': record.timestamp.isoformat(),
                'data_type': record.data_type,
                'tlv_type': record.raw_tlv_type,
                'tlv_length': record.raw_tlv_length,
                'data': record.data
            }
            export_data['records'].append(record_data)
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.json_indent, default=str)
    
    def _export_typed_json(self, records: List[TLVRecord], json_file: Path, data_type: str) -> None:
        """Export records of a specific type to JSON."""
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'data_type': data_type,
                'record_count': len(records),
                'sbw_version': 'v1.i2'
            },
            'data': []
        }
        
        for record in records:
            record_data = {
                'timestamp': record.timestamp.isoformat(),
                **record.data
            }
            export_data['data'].append(record_data)
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.json_indent, default=str)