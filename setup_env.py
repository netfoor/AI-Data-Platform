#!/usr/bin/env python3
"""
Setup script for AI Data Platform development environment
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Set up the development environment"""
    print("Setting up AI Data Platform development environment...")
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Already in a virtual environment")
    else:
        print("Creating virtual environment...")
        run_command("python -m venv venv", "Creating virtual environment")
        
        # Provide activation instructions
        if os.name == 'nt':  # Windows
            print("\nTo activate the virtual environment, run:")
            print("venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("\nTo activate the virtual environment, run:")
            print("source venv/bin/activate")
        
        print("\nAfter activation, run this script again to install dependencies.")
        return
    
    # Install dependencies
    run_command("pip install --upgrade pip", "Upgrading pip")
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Created data directory: {data_dir}")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"✓ Created logs directory: {logs_dir}")
    
    print("\n✓ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Copy your ads_spend.csv file to the data/ directory")
    print("2. Run the application with: python -m ai_data_platform")

if __name__ == "__main__":
    main()