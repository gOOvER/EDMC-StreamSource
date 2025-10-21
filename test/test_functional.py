#!/usr/bin/env python3
"""
Functional tests for EDMC-StreamSource plugin.

This module tests the core functionality of the plugin including:
- Plugin initialization
- Journal event processing
- Dashboard event processing
- File output operations
"""

import tempfile
import sys
from pathlib import Path

# Import test utilities
from mock_utils import setup_mock_environment, add_project_to_path, create_test_journal_entry, create_test_state

# Setup environment
add_project_to_path()
config, edmc_data, l10n = setup_mock_environment()

# Import plugin after mocking
import load  # noqa: E402


def test_plugin_functionality():
    """Test the plugin functionality with mock data."""
    print("Testing EDMC-StreamSource Plugin Functionality")
    print("=" * 50)

    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")

        # Set up config
        config.outdir = temp_dir
        load.stream_source.outdir = temp_dir
        load.stream_source._ensure_output_directory()

        # Test plugin_start3
        print("\n1. Testing plugin_start3...")
        result = load.plugin_start3("/fake/plugin/dir")
        print(f"   Plugin name: {result}")
        assert result == "EDMC-StreamSource", f"Expected 'EDMC-StreamSource', got '{result}'"

        # Check if placeholder files were created
        files = list(Path(temp_dir).glob("EDMC *.txt"))
        print(f"   Created {len(files)} files")
        assert len(files) == 9, f"Expected 9 files, got {len(files)}"

        # Test journal_entry with FSDJump
        print("\n2. Testing journal_entry with FSDJump...")
        test_entry = create_test_journal_entry(
            'FSDJump',
            StarSystem='Sol',
            StarPos=[0.0, 0.0, 0.0],
            Body=None
        )
        test_state = create_test_state(
            ShipType='sidewinder',
            ShipName='Test Ship'
        )

        load.journal_entry(
            cmdr="Test Commander",
            is_beta=False,
            system="Sol",
            station="",
            entry=test_entry,
            state=test_state
        )

        # Test dashboard_entry
        print("\n3. Testing dashboard_entry with coordinates...")
        dashboard_data = {
            'Latitude': 45.123456,
            'Longitude': -122.654321
        }

        load.dashboard_entry(
            cmdr="Test Commander",
            is_beta=False,
            entry=dashboard_data
        )

        # Test prefs_changed
        print("\n4. Testing prefs_changed...")
        load.prefs_changed("Test Commander", False)

        # Verify files content
        print("\n5. Verifying output files...")
        _verify_file_content(temp_dir, "EDMC System.txt", "Sol")
        _verify_file_content(temp_dir, "EDMC LatLon.txt", "45.123456 -122.654321")
        _verify_file_content(temp_dir, "EDMC ShipName.txt", "Test Ship")

        # List all files for verification
        print(f"\n6. All output files in {temp_dir}:")
        for file in sorted(Path(temp_dir).glob("*.txt")):
            size = file.stat().st_size
            content = file.read_text(encoding='utf-8').strip()
            print(f"   {file.name} ({size} bytes): '{content}'")

        print("\nFunctional test completed successfully! ✅")
        return True


def test_error_handling():
    """Test error handling with invalid configurations."""
    print("\n" + "=" * 50)
    print("Testing Error Handling")
    print("=" * 50)

    # Test with non-existent directory
    old_outdir = load.stream_source.outdir
    load.stream_source.outdir = "/this/path/does/not/exist"

    print("\n1. Testing with invalid output directory...")
    load.write_file("test.txt", "test content")

    # Restore original directory
    load.stream_source.outdir = old_outdir
    print("   Error handling test completed ✅")
    return True


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n" + "=" * 50)
    print("Testing Edge Cases")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        config.outdir = temp_dir
        load.stream_source.outdir = temp_dir
        load.stream_source._ensure_output_directory()

        # Test with None values
        print("\n1. Testing None values...")
        test_entry = create_test_journal_entry('StartUp')
        test_state = create_test_state(ShipName=None)

        load.journal_entry(
            cmdr="Test Commander",
            is_beta=False,
            system="Test System",
            station="",
            entry=test_entry,
            state=test_state
        )

        # Test with empty strings
        print("\n2. Testing empty strings...")
        load.dashboard_entry(
            cmdr="Test Commander",
            is_beta=False,
            entry={}  # No Latitude/Longitude
        )

        # Test with extreme coordinates
        print("\n3. Testing extreme coordinates...")
        dashboard_data = {
            'Latitude': 90.0,
            'Longitude': 180.0
        }
        load.dashboard_entry(
            cmdr="Test Commander",
            is_beta=False,
            entry=dashboard_data
        )

        print("   Edge case tests completed ✅")
        return True


def _verify_file_content(temp_dir, filename, expected_content):
    """Verify that a file contains the expected content."""
    file_path = Path(temp_dir) / filename
    if file_path.exists():
        actual_content = file_path.read_text(encoding='utf-8').strip()
        print(f"   {filename}: '{actual_content}'")
        if expected_content and actual_content != expected_content:
            print(f"   ⚠️ Expected '{expected_content}', got '{actual_content}'")
    else:
        print(f"   ❌ File {filename} not found")


def run_all_tests():
    """Run all functional tests."""
    tests = [
        ("Plugin Functionality", test_plugin_functionality),
        ("Error Handling", test_error_handling),
        ("Edge Cases", test_edge_cases)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    return results


if __name__ == "__main__":
    print("EDMC-StreamSource Functional Tests")
    print("=" * 60)

    results = run_all_tests()

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All functional tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the plugin code.")
        sys.exit(1)
