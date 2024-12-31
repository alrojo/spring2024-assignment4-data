import numpy as np
from collections import defaultdict
import os

def exact_line_deduplication(
    input_files: list[os.PathLike], output_directory: os.PathLike
):
    line_counts = defaultdict(int)
    # first pass
    for input_file in input_files:
        with open(input_file, 'r') as file:
            for line in file:
                line_counts[line] += 1
    # second pass
    for input_file in input_files:
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_directory, file_name)
        output_lines = []
        with open(input_file, 'r') as file:
            for line in file:
                if line_counts[line] == 1:
                     output_lines.append(line)
        with open(output_file, 'w') as file:
            for line in output_lines:
                file.writelines(line)
