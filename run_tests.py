#!/usr/bin/env python3
"""
Enhanced test runner script for Gradeinator Backend.
"""
import sys
import subprocess
import argparse


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"🧪 {description}")
    print("=" * 50)

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {description} passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_flake8():
    """Run Flake8 code quality checks."""
    cmd = ["python", "-m", "flake8", "app/", "tests/", "--max-line-length=88"]
    return run_command(cmd, "Flake8 Code Quality Checks")


def run_unit_tests():
    """Run only unit tests (fast)."""
    cmd = ["python", "-m", "pytest", "tests/unit/", "-v"]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run only integration tests."""
    cmd = ["python", "-m", "pytest", "tests/integration/", "-v"]
    return run_command(cmd, "Integration Tests")


def run_all_tests():
    """Run all tests with coverage."""
    cmd = [
        "python", "-m", "pytest", "tests/", "-v",
        "--cov=app", "--cov-report=term-missing"
    ]
    return run_command(cmd, "All Tests with Coverage")


def run_quality_checks():
    """Run all quality checks (flake8 + tests)."""
    print("🔍 Running Code Quality Checks...")
    print("=" * 60)

    # Run Flake8 first
    flake8_success = run_flake8()

    # Run tests
    tests_success = run_all_tests()

    overall_success = flake8_success and tests_success

    if overall_success:
        print("\n🎉 All quality checks passed!")
    else:
        print("\n💥 Some quality checks failed!")

    return overall_success


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Gradeinator Test Runner")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "all", "flake8", "quality"],
        default="all",
        nargs="?",
        help="Type of tests to run (default: all)"
    )

    args = parser.parse_args()

    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "flake8":
        success = run_flake8()
    elif args.test_type == "quality":
        success = run_quality_checks()
    else:
        success = run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
