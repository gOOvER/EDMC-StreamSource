#!/usr/bin/env python3
"""
Test runner for EDMC-StreamSource plugin.

This script runs all available tests and provides a comprehensive summary.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test_module(module_name, test_description):
    """
    Run a test module and return results.
    
    Args:
        module_name: Name of the test module to import
        test_description: Human readable description
        
    Returns:
        tuple: (success, duration, details)
    """
    try:
        print(f"\n{'='*60}")
        print(f"Running {test_description}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Import and run the test module
        test_module = __import__(module_name)
        
        if hasattr(test_module, 'run_all_tests'):
            # Module has a unified test runner
            results = test_module.run_all_tests()
            success = all(result[1] for result in results)
            details = results
        elif hasattr(test_module, f'run_all_{module_name.split("_")[1]}_tests'):
            # Module has a specific test runner
            runner_func = getattr(test_module, f'run_all_{module_name.split("_")[1]}_tests')
            results = runner_func()
            success = all(result[1] for result in results)
            details = results
        else:
            # Module is a script, run it and check exit code
            import subprocess
            result = subprocess.run([sys.executable, f"{module_name}.py"], 
                                  cwd=Path(__file__).parent,
                                  capture_output=True, text=True)
            success = result.returncode == 0
            details = result.stdout if success else result.stderr
        
        duration = time.time() - start_time
        return success, duration, details
        
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        return False, duration, str(e)


def main():
    """Main test runner function."""
    print("🧪 EDMC-StreamSource Test Suite")
    print("=" * 60)
    
    # Define available tests
    test_modules = [
        ("test_functional", "Functional Tests"),
        ("test_performance", "Performance Tests")
    ]
    
    # Track overall results
    all_results = []
    total_start_time = time.time()
    
    # Run each test module
    for module_name, description in test_modules:
        success, duration, details = run_test_module(module_name, description)
        all_results.append((description, success, duration, details))
        
        # Print immediate result
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{description}: {status} (took {duration:.2f}s)")
    
    total_duration = time.time() - total_start_time
    
    # Print comprehensive summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed_count = 0
    failed_count = 0
    
    for description, success, duration, details in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{description:<25} {status} ({duration:.2f}s)")
        
        if success:
            passed_count += 1
        else:
            failed_count += 1
            # Print failure details for debugging
            print(f"   Failure details: {details}")
    
    print(f"\n{'='*60}")
    print(f"📈 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests Run:    {len(all_results)}")
    print(f"Passed:            {passed_count} ✅")
    print(f"Failed:            {failed_count} {'❌' if failed_count > 0 else '✅'}")
    print(f"Success Rate:      {(passed_count/len(all_results)*100):.1f}%")
    print(f"Total Duration:    {total_duration:.2f}s")
    
    # Additional system info
    print(f"\n{'='*60}")
    print(f"🔧 ENVIRONMENT INFO")
    print(f"{'='*60}")
    print(f"Python Version:    {sys.version.split()[0]}")
    print(f"Platform:          {sys.platform}")
    print(f"Test Directory:    {Path(__file__).parent}")
    print(f"Project Root:      {project_root}")
    
    # Check if plugin file exists
    plugin_file = project_root / "load.py"
    print(f"Plugin File:       {'✅ Found' if plugin_file.exists() else '❌ Missing'}")
    
    if all_results:
        overall_success = all(result[1] for result in all_results)
        
        if overall_success:
            print(f"\n🎉 ALL TESTS PASSED! The plugin is ready for production use.")
            sys.exit(0)
        else:
            print(f"\n⚠️ SOME TESTS FAILED. Please review and fix issues before release.")
            sys.exit(1)
    else:
        print(f"\n❌ NO TESTS WERE RUN. Please check test configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()