"""
Python script to find the closest atlas regions to given MNI peak coordinates
using the whereami command from AFNI. Configuration is read from config.yml.
"""

import subprocess
import csv
import yaml
import os
import sys

def load_config(config_path):
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        sys.exit(f"Configuration file '{config_path}' not found.")
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Determine the directory where this script resides
    script_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Change the working directory to the script's directory
    os.chdir(script_dir)
    
    # Define the path to config.yml
    config_path = os.path.join(script_dir, 'config.yml')
    
    # Load configuration
    config = load_config(config_path)
    
    input_coordinates_file = config['input_coordinates_file']
    atlases = config['atlases']
    afni_parent_directory = config['afni_parent_directory']

    # Check if AFNI directory exists
    if not os.path.exists(afni_parent_directory):
        sys.exit(f"AFNI parent directory '{afni_parent_directory}' does not exist.")
    
    # Add AFNI directory to PATH
    os.environ['PATH'] = afni_parent_directory + os.pathsep + os.environ.get('PATH', '')
    
    # Read the MNI peak coordinates from the TSV file
    coordinates = []
    input_file_path = os.path.join(script_dir, input_coordinates_file)
    if not os.path.exists(input_file_path):
        sys.exit(f"Input coordinates file '{input_coordinates_file}' not found.")
    
    with open(input_file_path, mode='r', newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            contrast = row['Contrast']
            x = row['Peak coordinate X']
            y = row['Peak coordinate Y']
            z = row['Peak coordinate Z']
            coordinates.append((contrast, x, y, z))
    
    # Prepare an output file to store results in the script's directory
    output_file = os.path.join(script_dir, 'whereami_results.tsv')
    with open(output_file, mode='w', newline='') as outfile:
        fieldnames = ['Contrast', 'Peak_X', 'Peak_Y', 'Peak_Z', 'Atlas', 'Whereami_Output']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
    
        # For each coordinate, query each atlas
        for idx, (contrast, x, y, z) in enumerate(coordinates):
            print(f"\n=== Results for Contrast: {contrast}, Coordinate {idx+1} ({x}, {y}, {z}) ===\n")
            for atlas in atlases:
                print(f"--- Atlas: {atlas} ---")
                command = [
                    'whereami',
                    x, y, z,
                    '-atlas', atlas,
                    '-space', 'MNI',  # Assuming coordinates are in MNI space
                    '-lpi',           # Assuming coordinates are in LPI orientation
                    '-tab'            # Tab-delimited output
                ]
                try:
                    # Run the whereami command with error handling for decoding
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        check=True,
                        encoding='utf-8',
                        errors='replace'  # Replace undecodable bytes
                    )
                    output = result.stdout.strip()
                    print(output)
                    
                    # Write the result to the output TSV file
                    writer.writerow({
                        'Contrast': contrast,
                        'Peak_X': x,
                        'Peak_Y': y,
                        'Peak_Z': z,
                        'Atlas': atlas,
                        'Whereami_Output': output
                    })
                except subprocess.CalledProcessError as e:
                    error_message = e.stderr.strip()
                    print(f"Error running whereami for atlas '{atlas}' at coordinate ({x}, {y}, {z}):")
                    print(error_message)
                    
                    # Write the error to the output TSV file
                    writer.writerow({
                        'Contrast': contrast,
                        'Peak_X': x,
                        'Peak_Y': y,
                        'Peak_Z': z,
                        'Atlas': atlas,
                        'Whereami_Output': f"Error: {error_message}"
                    })

    print(f"\nAll results have been saved to '{output_file}'.")

if __name__ == "__main__":
    main()