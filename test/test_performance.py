#!/usr/bin/env python3
"""
Performance tests for EDMC-StreamSource plugin.

This module tests the plugin's performance under various scenarios including:
- Rapid update processing
- Memory usage monitoring  
- Stress testing with edge cases
- Throughput measurements
"""

import time
import tempfile
import sys
from pathlib import Path

# Import test utilities
from mock_utils import setup_mock_environment, add_project_to_path, create_test_journal_entry, create_test_state

# Setup environment
add_project_to_path()
config, edmc_data, l10n = setup_mock_environment()

# Import plugin after mocking
import load


def test_rapid_updates():
    """Test performance with many rapid updates."""
    print("Performance Test - Rapid Updates")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config.outdir = temp_dir
        load.stream_source.outdir = temp_dir
        load.stream_source._ensure_output_directory()
        
        # Initialize plugin
        load.plugin_start3("/fake/plugin/dir")
        
        # Test rapid journal entries
        start_time = time.time()
        num_updates = 1000
        
        print(f"Processing {num_updates} journal entries...")
        
        for i in range(num_updates):
            test_entry = create_test_journal_entry(
                'Location',
                StarSystem=f'System_{i}',
                StarPos=[float(i), float(i+1), float(i+2)],
                Body=f'Body_{i}' if i % 2 == 0 else None
            )
            test_state = create_test_state(
                ShipType='sidewinder',
                ShipName=f'Ship_{i}'
            )
            
            load.journal_entry(
                cmdr="Test Commander",
                is_beta=False,
                system=f'System_{i}',
                station=f'Station_{i}' if i % 3 == 0 else '',
                entry=test_entry,
                state=test_state
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Completed {num_updates} updates in {duration:.3f} seconds")
        print(f"Average time per update: {(duration/num_updates)*1000:.3f} ms")
        print(f"Updates per second: {num_updates/duration:.1f}")
        
        # Verify final state
        system_file = Path(temp_dir) / "EDMC System.txt"
        final_content = system_file.read_text(encoding='utf-8').strip()
        expected = f'System_{num_updates-1}'
        print(f"Final system: {final_content} (expected: {expected})")
        
        # Performance target: Should complete within 5 seconds
        success = duration < 5.0
        status = "PASS" if success else "FAIL"
        print(f"Performance target (<5s): {status}")
        
        return success


def test_stress_scenarios():
    """Test with extreme coordinate values and edge cases."""
    print("\nStress Test - Edge Cases")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config.outdir = temp_dir
        load.stream_source.outdir = temp_dir
        load.stream_source._ensure_output_directory()
        
        # Test extreme values
        test_cases = [
            {
                'name': 'Extreme coordinates',
                'entry': create_test_journal_entry(
                    'Location',
                    StarSystem='Test System',
                    StarPos=[999999999.123456789, -999999999.987654321, 0.0]
                ),
                'dashboard': {
                    'Latitude': 90.0,
                    'Longitude': 180.0
                }
            },
            {
                'name': 'Zero coordinates',
                'entry': create_test_journal_entry(
                    'Location',
                    StarSystem='Origin',
                    StarPos=[0.0, 0.0, 0.0]
                ),
                'dashboard': {
                    'Latitude': 0.0,
                    'Longitude': 0.0
                }
            },
            {
                'name': 'Very long names',
                'entry': create_test_journal_entry(
                    'Location',
                    StarSystem='A' * 100 + ' System',
                    StarPos=[1.0, 2.0, 3.0],
                    Body='B' * 50 + ' Body'
                ),
                'dashboard': {}
            },
            {
                'name': 'Special characters',
                'entry': create_test_journal_entry(
                    'Location',
                    StarSystem='Αλφα Κεντauri',  # Greek letters
                    StarPos=[1.0, 2.0, 3.0],
                    Body='Planet ñ'
                ),
                'dashboard': {}
            },
            {
                'name': 'Negative coordinates',
                'entry': create_test_journal_entry(
                    'Location',
                    StarSystem='Negative Space',
                    StarPos=[-123.456, -789.012, -345.678]
                ),
                'dashboard': {
                    'Latitude': -45.0,
                    'Longitude': -90.0
                }
            }
        ]
        
        state = create_test_state(ShipType='sidewinder', ShipName='Test Ship')
        
        for test_case in test_cases:
            print(f"Testing: {test_case['name']}")
            
            try:
                load.journal_entry(
                    cmdr="Test Commander",
                    is_beta=False,
                    system=test_case['entry'].get('StarSystem', ''),
                    station='',
                    entry=test_case['entry'],
                    state=state
                )
                
                if test_case['dashboard']:
                    load.dashboard_entry(
                        cmdr="Test Commander",
                        is_beta=False,
                        entry=test_case['dashboard']
                    )
                
                print(f"  PASSED")
                
            except Exception as e:
                print(f"  FAILED: {e}")
                return False
        
        return True


def test_memory_usage():
    """Test memory usage with repeated operations."""
    print("\nMemory Test - Repeated Operations")
    print("=" * 40)
    
    # Try to import psutil for memory monitoring
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config.outdir = temp_dir
            load.stream_source.outdir = temp_dir
            load.stream_source._ensure_output_directory()
            
            # Run many cycles
            print("Running 100 simulation cycles...")
            for cycle in range(100):
                # Simulate a typical gaming session with various events
                events = [
                    create_test_journal_entry('FSDJump', StarSystem=f'System_{cycle}', StarPos=[cycle, cycle+1, cycle+2]),
                    create_test_journal_entry('SupercruiseExit', Body=f'Planet_{cycle}'),
                    create_test_journal_entry('Docked', StationName=f'Station_{cycle}'),
                    create_test_journal_entry('Undocked'),
                    create_test_journal_entry('SupercruiseEntry'),
                ]
                
                for event in events:
                    load.journal_entry(
                        cmdr="Test Commander",
                        is_beta=False,
                        system=event.get('StarSystem', f'System_{cycle}'),
                        station=event.get('StationName', ''),
                        entry=event,
                        state=create_test_state(ShipType='sidewinder', ShipName='Test Ship')
                    )
                
                # Dashboard updates
                load.dashboard_entry(
                    cmdr="Test Commander",
                    is_beta=False,
                    entry={'Latitude': cycle % 90, 'Longitude': cycle % 180}
                )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Initial memory: {initial_memory:.1f} MB")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory growth: {memory_growth:.1f} MB")
        
        # Should not grow significantly (< 10MB for this test)
        success = memory_growth < 10.0
        status = "PASS" if success else "FAIL"
        print(f"Memory target (<10MB growth): {status}")
        
        return success
        
    except ImportError:
        print("psutil not available, using simplified memory test...")
        
        # Simple test without psutil
        with tempfile.TemporaryDirectory() as temp_dir:
            config.outdir = temp_dir
            load.stream_source.outdir = temp_dir
            load.stream_source._ensure_output_directory()
            
            # Run a smaller number of operations
            for i in range(50):
                test_entry = create_test_journal_entry('Location', StarSystem=f'System_{i}')
                test_state = create_test_state()
                
                load.journal_entry(
                    cmdr="Test Commander",
                    is_beta=False,
                    system=f'System_{i}',
                    station='',
                    entry=test_entry,
                    state=test_state
                )
        
        print("Basic memory test completed (psutil not available)")
        return True


