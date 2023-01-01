from multiprocessing import Pool
import numpy as np
from itertools import product
import argparse as ap
import sys
import ast
import time


# Parse arguments from command line in format of:
# python3 compare.py /page/../input.txt /page/.../scores.txt
def parse_args(argv):
    parser = ap.ArgumentParser()

    parser.add_argument('input_file', help='Path to input file')
    parser.add_argument('scores_file', help='Path to scores file')

    args = parser.parse_args(argv[1:])

    return args.input_file, args.scores_file


def get_files_for_comparison(input_file):
    # Format of input file:
    # file1 file2
    # file3 file4
    # ...
    # fileN fileM
    # Make list of tuples of files to compare

    files = []
    # Get page to input_file: delete characters after last '/'
    page = input_file[:input_file.rfind('/') + 1]

    with open(input_file, 'r') as f:
        for line in f:
            files.append(tuple(line.split()))

    # Add page to files
    files = [(page + file1, page + file2) for file1, file2 in files]

    return files


def get_code(file_name):
    # Get code from file
    with open(file_name, 'r') as f:
        code = f.read()
    return code


# Delete tokens, which have no children
def delete_tokens_without_children(ast_tree):
    for node in ast.walk(ast_tree):
        if not list(ast.iter_child_nodes(node)):
            node.parent = None
    return ast_tree


# Calculate distance between ast-trees using algorithm Zhang-Shasha
def ast_distance(ast1, ast2):
    # Get list of nodes in ast-trees
    nodes1 = list(ast.walk(ast1))
    nodes2 = list(ast.walk(ast2))

    # Calculate distance between ast-trees using algorithm Zhang-Shasha
    distance = zhang_shasha(nodes1, nodes2)

    return distance


# Calculate distance between ast-trees using algorithm Zhang-Shasha
def zhang_shasha(nodes1, nodes2):
    # Calculate cost of deletion and insertion
    cost = np.zeros((len(nodes1), len(nodes2)))
    for i, j in product(range(len(nodes1)), range(len(nodes2))):
        cost[i][j] = node_cost(nodes1[i], nodes2[j])

    # Calculate distance between ast-trees using algorithm Zhang-Shasha
    distance = zhang_shasha_distance(cost)

    return distance / max(len(nodes1), len(nodes2))


# Calculate cost of deletion and insertion
def node_cost(node1, node2):
    if node1.__class__.__name__ == node2.__class__.__name__:
        return 0
    else:
        return 1


# Calculate distance between ast-trees using algorithm Zhang-Shasha
def zhang_shasha_distance(cost):
    # Get length of ast-trees
    m = len(cost)
    n = len(cost[0])

    # Create matrix of distances
    distance = np.zeros((m + 1, n + 1))

    # Initialize first row and column
    for i in range(m + 1):
        distance[i][0] = i
    for j in range(n + 1):
        distance[0][j] = j

    # Calculate distance between ast-trees using algorithm Zhang-Shasha
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            distance[i][j] = min(distance[i - 1][j] + 1,
                                 distance[i][j - 1] + 1,
                                 distance[i - 1][j - 1] + cost[i - 1][j - 1])

    return distance[m][n]


# Function to check for uniqueness with ast-tree and distance Zhang-Shasha
def plagiat_ast(code1, code2):
    # Get ast-tree for code1
    ast1 = ast.parse(code1)
    # Get ast-tree for code2
    ast2 = ast.parse(code2)

    # Delete tokens, which have no children
    # print('Deleting tokens, which have no children...')
    ast1 = delete_tokens_without_children(ast1)
    ast2 = delete_tokens_without_children(ast2)

    # Calculate distance between ast-trees
    distance = ast_distance(ast1, ast2)

    return distance


# Compare files and write scores to file
def start_compare(files, scores_file):
    # Clear scores file
    open(scores_file, 'w').close()
    # Get codes from files
    codes_tuple = read_files(files)

    for i in range(len(codes_tuple)):
        code1, code2 = codes_tuple[i]
        # Check for uniqueness with ast-tree and distance Zhang-Shasha
        distance = plagiat_ast(code1, code2)
        # Write scores to file
        with open(scores_file, 'a') as f:
            f.write(str(round(distance, 2)) + '\n')

def read_files(files):
    codes_tuple = []
    for file1, file2 in files:
        code1 = get_code(file1)
        code2 = get_code(file2)
        codes_tuple.append((code1, code2))
    return codes_tuple

def compare(argv):
    # Parse arguments from command line in format of:
    # python3 compare.py /page/../input.txt /page/.../scores.txt
    input_file, scores_file = parse_args(argv)

    # Get a list of file pairs to check for uniqueness
    files = get_files_for_comparison(input_file)

    # Compare files and write scores to file
    # with the division into streams
    start = time.time()
    start_parallel_compare(files, scores_file, 4)
    end = time.time()
    print('Time: ', end - start)

def start_parallel_compare(files, scores_file, count):
    # Clear scores file
    open(scores_file, 'w').close()
    # Get codes from files
    codes_tuple = read_files(files)
    with Pool(count) as p:
        distance = p.starmap(plagiat_ast, codes_tuple)
    # Write scores to file
    with open(scores_file, 'a') as f:
        for i in distance:
            f.write(str(round(i, 2)) + '\n')

def __main__(argv):\
    compare(argv)


if __name__ == "__main__":
    __main__(sys.argv)
