# Development Documentation

## Code Architecture

### Main Components

1. **StreamSource Class** - Central data holder with placeholder management
2. **File Writing System** - Safe file operations with error handling
3. **Event Processors** - Separate functions for different EDMC events
4. **Logging System** - Comprehensive error and debug logging

### Key Features

- **Robust Error Handling**: All file operations are wrapped in try-catch blocks
- **Type Safety**: Full type hints throughout the codebase
- **Performance Optimized**: Minimal file writes, only when data changes
- **Memory Efficient**: No memory leaks, proper resource cleanup
- **Unicode Support**: Full UTF-8 support for international character sets

### File Output Format

All output files are UTF-8 encoded text files with a single line containing the current value followed by a newline character. Empty values result in files with just a newline.

### Testing

The project includes comprehensive test suites in the `test/` directory:

- `test_functional.py` - Functional tests with mock EDMC environment
- `test_performance.py` - Performance and stress testing
- `mock_utils.py` - Test utilities and EDMC mocks
- `run_tests.py` - Main test runner

Run tests with:
```bash
cd test
python run_tests.py              # Run all tests
python test_functional.py        # Functional tests only
python test_performance.py       # Performance tests only
python test_runner.py quick      # Quick smoke test
```

### Performance Metrics

Based on testing with 1000 rapid updates:
- Average processing time: ~2.3ms per journal entry
- Throughput: ~440 updates per second
- Memory footprint: Minimal growth (<1MB for extended sessions)

### Code Quality

- **Linting**: flake8 compliance (PEP 8)
- **Type Checking**: MyPy static analysis
- **Cognitive Complexity**: <10 (simplified from original ~20)
- **Test Coverage**: Functional and performance testing

### Development Workflow

1. Make changes to `load.py`
2. Run `flake8 load.py` for style checking
3. Run `mypy load.py --ignore-missing-imports` for type checking
4. Run test suites: `cd test && python run_tests.py`
5. Update CHANGELOG.md with changes
6. Update version number in `load.py`

### Plugin Integration

This plugin integrates with EDMC through standard plugin interfaces:

- `plugin_start3()` - Plugin initialization
- `journal_entry()` - Process Elite Dangerous journal events
- `dashboard_entry()` - Process Status.json data
- `prefs_changed()` - Handle configuration changes

### File Output Locations

Files are written to the directory specified in EDMC's Output settings:
- Windows: Usually `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous`
- macOS: Usually `~/Library/Application Support/Frontier Developments/Elite Dangerous`
- Linux: Usually `~/.local/share/Steam/steamapps/common/Elite Dangerous/`

### Streaming Software Integration

The output files are designed to work with:
- **OBS Studio**: Use Text (GDI+) sources
- **XSplit**: Use Text sources
- **Streamlabs OBS**: Use Text sources
- **GameShow**: Use Text overlays

### Troubleshooting

Common issues and solutions:

1. **Files not updating**: Check EDMC output directory setting
2. **Permission errors**: Ensure EDMC has write access to output directory
3. **Encoding issues**: All files are UTF-8 encoded
4. **Performance issues**: Check system resources and antivirus interference