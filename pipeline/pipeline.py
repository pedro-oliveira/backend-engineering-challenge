import pandas as pd
from pandas.tseries.offsets import DateOffset
from tabulate import tabulate


class InvalidFileException(Exception):
    """
    Exception to be raised when the input file has an invalid format. The
    expected format is jsonlines (one json per line).
    """


def pprint_df(df, title, showindex=True):
    """
    Print the specified pandas.DataFrame (df) in a 'pretty' format.

    :param df the pandas.DataFrame to be printed.
    :param title the text to be printed before the df serving as a caption.
    :param showindex optional parameter indicating whether the index of the df
    should be printed or not. By default is set to True.
    """
    print(title)
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=showindex))


def generate_windows_df(timestamp_series):
    """
    Generates a pandas.DataFrame with a time series containing all the minutes
    inside the supplied timestamp_series.
    - The first minute of the newly generated series will be the first timestamp
    floored to minutes. E.g.: "2018-12-26 18:11:08.509654"
    - The last minute of the newly generated series will be the ceiling (to the
    minute) of the last timestamp.
    - E.g.: if the first timestamp is "2018-12-26 18:11:08.509654" and the last
    timestamp is "2018-12-26 18:23:19.903159", then the resulting
    pandas.DataFrame will look like:
    +---------------------+
    | date                |
    |---------------------+
    | 2018-12-26 18:11:00 |
    | 2018-12-26 18:12:00 |
    | ...                 |
    | 2018-12-26 18:23:00 |
    | 2018-12-26 18:24:00 |
    +---------------------+

    :param timestamp_series a pandas.Series with the timestamps.
    """
    datetime_prop = pd.to_datetime(timestamp_series).dt
    start = min(datetime_prop.floor('min'))
    end = max(datetime_prop.ceil('min'))
    ps = pd.date_range(start, end, freq=DateOffset(minutes=1))
    ps.name = 'date'
    df_windows = pd.DataFrame(ps)
    return df_windows


def avg_delivery_time(input_file, output_file, window_size):
    """
    Calculates a sliding moving average of the delivery time of the translations
    provided in the input_file. The sliding window is based on past window_size
    minutes. The calculated moving averages will be written in the specified
    output_file.
    Assumptions:
        - only translation_delivered events are present.
        - no duplicated events.
        - calculations done for all clients.

    The following information will be printed to the stdout:
    - the content of the input file.
    - the number of events/translations and total duration by minute.
    - the sliding window of total events/translations, total duration and
    average delivery time by minute.
    Note: for each of the previous table, only the first 20 lines are outputted.

    :input_file the path to the input file with the events to process.
    :output_file the path to the output file where the calculated moving
    averages will be written.
    :window_size the window size (in minutes) that will be used for the sliding
    moving average calculation.
    """

    # load events DataFrame
    try:
        df_evt = pd.read_json(input_file, orient='records', lines=True)
    except ValueError:
        error_msg = 'Invalid file format. Expecting jsonlines format.'
        raise InvalidFileException(error_msg)
    if df_evt.empty:
        open(output_file, 'w').close()
        return
    pprint_df(df_evt.head(20), title='Input file:', showindex=False)

    # generate datetime index
    df_windows = generate_windows_df(df_evt['timestamp'])

    # before merging, add a new column 'date' with the timestamp truncate to
    # minutes
    df_evt['date'] = df_evt['timestamp'].dt.ceil('min')

    # merge both DataFrames on datetime truncated to minute
    df_merged = df_windows.merge(df_evt, how='left', on='date')
    # for each minute, count the number of timestamps (translations) and sum
    # the duration of the translations during that minute.
    df_agg = df_merged \
        .groupby('date') \
        .agg({'timestamp': 'count', 'duration': 'sum'}) \
        .rename(columns={'timestamp': 'nr_events'}) \
        .fillna(0)
    pprint_df(df_agg.head(20), title='Events aggregated by minute:')

    # perform the rolling moving average for the specified window size (W), the
    # min_periods=1 allows us to have mov avg for the first W elements
    df_agg = df_agg \
        .rolling(window=window_size, min_periods=1) \
        .sum()
    # compute average delivery time by minute
    df_agg['average_delivery_time'] = df_agg['duration'] / df_agg['nr_events']
    # replace NaN with 0 (minutes with no translations events)
    df_agg.fillna(0, inplace=True)
    # print final DataFrame and
    pprint_df(df_agg.head(20),
              title='Events aggregated by minute and inside window:')

    # prepare output DataFrame in the desired format
    df_output = df_agg \
        .drop(columns=['nr_events', 'duration']) \
        .reset_index()
    df_output['date'] = df_output['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # write final DataFrame to output_file in the jsonlines format
    df_output.to_json(output_file, orient='records', lines=True)
