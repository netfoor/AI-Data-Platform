#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Data Platform
Runs different test categories and generates reports
"""
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        
        print(f"✅ SUCCESS: {description}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        
        return True, duration
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        
        print(f"❌ FAILED: {description}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"Exit code: {e.returncode}")
        
        if e.stdout:
            print("\nStdout:")
            print(e.stdout)
        
        if e.stderr:
            print("\nStderr:")
            print(e.stderr)
        
        return False, duration


def run_tests(test_type, verbose=False):
    """Run specific test categories"""
    base_cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        base_cmd.append("-v")
    
    test_results = {}
    
    if test_type in ["all", "unit"]:
        success, duration = run_command(
            base_cmd + ["tests/test_kpi_calculations.py", "-m", "unit"],
            "Unit Tests - KPI Calculations"
        )
        test_results["unit"] = {"success": success, "duration": duration}
    
    if test_type in ["all", "integration"]:
        success, duration = run_command(
            base_cmd + ["tests/test_database_integration.py", "-m", "integration"],
            "Integration Tests - Database Operations"
        )
        test_results["integration"] = {"success": success, "duration": duration}
    
    if test_type in ["all", "api"]:
        success, duration = run_command(
            base_cmd + ["tests/test_api_endpoints.py", "-m", "api"],
            "API Tests - Endpoint Functionality"
        )
        test_results["api"] = {"success": success, "duration": duration}
    
    if test_type in ["all", "e2e"]:
        success, duration = run_command(
            base_cmd + ["tests/test_e2e_pipeline.py", "-m", "e2e"],
            "End-to-End Tests - Complete Pipeline"
        )
        test_results["e2e"] = {"success": success, "duration": duration}
    
    return test_results


def generate_report(test_results):
    """Generate a test execution report"""
    print(f"\n{'='*60}")
    print("TEST EXECUTION REPORT")
    print(f"{'='*60}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result["success"])
    total_duration = sum(result["duration"] for result in test_results.values())
    
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    
    print(f"\nDetailed Results:")
    print(f"{'Category':<15} {'Status':<10} {'Duration':<10}")
    print(f"{'-'*15} {'-'*10} {'-'*10}")
    
    for category, result in test_results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s"
        print(f"{category:<15} {status:<10} {duration:<10}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Your AI Data Platform is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test category(ies) failed. Check the output above.")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="AI Data Platform Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "api", "e2e"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install testing dependencies first"
    )
    
    args = parser.parse_args()
    
    print("🧪 AI Data Platform - Comprehensive Testing Suite")
    print("=" * 60)
    
    # Install dependencies if requested
    if args.install_deps:
        print("\n📦 Installing testing dependencies...")
        deps = [
            "pytest",
            "pytest-cov",
            "httpx",
            "fastapi[testing]"
        ]
        
        for dep in deps:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    # Check if tests directory exists
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Tests directory not found. Please run this from the project root.")
        sys.exit(1)
    
    # Run tests
    print(f"\n🚀 Starting {args.test_type} tests...")
    test_results = run_tests(args.test_type, args.verbose)
    
    # Generate report
    all_passed = generate_report(test_results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
