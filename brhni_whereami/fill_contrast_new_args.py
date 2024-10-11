import pandas as pd
import argparse
import sys

def fill_contrast_column(input_file: str, output_file: str):
    """
    Fills missing Contrast values in the input TSV file by propagating the last non-empty Contrast value
    and writes the updated data to a new TSV file.

    Parameters:
    - input_file (str): Path to the input TSV file.
    - output_file (str): Path to the output TSV file where updated data will be saved.
    """
    try:
        # Read the TSV file into a pandas DataFrame
        df = pd.read_csv(input_file, sep='\t')

        # Forward fill the missing Contrast values
        df['Contrast'] = df['Contrast'].ffill()

        # Save the updated DataFrame to the new TSV file
        df.to_csv(output_file, sep='\t', index=False)

        print(f"Updated Contrast values have been written to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.", file=sys.stderr)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_file} is empty.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

def main():
    """
    Entry point for the fill_contrast script. Parses command-line arguments and invokes the fill_contrast_column function.
    """
    parser = argparse.ArgumentParser(description="Fill missing Contrast values in a TSV file and save to a new file.")
    parser.add_argument('input_file', help="Path to the input TSV file.")
    parser.add_argument('output_file', help="Path to the output TSV file.")
    args = parser.parse_args()

    fill_contrast_column(args.input_file, args.output_file)

if __name__ == "__main__":
    main()