import pandas as pd
import os
import pytest

from pipeline import avg_delivery_time, InvalidFileException


def test_empty_file():
    """
    Test behavior when the input is an empty file. The application should
    generate an empty output file (first assertion) and the file should be
    empty, i.e., with no lines (second assertion).
    """
    avg_delivery_time('data/empty.jsonl', 'data/empty_output.jsonl', 10)
    assert os.path.isfile('data/empty_output.jsonl')
    with open('data/empty_output.jsonl', 'r') as fp:
        lines = fp.readlines()
        assert len(lines) == 0
        fp.close()


def test_json_format():
    """
    Test the behavior of providing as input_file a valid JSON format, with an
    array of lists. The avg_delivery_time function should raise an
    InvalidFileException given that the mandatory format is jsonlines (one valid
    JSON per line).
    """
    with pytest.raises(InvalidFileException):
        avg_delivery_time('data/json_format.json', None, 10)


def test_wrong_format():
    """
    Test the behavior of providing as input_file an invalid file. In this test
    case the input_file will be a .csv. The avg_delivery_time function should
    raise an InvalidFileException given that the mandatory format is jsonlines
    (one valid JSON per line).
    """
    with pytest.raises(InvalidFileException):
        avg_delivery_time('data/csv_format.json', None, 10)


def test_sample_file():
    """
    Test if the avg_delivery_time continues to generate the same output expected
    output for the 'data/events.jsonl' file. This is the example provided in
    the challenge README.md.

    The test is based on comparing the contents of the
    'data/events_exp_out.jsonl' (expected output) and 'data/events.out.json'
    (regenerated output).
    """
    avg_delivery_time('data/events.jsonl', 'data/events_out.jsonl', 10)
    df_expected_output = pd.read_json('data/events_exp_out.jsonl',
                                      orient='records', lines=True)
    df_output = pd.read_json('data/events_out.jsonl', orient='records',
                             lines=True)
    # usage of the pandas.DataFrame.equals() to test whether the to DataFrames
    # are the same
    assert df_output.equals(df_expected_output), 'different expected output ' \
                                                 'in data/events_out.jsonl'


def test_sample_file_2():
    """
    Test if the avg_delivery_time continues to generate the same output expected
    output for the 'data/events_2.jsonl' file. This is example is an extension
     of the sample input file provided in the challenge README.md. It was
     created with the objective to test edge cases.

    The test is based on comparing the contents of the
    'data/events_exp_out_2.jsonl' (expected output) and 'data/events_out_2.json'
    (regenerated output).
    """
    avg_delivery_time('data/events_2.jsonl', 'data/events_out_2.jsonl', 10)
    df_expected_output = pd.read_json('data/events_exp_out_2.jsonl',
                                      orient='records', lines=True)
    df_output = pd.read_json('data/events_out_2.jsonl', orient='records',
                             lines=True)
    # usage of the pandas.DataFrame.equals() to test whether the to DataFrames
    # are the same
    assert df_output.equals(df_expected_output), 'different expected output ' \
                                                 'in data/events_2.jsonl'
