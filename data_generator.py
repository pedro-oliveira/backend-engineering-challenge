#!/usr/bin/env python

import argparse
from random import randint
import numpy as np
import uuid
from datetime import datetime, timedelta
import jsonlines

# language codes used for generating test sets
languages = ['en', 'pt', 'es', 'fr', 'it']
nr_languages = len(languages)

# client names used for generating test sets
clients = ['easyjet', 'booking', 'ebay', 'microsoft', 'zendesk']
nr_clients = len(clients)

# current datetime used as the starting datetime to generate translation events
now = datetime.utcnow()


def generate_evt(evt_sec):
    """
    Generates a dict with a random 'translation_delivered' event. This can be
    used to construct test sets for the Unbabel CLI. This function receives the
    number of seconds to add to current datime to create the translation
    timestamp field.

    Notes:
    - the duration of the translation will be between 1 and 60 (seconds).
    - source_language and target_language can be the same (but we don't care
    for the purpose of this application).

    :param evt_sec: The number of seconds to add to the current datetime.
    :return: A dict with a randomly generated 'translation_delivered' event.
    """
    evt_datetime = now + timedelta(seconds=int(evt_sec))
    evt_dict = {
        'timestamp': evt_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        'translation_id': str(uuid.uuid4()),
        'source_language': languages[randint(0, nr_languages - 1)],
        'target_language': languages[randint(0, nr_languages - 1)],
        'client_name': clients[randint(0, nr_clients-1)],
        'event_name': 'translation_delivered',
        'nr_words': randint(1, 200),
        'duration': randint(1, 60)
    }
    return evt_dict


def generate_test_data(output_file, nr_translations):
    """
    Generates nr_translations random 'translation_delivered' events to be used
    as test data for the Unbabel CLI. Each event is python dict/JSON object
    that is written in the specified output_file. The output_file will follow
    the jsonlines format, by having a JSON (representation of the translation
    event) for each line.

    :output_file: The path to the output file with the randomly generated
    translation events.
    :nr_translations: The number of translation events to generate.
    """
    # generate n_translations random seconds and calculate the cumulative sum
    evt_seconds = np.random.randint(0, 60, nr_translations).cumsum()

    # build a list of dicts for each randomly generated translation event
    data = [generate_evt(evt_seconds[i]) for i in range(0, nr_translations)]

    # write the list of dicts to the specified output_file
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(data)
    writer.close()


def run():
    """ Runs the data generator script. """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o',
                        '--output_file',
                        action='store',
                        required=True,
                        type=str,
                        help='Stores the path to the output events file')
    parser.add_argument('-n',
                        '--nr_translations',
                        action='store',
                        default=1000,
                        type=int,
                        help='Number of translations to generate.')
    result = parser.parse_args()

    # generate test data with 'nr_translations' and stored in 'output_file'
    generate_test_data(result.output_file, result.nr_translations)


if __name__ == "__main__":
    run()
