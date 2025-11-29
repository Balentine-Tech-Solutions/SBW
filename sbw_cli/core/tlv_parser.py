"""
TLV Parsing Module
SBWv1.i2 Mark I Prototype

Parses Type-Length-Value (TLV) formatted data from decompressed SBW blocks.
Implements TL-1.0 specification for IMU, Temperature, and Health data.
"""

import logging
import struct
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from sbw_cli.utils.config import Config


@dataclass
class TLVRecord:
    """Represents a parsed TLV record."""
    timestamp: datetime
    data_type: str
    data: Dict[str, Any]
    raw_tlv_type: int
    raw_tlv_length: int


@dataclass
class IMUData:
    """IMU sensor data structure."""
    accel_x: float
    accel_y: float  
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    

@dataclass
class TemperatureData:
    """Temperature sensor data structure."""
    temperature: float
    sensor_id: int


@dataclass
class HealthData:
    """System health data structure."""
    battery_voltage: float
    cpu_temperature: float
    memory_usage: int
    error_code: int


class TLVParser:
    """Parses TLV formatted data from SBW blocks."""
    
    # TLV Type IDs (placeholder values - will be defined in TL-1.0 spec)
    TLV_IMU = 0x01
    TLV_TEMPERATURE = 0x02 
    TLV_HEALTH = 0x03
    TLV_SESSION_METADATA = 0x04
    TLV_TIMESTAMP = 0x05
    
    def __init__(self, config: Config):
        """Initialize TLV parser with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load TLV specification settings
        self.tlv_version = config.get('tlv.version', '1.0')
        self.byte_order = config.get('tlv.byte_order', 'little')  # or 'big'
        self.alignment = config.get('tlv.alignment', 4)  # byte alignment
        
        self.logger.debug(f"TLV parser initialized for version {self.tlv_version}")
    
    def parse_block(self, data: bytes) -> List[TLVRecord]:
        """
        Parse all TLV records from a decompressed block.
        
        Args:
            data: Decompressed block data
            
        Returns:
            List of parsed TLV records
        """
        records = []
        offset = 0
        
        try:
            self.logger.debug(f"Parsing TLV data from {len(data)} bytes")
            
            while offset < len(data):
                # Parse TLV header
                tlv_type, tlv_length, header_size = self._parse_tlv_header(data, offset)
                
                if tlv_type is None or tlv_length is None:
                    # End of valid data or parse error
                    break
                    
                # Extract TLV payload
                payload_start = offset + header_size
                payload_end = payload_start + tlv_length
                
                if payload_end > len(data):
                    self.logger.warning(f"TLV payload extends beyond data boundary at offset {offset}")
                    break
                    
                payload = data[payload_start:payload_end]
                
                # Parse the TLV record based on type
                record = self._parse_tlv_record(tlv_type, tlv_length, payload)
                if record:
                    records.append(record)
                    
                # Move to next TLV record
                offset = payload_end
                
                # Handle alignment padding
                if self.alignment > 1:
                    alignment_padding = (self.alignment - (offset % self.alignment)) % self.alignment
                    offset += alignment_padding
                    
            self.logger.debug(f"Parsed {len(records)} TLV records")
            
        except Exception as e:
            self.logger.error(f"Error parsing TLV block: {e}")
            
        return records
    
    def _parse_tlv_header(self, data: bytes, offset: int) -> Tuple[Optional[int], Optional[int], int]:
        """Parse TLV header (Type and Length fields)."""
        try:
            # TODO: Implement actual TLV header format from TL-1.0 spec
            # For now, assume: 2 bytes type + 2 bytes length (little endian)
            
            if offset + 4 > len(data):
                return None, None, 0
                
            endian = '<' if self.byte_order == 'little' else '>'
            tlv_type, tlv_length = struct.unpack(f'{endian}HH', data[offset:offset+4])
            
            return tlv_type, tlv_length, 4
            
        except Exception as e:
            self.logger.error(f"Error parsing TLV header at offset {offset}: {e}")
            return None, None, 0
    
    def _parse_tlv_record(self, tlv_type: int, tlv_length: int, payload: bytes) -> Optional[TLVRecord]:
        """Parse a single TLV record based on its type."""
        try:
            timestamp = datetime.now()  # TODO: Extract from session metadata or TLV timestamp
            
            if tlv_type == self.TLV_IMU:
                data = self._parse_imu_data(payload)
                data_type = 'imu'
            elif tlv_type == self.TLV_TEMPERATURE:
                data = self._parse_temperature_data(payload)
                data_type = 'temperature'
            elif tlv_type == self.TLV_HEALTH:
                data = self._parse_health_data(payload)
                data_type = 'health'
            elif tlv_type == self.TLV_SESSION_METADATA:
                data = self._parse_session_metadata(payload)
                data_type = 'session_metadata'
            elif tlv_type == self.TLV_TIMESTAMP:
                data = self._parse_timestamp(payload)
                data_type = 'timestamp'
                if 'timestamp' in data:
                    timestamp = data['timestamp']
            else:
                self.logger.warning(f"Unknown TLV type: 0x{tlv_type:02X}")
                data = {'raw_payload': payload.hex()}
                data_type = 'unknown'
                
            return TLVRecord(
                timestamp=timestamp,
                data_type=data_type,
                data=data,
                raw_tlv_type=tlv_type,
                raw_tlv_length=tlv_length
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing TLV record type 0x{tlv_type:02X}: {e}")
            return None
    
    def _parse_imu_data(self, payload: bytes) -> Dict[str, Any]:
        """Parse IMU data payload (TL-1.0 spec)."""
        # IMU Format: 6 float32 values (accel_xyz + gyro_xyz)
        
        if len(payload) < 24:  # 6 * 4 bytes
            raise ValueError(f"IMU payload too short: {len(payload)} bytes (expected 24+)")
            
        try:
            endian = '<' if self.byte_order == 'little' else '>'
            values = struct.unpack(f'{endian}6f', payload[:24])
            
            return {
                'accel_x': float(values[0]),
                'accel_y': float(values[1]), 
                'accel_z': float(values[2]),
                'gyro_x': float(values[3]),
                'gyro_y': float(values[4]),
                'gyro_z': float(values[5])
            }
        except struct.error as e:
            raise ValueError(f"Failed to unpack IMU data: {e}")
    
    def _parse_temperature_data(self, payload: bytes) -> Dict[str, Any]:
        """Parse temperature data payload (TL-1.0 spec)."""
        # Temperature Format: float32 temperature + uint32 sensor_id
        
        if len(payload) < 8:
            raise ValueError(f"Temperature payload too short: {len(payload)} bytes (expected 8+)")
            
        try:
            endian = '<' if self.byte_order == 'little' else '>'
            temperature, sensor_id = struct.unpack(f'{endian}fI', payload[:8])
            
            return {
                'temperature': float(temperature),
                'sensor_id': int(sensor_id)
            }
        except struct.error as e:
            raise ValueError(f"Failed to unpack temperature data: {e}")
    
    def _parse_health_data(self, payload: bytes) -> Dict[str, Any]:
        """Parse health data payload (TL-1.0 spec)."""
        # Health Format: battery_voltage(f) + cpu_temp(f) + memory_usage(I) + error_code(I)
        
        if len(payload) < 16:
            raise ValueError(f"Health payload too short: {len(payload)} bytes (expected 16+)")
            
        try:
            endian = '<' if self.byte_order == 'little' else '>'
            battery_voltage, cpu_temperature, memory_usage, error_code = struct.unpack(
                f'{endian}ffII', payload[:16]
            )
            
            return {
                'battery_voltage': float(battery_voltage),
                'cpu_temperature': float(cpu_temperature),
                'memory_usage': int(memory_usage),
                'error_code': int(error_code)
            }
        except struct.error as e:
            raise ValueError(f"Failed to unpack health data: {e}")
    
    def _parse_session_metadata(self, payload: bytes) -> Dict[str, Any]:
        """Parse session metadata payload (TL-1.0 spec)."""
        # Session Metadata Format: session_id(16 bytes) + firmware_version(4 bytes) + reserved
        
        result = {}
        
        try:
            if len(payload) >= 16:
                result['session_id'] = payload[:16].hex().upper()
            else:
                result['session_id'] = None
                
            if len(payload) >= 20:
                import struct
                endian = '<' if self.byte_order == 'little' else '>'
                fw_version = struct.unpack(f'{endian}I', payload[16:20])[0]
                result['firmware_version'] = f"0x{fw_version:08X}"
            else:
                result['firmware_version'] = 'Unknown'
                
            return result
            
        except Exception as e:
            self.logger.warning(f"Error parsing session metadata: {e}")
            return {
                'session_id': None,
                'firmware_version': 'Unknown',
                'raw_metadata': payload.hex()
            }
    
    def _parse_timestamp(self, payload: bytes) -> Dict[str, Any]:
        """Parse timestamp payload (TL-1.0 spec)."""
        # Timestamp Format: uint64 Unix timestamp microseconds
        
        if len(payload) < 8:
            raise ValueError(f"Timestamp payload too short: {len(payload)} bytes (expected 8+)")
            
        try:
            endian = '<' if self.byte_order == 'little' else '>'
            timestamp_us = struct.unpack(f'{endian}Q', payload[:8])[0]
            
            ts_obj = datetime.fromtimestamp(timestamp_us / 1_000_000)
            
            return {
                'timestamp': ts_obj,
                'timestamp_us': int(timestamp_us),
                'timestamp_iso': ts_obj.isoformat()
            }
        except (struct.error, ValueError, OSError) as e:
            raise ValueError(f"Failed to parse timestamp: {e}")