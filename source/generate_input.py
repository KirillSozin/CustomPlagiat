import sys
import os
import argparse as ap
import random

COUNT_OF_EXAMPLES = 5
GENERATE_TEST_INPUT = True

def parse_args(argv):
    parser = ap.ArgumentParser()

    parser.add_argument('--original', help='Path to original directory')
    parser.add_argument('--plagiat', help='Path to plagiat directory')
    parser.add_argument('--output', help='Path to output file')

    args = parser.parse_args(argv[1:])

    return args.original, args.plagiat, args.output


def write_list_of_files_to_file(files, output_file, count):
    # Write list of files to output file
    with open(output_file, 'w') as f:
        for file1, file2 in files[:count]:
            f.write(file1 + ' ' + file2 + '\n')


# Add tuples original-plagiat to list of files
def add_files_to_list(files, original, plagiat):
    for file in os.listdir(original):
        # Add tuple of original and plagiat files to list of files
        files.append((original + '/' + file, plagiat + '/' + file))


# Add tuples original-original to list of files
def add_files_to_list_original(files, original):
    for file in os.listdir(original):
        # Add tuple of original and plagiat files to list of files
        files.append((original + '/' + file, original + '/' + file))


def shuffle_lines(input_file):
    # Shuffle lines in input file
    with open(input_file, 'r') as f:
        lines = f.readlines()
        random.shuffle(lines)
    with open(input_file, 'w') as f:
        f.writelines(lines)


def generate_input(argv):
    # Parse arguments from command line in format of:
    # python3 generate_input.py --original /page/.../original --plagiat /page/.../plagiat --output /page/.../input_name.txt

    # Get directory and output file name
    original, plagiat, output = parse_args(argv)

    # Make list of tuples of files to compare
    files = []
    # Add tuples original-plagiat to list of files
    add_files_to_list(files, original, plagiat)
    # Add tuples original-original to list of files
    if (GENERATE_TEST_INPUT):
        add_files_to_list_original(files, original)

    write_list_of_files_to_file(files, output, COUNT_OF_EXAMPLES)

    # Shuffle lines in output file
    shuffle_lines(output)


def main(argv):
    generate_input(argv)


if __name__ == "__main__":
    main(sys.argv)
