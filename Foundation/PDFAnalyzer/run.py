#!/usr/bin/env python3
"""
Script to run main.py with environment variables from env.txt
"""
import os
import sys

# Load environment variables from env.txt
def load_env_file(env_file):
    """Load environment variables from file"""
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded: {key}")

if __name__ == "__main__":
    # Load environment variables
    load_env_file('env.txt')
    
    # Import and run main
    from main import main
    main()
