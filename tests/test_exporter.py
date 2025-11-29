"""
Tests for Data Export Module
SBWv1.i2 Mark I Prototype
"""

import pytest
from pathlib import Path
import tempfile
import csv
import json
from datetime import datetime

from sbw_cli.core.exporter import DataExporter
from sbw_cli.core.tlv_parser import TLVRecord
from sbw_cli.utils.config import Config


class TestDataExporter:
    """Test cases for data exporter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config.default()
        self.exporter = DataExporter(self.config)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def create_sample_records(self):
        """Create sample TLV records for testing."""
        records = [
            TLVRecord(
                timestamp=datetime.now(),
                data_type='imu',
                data={
                    'accel_x': 1.0, 'accel_y': 2.0, 'accel_z': 3.0,
                    'gyro_x': 0.1, 'gyro_y': 0.2, 'gyro_z': 0.3
                },
                raw_tlv_type=0x01,
                raw_tlv_length=24
            ),
            TLVRecord(
                timestamp=datetime.now(),
                data_type='temperature',
                data={'temperature': 25.5, 'sensor_id': 1},
                raw_tlv_type=0x02,
                raw_tlv_length=8
            ),
            TLVRecord(
                timestamp=datetime.now(),
                data_type='health',
                data={
                    'battery_voltage': 3.7,
                    'cpu_temperature': 45.2,
                    'memory_usage': 1024,
                    'error_code': 0
                },
                raw_tlv_type=0x03,
                raw_tlv_length=16
            )
        ]
        return records
    
    def test_exporter_initialization(self):
        """Test exporter initializes correctly."""
        assert self.exporter is not None
        assert self.exporter.timestamp_format == '%Y-%m-%d %H:%M:%S.%f'
        assert self.exporter.csv_delimiter == ','
        assert self.exporter.json_indent == 2
    
    def test_export_csv_empty_records(self):
        """Test exporting empty records to CSV."""
        files = self.exporter.export_csv([], self.output_dir)
        assert len(files) == 0
    
    def test_export_json_empty_records(self):
        """Test exporting empty records to JSON."""
        files = self.exporter.export_json([], self.output_dir)
        assert len(files) == 0
    
    def test_export_csv_with_records(self):
        """Test exporting records to CSV."""
        records = self.create_sample_records()
        files = self.exporter.export_csv(records, self.output_dir)
        
        assert len(files) > 0
        
        # Verify CSV files were created
        for csv_file in files:
            assert csv_file.exists()
            assert csv_file.suffix == '.csv'
            
            # Verify CSV content
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) > 1  # Header + data rows
    
    def test_export_json_with_records(self):
        """Test exporting records to JSON."""
        records = self.create_sample_records()
        files = self.exporter.export_json(records, self.output_dir)
        
        assert len(files) > 0
        
        # Verify JSON files were created
        for json_file in files:
            assert json_file.exists()
            assert json_file.suffix == '.json'
            
            # Verify JSON content
            with open(json_file, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict)
    
    def test_group_records_by_type(self):
        """Test grouping records by data type."""
        records = self.create_sample_records()
        grouped = self.exporter._group_records_by_type(records)
        
        assert 'imu' in grouped
        assert 'temperature' in grouped
        assert 'health' in grouped
        assert len(grouped['imu']) == 1
        assert len(grouped['temperature']) == 1
        assert len(grouped['health']) == 1


if __name__ == "__main__":
    pytest.main([__file__])
