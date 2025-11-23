"""
Data Visualization Module
SBWv1.i2 Mark I Prototype

Generates graphs and visualizations for SBW data:
- Accelerometer (X/Y/Z) vs time
- Gyroscope (X/Y/Z) vs time  
- Temperature vs time
- Health events vs time
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure

from sbw_cli.core.tlv_parser import TLVRecord
from sbw_cli.utils.config import Config


class DataVisualizer:
    """Generates visualizations for parsed SBW data."""
    
    def __init__(self, config: Config):
        """Initialize data visualizer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Visualization settings
        self.figure_size = config.get('visualization.figure_size', (12, 8))
        self.dpi = config.get('visualization.dpi', 300)
        self.plot_style = config.get('visualization.style', 'seaborn-v0_8')
        
        # Set matplotlib style
        try:
            plt.style.use(self.plot_style)
        except:
            self.logger.warning(f"Plot style '{self.plot_style}' not available, using default")
            
        # Configure matplotlib for better plots
        plt.rcParams['figure.figsize'] = self.figure_size
        plt.rcParams['savefig.dpi'] = self.dpi
        plt.rcParams['font.size'] = 10
        
    def generate_plots(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """
        Generate all visualization plots for the dataset.
        
        Args:
            records: List of parsed TLV records
            output_dir: Directory for plot output files
            
        Returns:
            List of created plot file paths
        """
        created_files = []
        
        try:
            self.logger.info(f"Generating visualizations for {len(records)} records")
            
            # Group records by type for plotting
            grouped_data = self._group_records_by_type(records)
            
            # Generate IMU plots
            if 'imu' in grouped_data and grouped_data['imu']:
                imu_files = self._plot_imu_data(grouped_data['imu'], output_dir)
                created_files.extend(imu_files)
                
            # Generate temperature plots  
            if 'temperature' in grouped_data and grouped_data['temperature']:
                temp_files = self._plot_temperature_data(grouped_data['temperature'], output_dir)
                created_files.extend(temp_files)
                
            # Generate health plots
            if 'health' in grouped_data and grouped_data['health']:
                health_files = self._plot_health_data(grouped_data['health'], output_dir)
                created_files.extend(health_files)
                
            # Generate summary plot
            summary_file = self._plot_summary_dashboard(grouped_data, output_dir)
            if summary_file:
                created_files.append(summary_file)
                
            self.logger.info(f"Generated {len(created_files)} plot files")
            
        except Exception as e:
            self.logger.error(f"Error during plot generation: {e}")
            
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
    
    def _plot_imu_data(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """Generate IMU data plots (accelerometer and gyroscope)."""
        created_files = []
        
        if not records:
            return created_files
            
        # Extract timestamps and data
        timestamps = [record.timestamp for record in records]
        accel_x = [record.data.get('accel_x', 0.0) for record in records]
        accel_y = [record.data.get('accel_y', 0.0) for record in records]
        accel_z = [record.data.get('accel_z', 0.0) for record in records]
        gyro_x = [record.data.get('gyro_x', 0.0) for record in records]
        gyro_y = [record.data.get('gyro_y', 0.0) for record in records]
        gyro_z = [record.data.get('gyro_z', 0.0) for record in records]
        
        # Accelerometer plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=self.figure_size, sharex=True)
        fig.suptitle('IMU Accelerometer Data vs Time', fontsize=14, fontweight='bold')
        
        ax1.plot(timestamps, accel_x, 'r-', linewidth=1, label='Accel X')
        ax1.set_ylabel('Accel X (m/s²)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.plot(timestamps, accel_y, 'g-', linewidth=1, label='Accel Y')
        ax2.set_ylabel('Accel Y (m/s²)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        ax3.plot(timestamps, accel_z, 'b-', linewidth=1, label='Accel Z')
        ax3.set_ylabel('Accel Z (m/s²)')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        accel_file = output_dir / 'imu_accelerometer.png'
        plt.savefig(accel_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        created_files.append(accel_file)
        
        # Gyroscope plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=self.figure_size, sharex=True)
        fig.suptitle('IMU Gyroscope Data vs Time', fontsize=14, fontweight='bold')
        
        ax1.plot(timestamps, gyro_x, 'r-', linewidth=1, label='Gyro X')
        ax1.set_ylabel('Gyro X (rad/s)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.plot(timestamps, gyro_y, 'g-', linewidth=1, label='Gyro Y')
        ax2.set_ylabel('Gyro Y (rad/s)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        ax3.plot(timestamps, gyro_z, 'b-', linewidth=1, label='Gyro Z')
        ax3.set_ylabel('Gyro Z (rad/s)')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        gyro_file = output_dir / 'imu_gyroscope.png'
        plt.savefig(gyro_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        created_files.append(gyro_file)
        
        return created_files
    
    def _plot_temperature_data(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """Generate temperature data plots."""
        created_files = []
        
        if not records:
            return created_files
            
        # Extract timestamps and temperature data
        timestamps = [record.timestamp for record in records]
        temperatures = [record.data.get('temperature', 0.0) for record in records]
        
        # Temperature plot
        fig, ax = plt.subplots(figsize=self.figure_size)
        fig.suptitle('Temperature vs Time', fontsize=14, fontweight='bold')
        
        ax.plot(timestamps, temperatures, 'r-', linewidth=2, label='Temperature')
        ax.set_ylabel('Temperature (°C)')
        ax.set_xlabel('Time')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        temp_file = output_dir / 'temperature.png'
        plt.savefig(temp_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        created_files.append(temp_file)
        
        return created_files
    
    def _plot_health_data(self, records: List[TLVRecord], output_dir: Path) -> List[Path]:
        """Generate health data plots."""
        created_files = []
        
        if not records:
            return created_files
            
        # Extract timestamps and health data
        timestamps = [record.timestamp for record in records]
        battery_voltage = [record.data.get('battery_voltage', 0.0) for record in records]
        cpu_temperature = [record.data.get('cpu_temperature', 0.0) for record in records]
        memory_usage = [record.data.get('memory_usage', 0) for record in records]
        
        # Health metrics plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=self.figure_size, sharex=True)
        fig.suptitle('System Health Metrics vs Time', fontsize=14, fontweight='bold')
        
        ax1.plot(timestamps, battery_voltage, 'g-', linewidth=2, label='Battery Voltage')
        ax1.set_ylabel('Voltage (V)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.plot(timestamps, cpu_temperature, 'r-', linewidth=2, label='CPU Temperature')
        ax2.set_ylabel('Temperature (°C)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        ax3.plot(timestamps, memory_usage, 'b-', linewidth=2, label='Memory Usage')
        ax3.set_ylabel('Memory (%)')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Format x-axis
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        health_file = output_dir / 'health_metrics.png'
        plt.savefig(health_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        created_files.append(health_file)
        
        return created_files
    
    def _plot_summary_dashboard(self, grouped_data: Dict[str, List[TLVRecord]], output_dir: Path) -> Optional[Path]:
        """Generate a summary dashboard with key metrics."""
        try:
            fig = plt.figure(figsize=(16, 12))
            fig.suptitle('SBW Data Summary Dashboard', fontsize=16, fontweight='bold')
            
            # Create subplots for different data types
            subplot_count = 0
            
            # IMU summary (if available)
            if 'imu' in grouped_data and grouped_data['imu']:
                subplot_count += 2
                
            # Temperature summary (if available)
            if 'temperature' in grouped_data and grouped_data['temperature']:
                subplot_count += 1
                
            # Health summary (if available)
            if 'health' in grouped_data and grouped_data['health']:
                subplot_count += 1
                
            if subplot_count == 0:
                plt.close()
                return None
                
            current_subplot = 1
            
            # IMU plots
            if 'imu' in grouped_data and grouped_data['imu']:
                records = grouped_data['imu']
                timestamps = [r.timestamp for r in records]
                accel_x = [r.data.get('accel_x', 0.0) for r in records]
                accel_y = [r.data.get('accel_y', 0.0) for r in records]
                accel_z = [r.data.get('accel_z', 0.0) for r in records]
                
                ax = plt.subplot(subplot_count, 1, current_subplot)
                ax.plot(timestamps, accel_x, 'r-', label='Accel X', alpha=0.7)
                ax.plot(timestamps, accel_y, 'g-', label='Accel Y', alpha=0.7)
                ax.plot(timestamps, accel_z, 'b-', label='Accel Z', alpha=0.7)
                ax.set_ylabel('Acceleration (m/s²)')
                ax.set_title('IMU Accelerometer Summary')
                ax.grid(True, alpha=0.3)
                ax.legend()
                current_subplot += 1
                
                gyro_x = [r.data.get('gyro_x', 0.0) for r in records]
                gyro_y = [r.data.get('gyro_y', 0.0) for r in records]
                gyro_z = [r.data.get('gyro_z', 0.0) for r in records]
                
                ax = plt.subplot(subplot_count, 1, current_subplot)
                ax.plot(timestamps, gyro_x, 'r-', label='Gyro X', alpha=0.7)
                ax.plot(timestamps, gyro_y, 'g-', label='Gyro Y', alpha=0.7)
                ax.plot(timestamps, gyro_z, 'b-', label='Gyro Z', alpha=0.7)
                ax.set_ylabel('Angular Velocity (rad/s)')
                ax.set_title('IMU Gyroscope Summary')
                ax.grid(True, alpha=0.3)
                ax.legend()
                current_subplot += 1
                
            # Temperature plot
            if 'temperature' in grouped_data and grouped_data['temperature']:
                records = grouped_data['temperature']
                timestamps = [r.timestamp for r in records]
                temperatures = [r.data.get('temperature', 0.0) for r in records]
                
                ax = plt.subplot(subplot_count, 1, current_subplot)
                ax.plot(timestamps, temperatures, 'orange', linewidth=2, label='Temperature')
                ax.set_ylabel('Temperature (°C)')
                ax.set_title('Temperature Summary')
                ax.grid(True, alpha=0.3)
                ax.legend()
                current_subplot += 1
                
            # Health plot
            if 'health' in grouped_data and grouped_data['health']:
                records = grouped_data['health']
                timestamps = [r.timestamp for r in records]
                battery_voltage = [r.data.get('battery_voltage', 0.0) for r in records]
                
                ax = plt.subplot(subplot_count, 1, current_subplot)
                ax.plot(timestamps, battery_voltage, 'purple', linewidth=2, label='Battery Voltage')
                ax.set_ylabel('Voltage (V)')
                ax.set_title('Health Summary')
                ax.set_xlabel('Time')
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # Format x-axis for the last subplot
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            summary_file = output_dir / 'summary_dashboard.png'
            plt.savefig(summary_file, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            return summary_file
            
        except Exception as e:
            self.logger.error(f"Error generating summary dashboard: {e}")
            return None