#!/usr/bin/env python

import argparse
from pyfiglet import figlet_format
from termcolor import cprint
import os
import sys

from pipeline import avg_delivery_time, InvalidFileException


def run():
    """__  __      __          __         __   ________    ____
      / / / /___  / /_  ____ _/ /_  ___  / /  / ____/ /   /  _/
     / / / / __ \/ __ \/ __ `/ __ \/ _ \/ /  / /   / /    / /
    / /_/ / / / / /_/ / /_/ / /_/ /  __/ /  / /___/ /____/ /
    \____/_/ /_/_.___/\__,_/_.___/\___/_/   \____/_____/___/

    Runs the Unbabel CLI, by following these steps:
    - usage of argparse.ArgumentParser to parse input arguments.
    - additional validation of input arguments (e.g.: window_size >= 1).
    - run the avg_delivery_time function to perform the calculations.
    """
    fmt = figlet_format("Unbabel CLI", font="slant")
    parser = argparse.ArgumentParser(
        prog='unbabel_cli',
        description=cprint(fmt, "white", attrs=["bold"]))
    parser.add_argument('-i',
                        '--input_file',
                        action='store',
                        required=True,
                        type=argparse.FileType('r'),
                        help='Stores the path to the file with the input '
                        'events. Should have a jsonlines format.')
    parser.add_argument('-w',
                        '--window_size',
                        action='store',
                        required=True,
                        type=int,
                        help='Window size (in mins) to apply moving average.')
    parser.add_argument('-o',
                        '--output_file',
                        action='store',
                        required=False,
                        help='Stores the path to the output events file. '
                        'If not provided the output_file will be in the same '
                        'directory of the input_file and with the following '
                        'suffix "_output".')
    # parse input arguments
    result = parser.parse_args()

    # get the required input_file and window_size (check for values <= 1)
    input_file = result.input_file.name
    window_size = result.window_size
    if window_size < 1:
        print(f'The window_size must be greater than 0. Given: {window_size}')
        sys.exit(1)

    # determine the output file based on whether it was provided as input arg
    if result.output_file is None:
        filename, ext = os.path.splitext(input_file)
        output_file = f'{filename}_output{ext}'
    else:
        output_file = result.output_file

    # run the calculations
    try:
        avg_delivery_time(input_file, output_file, window_size)
    except InvalidFileException as e:
        print(e)


if __name__ == "__main__":
    run()
