"""
Python script to find the closest atlas regions to given MNI peak coordinates
using the whereami command from AFNI. Configuration is read from config.yml.
This script extracts specific fields from whereami's output and stores them
in separate columns within a TSV file.
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

def parse_whereami_output(output):
    """
    Parse the output from the whereami command to extract relevant fields.
    
    Args:
        output (str): The raw output string from whereami.
        
    Returns:
        list of dict: A list where each dict contains extracted fields.
    """
    parsed_results = []
    lines = output.split('\n')
    parse_section = False  # Flag to indicate if we're in the relevant section

    for line in lines:
        # Identify the start of the relevant section
        if line.startswith("Atlas") and "Within" in line and "Label" in line:
            parse_section = True
            continue  # Skip the header line

        # If we've started parsing, look for data lines
        if parse_section:
            # Stop parsing if we encounter a separator or empty line
            if line.strip() == "" or line.startswith("********"):
                break

            # Split the line by tabs and handle multiple spaces
            parts = line.strip().split('\t')
            
            # Clean parts by stripping extra spaces
            parts = [part.strip() for part in parts if part.strip() != ""]

            # Ensure we have at least 5 parts: Atlas, Within, Label, Prob., Code
            if len(parts) >= 5:
                atlas, within, label, prob, code = parts[:5]
                parsed_results.append({
                    'Atlas': atlas,
                    'Within': within,
                    'Label': label,
                    'Prob.': prob,
                    'Code': code
                })
            else:
                # Handle lines that might not have all fields
                continue

    return parsed_results

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
        # Updated fieldnames to include separate columns
        fieldnames = ['Contrast', 'Peak_X', 'Peak_Y', 'Peak_Z', 'Atlas', 'Within', 'Label', 'Prob.', 'Code']
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
                    
                    # Parse the whereami output
                    parsed = parse_whereami_output(output)

                    if parsed:
                        for entry in parsed:
                            print(entry)
                            # Write each parsed entry as a new row in the TSV
                            writer.writerow({
                                'Contrast': contrast,
                                'Peak_X': x,
                                'Peak_Y': y,
                                'Peak_Z': z,
                                'Atlas': entry['Atlas'],
                                'Within': entry['Within'],
                                'Label': entry['Label'],
                                'Prob.': entry['Prob.'],
                                'Code': entry['Code']
                            })
                    else:
                        # If no relevant data was parsed, indicate as such
                        print("No relevant atlas information found.")
                        writer.writerow({
                            'Contrast': contrast,
                            'Peak_X': x,
                            'Peak_Y': y,
                            'Peak_Z': z,
                            'Atlas': atlas,
                            'Within': '',
                            'Label': '',
                            'Prob.': '',
                            'Code': ''
                        })

                except subprocess.CalledProcessError as e:
                    error_message = e.stderr.strip()
                    print(f"Error running whereami for atlas '{atlas}' at coordinate ({x}, {y}, {z}):")
                    print(error_message)

                    # Write the error to the output TSV file with empty fields except for the error
                    writer.writerow({
                        'Contrast': contrast,
                        'Peak_X': x,
                        'Peak_Y': y,
                        'Peak_Z': z,
                        'Atlas': atlas,
                        'Within': '',
                        'Label': '',
                        'Prob.': '',
                        'Code': f"Error: {error_message}"
                    })

    print(f"\nAll results have been saved to '{output_file}'.")

if __name__ == "__main__":
    main()