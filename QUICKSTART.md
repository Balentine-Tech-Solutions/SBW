# SBW CLI Tool - Quick Reference

## Installation

```bash
# Development
git clone https://github.com/Balentine-Tech-Solutions/SBW.git
cd SBW
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .

# Production (when available)
pip install sbw-cli
```

## Basic Commands

### Decode Full Pipeline
```bash
sbw-cli decode input.sbw --out output_dir/
```

### Full Analysis with All Outputs
```bash
sbw-cli decode input.sbw --out results/ --csv --json --plots --verbose
```

### File Information
```bash
sbw-cli info input.sbw
sbw-cli info input.sbw --verbose  # Detailed output
```

### Validate File Integrity
```bash
sbw-cli validate input.sbw
```

### With Custom Configuration
```bash
sbw-cli decode input.sbw --out output/ --config my_config.json
```

## Output Files

### Data Exports
- `imu_data.csv` - Accelerometer and gyroscope data
- `temperature_data.csv` - Temperature readings
- `health_data.csv` - System health metrics
- `sbw_data_complete.json` - All data in JSON format

### Visualizations
- `imu_accelerometer.png` - Accel X/Y/Z vs time
- `imu_gyroscope.png` - Gyro X/Y/Z vs time
- `temperature.png` - Temperature vs time
- `health_metrics.png` - System health vs time
- `summary_dashboard.png` - Combined overview

## Configuration

### Create Default Config
```bash
cat > config.json << 'EOF'
{
  "crypto": {
    "algorithm": "AES-GCM",
    "tag_length": 16,
    "nonce_length": 12
  },
  "compression": {
    "algorithm": "lz4"
  },
  "export": {
    "timestamp_format": "%Y-%m-%d %H:%M:%S.%f",
    "csv_delimiter": ","
  }
}
EOF
```

### Use Custom Config
```bash
sbw-cli decode input.sbw --out output/ --config config.json
```

## Environment Variables

```bash
# Set max file size (bytes)
export SBW_MAX_FILE_SIZE=524288000  # 500MB

# Enable debug logging
export SBW_DEBUG=1
```

## Development

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_crypto.py -v

# With coverage
pytest tests/ --cov=sbw_cli --cov-report=html
```

### Code Quality
```bash
# Format code
black sbw_cli/

# Lint
flake8 sbw_cli/

# Type check
mypy sbw_cli/
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Data Format Reference

### IMU Data (TLV Type 0x01)
```
Field          Type      Units
accel_x        float32   m/s²
accel_y        float32   m/s²
accel_z        float32   m/s²
gyro_x         float32   rad/s
gyro_y         float32   rad/s
gyro_z         float32   rad/s
```

### Temperature Data (TLV Type 0x02)
```
Field          Type      Units
temperature    float32   °C
sensor_id      uint32    -
```

### Health Data (TLV Type 0x03)
```
Field              Type      Units
battery_voltage    float32   V
cpu_temperature    float32   °C
memory_usage       uint32    bytes
error_code         uint32    -
```

## Troubleshooting

### Command Not Found
```bash
# Add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Or use with Python
python -m sbw_cli.main decode input.sbw --out output/
```

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install -r requirements.txt
pip install -e .
```

### Cryptography Errors
```bash
# Reinstall cryptography
pip install --upgrade --force-reinstall cryptography

# On Ubuntu/Debian, install build dependencies:
sudo apt-get install libssl-dev libffi-dev python3-dev
```

### Large File Out of Memory
```bash
# Increase Python memory limit
export PYTHONUNBUFFERED=1

# Or process smaller files first
sbw-cli decode small_file.sbw --out output/
```

## Security Considerations

- ✅ AES-GCM encryption with 256-bit keys
- ✅ File integrity verification via SHA-256
- ✅ Path traversal protection
- ✅ File size limits enforced
- ✅ Audit logging available
- ✅ ITAR compliance framework

## Performance Tips

1. Use `--out` to specify output directory
2. Omit `--plots` for faster processing if plots not needed
3. Use `--csv` for smaller exports
4. Process large files in batch mode (future)
5. Use `--verbose` for debugging only

## Documentation

- **README.md** - Overview and usage
- **INSTALL.md** - Installation instructions
- **DEVELOPMENT.md** - Architecture and design
- **MVP_STATUS.md** - Project status
- **SCALING_SUMMARY.md** - Recent improvements

## Getting Help

```bash
# Show all commands
sbw-cli --help

# Show decode help
sbw-cli decode --help

# Show info help
sbw-cli info --help

# Show validate help
sbw-cli validate --help
```

## Version Info

```bash
# Check version
python -c "import sbw_cli; print(sbw_cli.__version__)"

# Current version: 1.0.0-alpha
# Released: November 2025
```

## Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and discuss ideas
- **Email**: Contact development team

---

**Last Updated**: November 2025
**Version**: 1.0.0-alpha
