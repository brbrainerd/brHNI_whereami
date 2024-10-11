"""
Main script to orchestrate the configuration generation and whereami analysis.
It checks for the existence of 'config.yml', generates it if missing,
and then proceeds to run the analysis.
"""

import os
import sys
import subprocess

def main():
    # Determine the directory where this script resides
    script_dir = os.path.abspath(os.path.dirname(__file__))

    # Define the path to config.yml
    config_path = os.path.join(script_dir, 'config.yml')

    # Path to generate_config.py and whereami_analysis.py
    generate_config_path = os.path.join(script_dir, 'generate_config.py')
    whereami_analysis_path = os.path.join(script_dir, 'brhni_whereami', 'whereami_analysis.py')

    # Check if 'config.yml' exists
    if not os.path.exists(config_path):
        print("Configuration file 'config.yml' not found. Generating configuration...")
        try:
            subprocess.run(
                ['poetry', 'run', 'generate-config'],
                check=True
            )
            print("Configuration generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate configuration: {e}")
            sys.exit(1)
    else:
        print("Configuration file 'config.yml' found. Skipping generation.")

    # Proceed to run 'whereami_analysis.py'
    print("Running whereami analysis...")
    try:
        subprocess.run(
            ['poetry', 'run', 'whereami-analysis'],
            check=True
        )
        print("Whereami analysis completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Whereami analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
        main()