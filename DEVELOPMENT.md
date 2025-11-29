# SBW CLI Tool - MVP Development Guide

## Project Status: Scaling to MVP

This document outlines the current state of the SBW CLI tool and the improvements made for MVP readiness.

### Current Implementation Status

#### ✅ Completed Modules

1. **Core Processing Pipeline**
   - Block header parsing (LG-1.0 specification)
   - AES-GCM decryption with proper error handling
   - LZ4/Heatshrink decompression support
   - TLV parsing for IMU, Temperature, Health, and Session metadata
   - Data export to CSV/JSON formats
   - Visualization with matplotlib

2. **Error Handling & Validation**
   - Graceful handling of corrupted blocks
   - Detailed error logging at each pipeline stage
   - Block index tracking for debugging
   - Fallback mechanisms for incomplete data

3. **Configuration Management**
   - JSON/YAML configuration file support
   - Environment-based defaults
   - Nested configuration with dot notation access

4. **CLI Entry Point**
   - Argument parsing with argparse
   - Input file validation
   - Output directory creation
   - Verbose logging support

#### 🔄 In Progress

1. **Comprehensive Test Suite**
   - Unit tests for all core modules
   - Integration tests for full pipeline
   - Edge case handling tests
   - Coverage analysis

2. **Enhanced CLI Commands**
   - `info` command for file inspection
   - `validate` command for integrity checks
   - `batch` command for multi-file processing
   - Progress indicators for long operations

#### 📋 Planned for MVP

1. **Documentation**
   - API documentation
   - Developer guide with examples
   - Troubleshooting guide
   - Security considerations

2. **CI/CD Integration**
   - GitHub Actions workflows
   - Automated testing and deployment
   - Code quality checks

3. **Performance Optimization**
   - Streaming for large files
   - Memory optimization
   - Caching strategies

4. **Security Hardening**
   - Secure key management
   - Input validation and sanitization
   - Audit logging

### Architecture Overview

```
┌─────────────────────────────────────────┐
│         SBW CLI Entry Point             │
│        (main.py - argparse)             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│       File Reading & Validation         │
│        (decoder.py _read_file)          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Block Parsing (LG-1.0 spec)       │
│     (decoder.py _parse_blocks)          │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐
  │Decrypt │ │Decrypt │ │Decrypt │
  │Block 1 │ │Block N │ │  ...   │
  │(AES)   │ │(AES)   │ │ (AES)  │
  └───┬────┘ └───┬────┘ └───┬────┘
      │          │          │
      ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐
  │Decomp. │ │Decomp. │ │Decomp. │
  │ (LZ4)  │ │ (LZ4)  │ │ (LZ4)  │
  └───┬────┘ └───┬────┘ └───┬────┘
      │          │          │
      ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐
  │ Parse  │ │ Parse  │ │ Parse  │
  │  TLV   │ │  TLV   │ │  TLV   │
  └───┬────┘ └───┬────┘ └───┬────┘
      │          │          │
      └──────────┼──────────┘
                 │
         ┌───────▼────────┐
         │  Merge Data    │
         └───────┬────────┘
                 │
         ┌───────┴────────────┬────────────┐
         │                    │            │
         ▼                    ▼            ▼
     ┌────────┐           ┌────────┐  ┌──────────┐
     │ Export │           │ Export │  │ Generate │
     │  CSV   │           │  JSON  │  │  Plots   │
     └────────┘           └────────┘  └──────────┘
```

### Data Flow & Specifications

#### Block Format (LG-1.0)
```
Header (12 bytes):
├─ Offset 0-3:   Raw Size (uint32 LE)
├─ Offset 4-7:   Compressed Size (uint32 LE)
├─ Offset 8:     Flags (uint8)
├─ Offset 9:     Nonce Size (uint8)
└─ Offset 10-11: Block ID (uint16 LE)

Payload:
├─ Nonce (variable length from header)
├─ Ciphertext (compressed data)
└─ Authentication Tag (16 bytes - AES-GCM)
```

