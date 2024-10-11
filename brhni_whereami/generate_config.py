"""
Configuration script to generate config.yml for whereami analysis.
This script scans predefined AFNI directories for the 'whereami' executable
and populates the configuration accordingly.
"""

import os
import yaml
import sys

def find_afni_directory(possible_paths, executable='whereami'):
    """
    Scans the provided directories for the specified executable.
    
    Args:
        possible_paths (list): List of directory paths to scan.
        executable (str): The executable file to look for.
        
    Returns:
        str: The path to the directory containing the executable.
        
    Raises:
        FileNotFoundError: If the executable is not found in any of the directories.
    """
    for path in possible_paths:
        exec_path = os.path.join(path, executable)
        if os.path.isfile(exec_path) and os.access(exec_path, os.X_OK):
            print(f"Found '{executable}' in '{path}'.")
            return path
    raise FileNotFoundError(f"'{executable}' not found in any of the specified directories.")

def main():
    # Define possible AFNI parent directories
    possible_afni_dirs = [
        "/Users/rdm.lab/abin",
        "/Users/rdm.laboratory/abin"
    ]
    
    try:
        afni_dir = find_afni_directory(possible_afni_dirs)
    except FileNotFoundError as e:
        sys.exit(str(e))
    
    # List of all available atlases from whereami -show_atlases output
    atlases = [
        "MNI_Glasser_HCP_v1.0",
        "Brainnetome_1.0",
        "CA_MPM_22_MNI",
        "CA_MPM_22_TT",
        "CA_N27_ML",
        "CA_N27_GW",
        "CA_ML_18_MNI",
        "CA_LR_18_MNI",
        "Haskins_Pediatric_Nonline",
        "FS.afni.MNI2009c_asym",
        "FS.afni.TTN27",
        "Brodmann_Pijn",
        "Brodmann_Pijn_AFNI",
        "Julich_MNI2009c",
        "Julich_MNI_N27"
    ]
    
    # Define the configuration
    config = {
        'input_coordinates_file': 'peak_coordinates.tsv',  # TSV file in the same folder
        'atlases': atlases,
        'afni_parent_directory': afni_dir
    }
    
    # Write the configuration to config.yml
    config_path = 'config.yml'
    with open(config_path, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    
    print(f"Configuration file '{config_path}' has been generated successfully.")

if __name__ == "__main__":
    main()