"""
Tests for TLV Parsing Module
SBWv1.i2 Mark I Prototype
"""

import pytest
from pathlib import Path
import struct
from datetime import datetime

from sbw_cli.core.tlv_parser import TLVParser, TLVRecord
from sbw_cli.utils.config import Config


class TestTLVParser:
    """Test cases for TLV parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config.default()
        self.parser = TLVParser(self.config)
    
    def test_tlv_parser_initialization(self):
        """Test TLV parser initializes correctly."""
        assert self.parser is not None
        assert self.parser.tlv_version == '1.0'
        assert self.parser.byte_order == 'little'
        assert self.parser.alignment == 4
    
    def test_parse_block_empty(self):
        """Test parsing empty block."""
        records = self.parser.parse_block(b'')
        assert len(records) == 0
    
    def test_parse_block_incomplete_header(self):
        """Test parsing block with incomplete header."""
        # Less than 4 bytes (TLV type + length)
        records = self.parser.parse_block(b'\x00\x00')
        assert len(records) == 0
    
    def test_parse_imu_data(self):
        """Test parsing IMU data payload."""
        # Create valid IMU payload: 6 floats (accel_xyz + gyro_xyz)
        accel_x, accel_y, accel_z = 1.0, 2.0, 3.0
        gyro_x, gyro_y, gyro_z = 0.1, 0.2, 0.3
        
        payload = struct.pack('<6f', accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        
        data = self.parser._parse_imu_data(payload)
        
        assert abs(data['accel_x'] - accel_x) < 0.001
        assert abs(data['accel_y'] - accel_y) < 0.001
        assert abs(data['accel_z'] - accel_z) < 0.001
        assert abs(data['gyro_x'] - gyro_x) < 0.001
        assert abs(data['gyro_y'] - gyro_y) < 0.001
        assert abs(data['gyro_z'] - gyro_z) < 0.001
    
    def test_parse_imu_data_short_payload(self):
        """Test parsing IMU data with short payload."""
        with pytest.raises(ValueError):
            self.parser._parse_imu_data(b'\x00' * 20)
    
    def test_parse_temperature_data(self):
        """Test parsing temperature data payload."""
        temperature = 25.5
        sensor_id = 42
        
        payload = struct.pack('<fI', temperature, sensor_id)
        
        data = self.parser._parse_temperature_data(payload)
        
        assert abs(data['temperature'] - temperature) < 0.001
        assert data['sensor_id'] == sensor_id
    
    def test_parse_temperature_data_short_payload(self):
        """Test parsing temperature data with short payload."""
        with pytest.raises(ValueError):
            self.parser._parse_temperature_data(b'\x00' * 4)
    
    def test_parse_health_data(self):
        """Test parsing health data payload."""
        battery_voltage = 3.7
        cpu_temperature = 45.2
        memory_usage = 1024
        error_code = 0
        
        payload = struct.pack('<ffII', battery_voltage, cpu_temperature, memory_usage, error_code)
        
        data = self.parser._parse_health_data(payload)
        
        assert abs(data['battery_voltage'] - battery_voltage) < 0.001
        assert abs(data['cpu_temperature'] - cpu_temperature) < 0.001
        assert data['memory_usage'] == memory_usage
        assert data['error_code'] == error_code
    
    def test_parse_health_data_short_payload(self):
        """Test parsing health data with short payload."""
        with pytest.raises(ValueError):
            self.parser._parse_health_data(b'\x00' * 14)
    
    def test_parse_timestamp(self):
        """Test parsing timestamp payload."""
        # Current time in microseconds
        timestamp_us = int(datetime.now().timestamp() * 1_000_000)
        
        payload = struct.pack('<Q', timestamp_us)
        
        data = self.parser._parse_timestamp(payload)
        
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], datetime)
        assert data['timestamp_us'] == timestamp_us
        assert 'timestamp_iso' in data
    
    def test_parse_timestamp_short_payload(self):
        """Test parsing timestamp with short payload."""
        with pytest.raises(ValueError):
            self.parser._parse_timestamp(b'\x00' * 4)
    
    def test_parse_session_metadata(self):
        """Test parsing session metadata."""
        session_id = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10'
        fw_version = 0x01020304
        
        payload = session_id + struct.pack('<I', fw_version)
        
        data = self.parser._parse_session_metadata(payload)
        
        assert data['session_id'] == session_id.hex().upper()
        assert '01020304' in data['firmware_version']
    
    def test_tlv_record_creation(self):
        """Test TLV record creation."""
        timestamp = datetime.now()
        data_type = 'imu'
        data = {'accel_x': 1.0}
        
        record = TLVRecord(
            timestamp=timestamp,
            data_type=data_type,
            data=data,
            raw_tlv_type=0x01,
            raw_tlv_length=24
        )
        
        assert record.timestamp == timestamp
        assert record.data_type == data_type
        assert record.data == data
        assert record.raw_tlv_type == 0x01
        assert record.raw_tlv_length == 24


if __name__ == "__main__":
    pytest.main([__file__])
