# Installation Guide - SBW CLI Tool

## System Requirements

- **Operating Systems**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+, CentOS 7+, etc.)
- **Python**: 3.10, 3.11, or 3.12
- **RAM**: Minimum 2GB (4GB recommended for large files)
- **Disk Space**: 500MB for installation and dependencies

## Installation Methods

### Method 1: Development Installation (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Balentine-Tech-Solutions/SBW.git
cd SBW

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies (optional)
pip install -r requirements.txt
pip install pre-commit black flake8
pre-commit install
```

### Method 2: Package Installation

```bash
# Install from PyPI (when available)
pip install sbw-cli

# Or install from source distribution
pip install dist/sbw-cli-1.0.0.tar.gz
```

### Method 3: Docker Installation (Future)

```bash
# Build Docker image
docker build -t sbw-cli:latest .

# Run in container
docker run -v /path/to/data:/data sbw-cli:latest decode /data/input.sbw --out /data/output/
```

## Verification

After installation, verify everything is working:

```bash
# Check CLI is installed
sbw-cli --help

# Run tests to verify installation
pytest tests/ -v

# Check version
sbw-cli decode --help
```

## Platform-Specific Notes

### Windows

- Python from Microsoft Store or python.org
- Visual C++ redistributables may be required for some dependencies
- Use PowerShell or Command Prompt for CLI commands

```powershell
# PowerShell example
$env:PYTHONPATH="C:\path\to\SBW"
python -m sbw_cli.main decode input.sbw --out output\
```

### macOS

- Install Python via Homebrew or official installer
- May require `xcode-select --install` for build tools

```bash
# Homebrew installation
brew install python@3.11
python3.11 -m pip install -e .
```

### Linux

- Use system package manager or pyenv for Python version management
- May require `python3-dev` and `build-essential` packages

```bash
# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-venv python3-pip
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# CentOS/RHEL
sudo yum install python311 python311-devel gcc
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

### Initial Setup

Create a configuration file for your environment:

```bash
# Create config directory
mkdir ~/.sbw-cli
# or on Windows: mkdir %APPDATA%\sbw-cli

# Create config file
cat > ~/.sbw-cli/config.json << 'EOF'
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
  },
  "visualization": {
    "figure_size": [12, 8],
    "dpi": 300
  }
}
EOF
```

### Environment Variables

```bash
# Set maximum file size (default 100MB)
export SBW_MAX_FILE_SIZE=524288000  # 500MB

# Set config directory
export SBW_CONFIG_DIR=~/.sbw-cli

# Enable debug logging
export SBW_DEBUG=1

# On Windows:
set SBW_MAX_FILE_SIZE=524288000
set SBW_CONFIG_DIR=%APPDATA%\sbw-cli
set SBW_DEBUG=1
```

## Troubleshooting

### Issue: Command not found

```bash
# Solution: Ensure pip install location is in PATH
# Check pip install location:
pip show sbw-cli

# Add to PATH (Linux/macOS):
export PATH="$PATH:$HOME/.local/bin"

# Check if in PATH:
which sbw-cli
```

### Issue: ModuleNotFoundError

```bash
# Solution: Reinstall with all dependencies
pip install -r requirements.txt
pip install -e .

# Verify installation:
python -c "import sbw_cli; print(sbw_cli.__file__)"
```

### Issue: Cryptography library errors

```bash
# Solution: Reinstall cryptography
pip install --upgrade --force-reinstall cryptography

# Or install build dependencies first:
# Ubuntu/Debian:
sudo apt-get install libssl-dev libffi-dev python3-dev
# macOS:
brew install openssl
# Windows: Install Visual C++ Build Tools
```

### Issue: LZ4 decompression errors

```bash
# Solution: Verify LZ4 installation
pip install --upgrade lz4

# Test LZ4:
python -c "import lz4.frame; print('LZ4 OK')"
```

### Issue: Out of memory on large files

```bash
# Solution: Increase available memory or process smaller files
# Increase Python memory limit:
export PYTHONUNBUFFERED=1
# Process with streaming (future feature)
sbw-cli decode large_file.sbw --out output/ --streaming
```

## Uninstallation

### From Development

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Remove source code
cd ..
rm -rf SBW
```

### From Package

```bash
# Uninstall package
pip uninstall sbw-cli

# Remove configuration
rm -rf ~/.sbw-cli  # Linux/macOS
rmdir %APPDATA%\sbw-cli  # Windows
```

## Getting Help

- **Documentation**: See `README.md` and `DEVELOPMENT.md`
- **Issues**: Report on GitHub at https://github.com/Balentine-Tech-Solutions/SBW/issues
- **Discussion**: Use GitHub Discussions for questions

## Next Steps

After installation:

1. Read the [README.md](README.md) for usage examples
2. Run `sbw-cli --help` to see available commands
3. Check [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details
4. Review example configuration in `examples/config_example.json`

---

**Last Updated**: November 2025
**Version**: 1.0.0-alpha