#### Crypto Profile (EN-1.0)
```
Algorithm: AES-GCM
├─ Key Length: 256-bit (32 bytes)
├─ Nonce Length: 96-bit (12 bytes) [per GCM standard]
├─ Tag Length: 128-bit (16 bytes)
└─ Byte Order: Little-endian
```

#### TLV Types (TL-1.0)
```
0x01: IMU Data
      ├─ accel_x (float32)
      ├─ accel_y (float32)
      ├─ accel_z (float32)
      ├─ gyro_x (float32)
      ├─ gyro_y (float32)
      └─ gyro_z (float32)

0x02: Temperature Data
      ├─ temperature (float32)
      └─ sensor_id (uint32)

0x03: Health Data
      ├─ battery_voltage (float32)
      ├─ cpu_temperature (float32)
      ├─ memory_usage (uint32)
      └─ error_code (uint32)

0x04: Session Metadata
      ├─ session_id (16 bytes)
      ├─ firmware_version (uint32)
      └─ reserved

0x05: Timestamp
      └─ timestamp_us (uint64) - Unix epoch microseconds
```

### Error Handling Strategy

#### Recovery Levels

1. **Block Level**
   - Invalid blocks skipped with warning
   - Partial data extracted when possible
   - Logging of failure details for debugging

2. **Record Level**
   - Malformed TLV records skipped
   - Type mismatches handled gracefully
   - Detailed error messages per record

3. **Pipeline Level**
   - Continuation on individual block failures
   - Aggregation of all errors for reporting
   - Summary statistics with partial success indication

#### Error Categories

- **Decryption Errors**: Wrong key, corrupted data, tag mismatch
- **Decompression Errors**: Invalid LZ4 format, incomplete data
- **Parsing Errors**: Malformed TLV, unexpected type codes
- **I/O Errors**: File access, disk space, permission issues

### Testing Strategy

#### Test Coverage Targets
- Unit Tests: >85% code coverage
- Integration Tests: Full pipeline validation
- Edge Cases: Corrupted data, truncated blocks, extreme values

#### Test Categories
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Multi-module pipeline
- **Performance Tests**: Large file handling
- **Security Tests**: Key management, input validation

### Performance Considerations

#### Optimization Opportunities
- **Streaming**: Process blocks sequentially to minimize memory
- **Caching**: Avoid redundant decompression/parsing
- **Parallelization**: Process multiple blocks concurrently
- **Memory Pooling**: Reuse buffers for repeated operations

#### Benchmarks
- Target: <5 minutes for 100MB file
- Memory: <500MB for typical workflows
- I/O: Optimize read/write patterns

### Security Considerations

#### Key Management
- Keys loaded from secure configuration
- Never logged or exposed in debug output
- Cryptographic material cleared from memory
- Audit trail for key usage

#### Input Validation
- File size limits enforced
- Block format validation
- TLV type validation
- Overflow protection

#### Access Control
- File permission checks
- Output directory isolation
- Configuration file protection
- Audit logging

### Deployment Checklist

- [ ] All tests passing (>85% coverage)
- [ ] Documentation complete
- [ ] CI/CD pipelines configured
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Package creation tested
- [ ] Installation instructions verified
- [ ] User documentation published

### Next Steps

1. **Phase 1**: Expand test coverage and integration tests
2. **Phase 2**: Add enhanced CLI commands (info, validate, batch)
3. **Phase 3**: Implement performance optimizations
4. **Phase 4**: Security hardening and audit logging
5. **Phase 5**: Release as MVP v1.0

### References

- **LG-1.0**: Block header format specification
- **EN-1.0**: Encryption and crypto profile specification
- **TL-1.0**: TLV data format specification
- **SBW System**: Shoot-By-Wire telemetry system

### Contact

For questions or issues related to this MVP development, contact the development team.

---

**Last Updated**: November 2025
**Status**: MVP Scaling In Progress
**Version**: 1.0.0-alpha