def test_file_io_performance():
    """Test file I/O performance under load."""
    print("\nFile I/O Performance Test")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config.outdir = temp_dir
        load.stream_source.outdir = temp_dir
        load.stream_source._ensure_output_directory()
        
        # Test many file writes
        num_writes = 500
        start_time = time.time()
        
        print(f"Performing {num_writes} file write operations...")
        
        for i in range(num_writes):
            # Alternate between different file types
            if i % 3 == 0:
                load.write_file("EDMC System.txt", f"System_{i}")
            elif i % 3 == 1:
                load.write_file("EDMC Station.txt", f"Station_{i}")
            else:
                load.write_file("EDMC ShipName.txt", f"Ship_{i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Completed {num_writes} writes in {duration:.3f} seconds")
        print(f"Average time per write: {(duration/num_writes)*1000:.3f} ms")
        print(f"Writes per second: {num_writes/duration:.1f}")
        
        # Should be very fast (< 1 second for 500 writes)
        success = duration < 1.0
        status = "PASS" if success else "FAIL"
        print(f"I/O performance target (<1s): {status}")
        
        return success


def run_all_performance_tests():
    """Run all performance tests."""
    tests = [
        ("Rapid Updates", test_rapid_updates),
        ("Stress Scenarios", test_stress_scenarios),
        ("Memory Usage", test_memory_usage),
        ("File I/O Performance", test_file_io_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nPerformance test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    return results


if __name__ == "__main__":
    print("EDMC-StreamSource Performance Tests")
    print("=" * 60)
    
    results = run_all_performance_tests()
    
    print(f"\n{'='*60}")
    print("Performance Test Results:")
    print(f"{'='*60}")
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\nAll performance tests passed! Plugin performance is excellent.")
        sys.exit(0)
    else:
        print(f"\nSome performance tests failed. Please review the plugin code.")
        sys.exit(1)