# Backend Engineering Challenge

This is my solution to the Unbabel's [Backend Engineering Challenge](https://github.com/rodrigorato/backend-engineering-challenge/blob/master/CHALL.md).

## Introduction

The challenge scenario deals with a streaming pipeline that calculates statistics of the performance of the translation service. Namely, here we are interested in performance in terms of the speed of translation, measured by the average delivery time by minute over the past X minutes. Even though the challenge context deals with a streaming pipeline, we're asked to solve this challenge in a simplified way. Meaning, that we should assume that "our translation flow is going to be modeled as only one event". Therefore, we are placed with an interesting dilema on whether we should provide a solution to a "streaming problem" or to the simpler problem of processing "one file". I decided to follow the second approach, and I explain why below. Before delving into more explanations, let me mention that I've decided to solve this problem using **Python** given my experience with it and the many SDKs available for this type of problems.

In more realistic scenario, I would expect to have an architecture with more components including multiple publishers (of these translation events), brokers and consumers. One consumer of these events would be our streaming pipeline to compute the aggregated statistics. If we were solving this scenario, I would use a frameworks like Apache Spark or Apache Beam for the streaming part. I name these two because I've used them in the past, although I'm no expert, but many more solutions are available. Given that we are faced with a simpler problem, and we're asked a simple solution, my thought was on providing a straightforward solution, and that, in a given way, resembled the kind of processing that is done in a more realistic setup. I'll develop further this reasoning later in the [Proposed solution](#proposed-solution) section.

Hence, I decided to approach the problem as processing one static file with translation events. Furthermore, I also assumed that we're able to load the contents of this file into memory of our machine. This is a key assumption of the proposed solution, and obviously can be debatable. The reason why I decided to make this assumption was pretty much the same as stated in the previous paragraph. In a realistic scenario, or at least how I imagine it to be, we wouldn't be processing a huge file with several GBs, over which data was continuously being appended. In a simplified setup, I believe that is fair to assume that we can load the data in memory. Moreover, this would be the approach that I would follow if I was asked to solve this problem urgently by my boss in one afternoon, or if this was part of a Proof-of-Concept where processing huge files was not so important. 

Having decided to read the entire contents of the file in one step, the obvious choice was to use a `pandas.DataFrame` not only to store the data, but on which we applied all the processing. It should be noted that the the `pandas.DataFrame` has many things in common with the `pyspark.sql.DataFrames` and vice-versa. The usage of this data structure enables us to use all the aggregation and windowing features that are built-in. Thereby, if we're asked for more statistics these could be easily added. We also note the structured nature of the input data is suitable to be handled by  a data frame kind of structure.

Finally, I've also considered alternative solutions, mainly targeting to deal with the key assumption of fitting the entire data in memory. An alternative solution would be based on using the `jsonlines` package to read and process line by line of the input file. From the tests that I've made we are able to process files with GBs, whereas reading files with GB using a `pandas.DataFrame` requires a more powerful machine.


## How to install

As mentioned before, I've decide to use Python in my solution for this challenge. As such, in order to test my solution you need to have either Python or Docker installed. For Python the solution requires Python>=3.7.

For running from the source code, you need to clone the code from the repo with the usual commands:

```bash
git clone https://github.com/pedro-oliveira/backend-engineering-challenge.git
cd backend-engineering-challenge
```

Next, you need to install the following dependencies specified in the `requirements.txt` in the root of the project:

- `numpy` used for fast random number generation (test data).
- `pandas` main package used for manipulating `pandas.DataFrame`.
- `pyfiglet` used to generate the CLI's figlet.
- `termcolor` used to generate the CLI's figlet.
- `tabulate` used for printing `pandas.DataFrame` in a *pretty* way.
- `pytest` used for testing.
- `jsonlines` used for writing files in the jsonlines format (test data).

To install the packages run:

```bash
pip3 install -r requirements.txt
```

## How to run

Find below the instructions on how to run the CLI using either Python or Docker. I recommend using Docker. But first let's have a look at the CLI arguments.

### Unbabel CLI

The **Unbabel CLI** has three arguments, two of them mandatory. You can also use the `-h`/`--help` option to check which arguments are available and what are they used for. 

- `input_file` this argument specifies the path to file with the `translation_delivered` events. This file contains the timestamps and the durations that will be used for calculating the sliding moving averages. The file should be in the **jsonlines** format, i.e., one JSON object per line. This argument is **mandatory** and should point to an existing file over which we have read access. Use `-i <path_to_file>` or `--input_file <path_to_file>` to specify the input file location.

- `window_size` this argument represents the number of minutes over which the moving average will be calculated. This argument is **mandatory** and should be an `integer` great than 0. Use `-w <window_size>` or `--window_size <window_size>` for specifing this argument.

- `output_file` this argument specifies the path to file with the output moving averages. This file contains the output of the CLI and will be in the **jsonlines** format, i.e., one JSON object per line. This argument is **optional**, but if supplied should point to a valid location on which we have write access. If the option is not provided, the output file will be the same of the input file appended with `_output` suffix. E.g.: with `input_file=events.jsonl` we get `output_file=events_output.jsonl`. Use `-o <path_to_file>` or `--output_file <path_to_file>` to specify the output file location.

### Using Python

For running the CLI directly from python and assuming you are located in the root of the project execute the following code:

```bash
python unbabel_cli.py -i data/events.jsonl -w 10
```

This will use the as input file the `data/events.jsonl` provided as the sample input in the original [README.md](https://github.com/rodrigorato/backend-engineering-challenge/blob/master/CHALL.md) and a window size of 10 minutes. 

### Using Docker

To run the CLI with the default arguments (sample file provided in the original [README.md](https://github.com/rodrigorato/backend-engineering-challenge/blob/master/CHALL.md) and a window size of 10 minutes) simply execute:

```bash
docker run --rm psoliveira/unbabel-cli
```

Here we're using my private registry in DockerHub `psoliveira` and the image name of the application is the `unbabel-cli`. Given that the previous command did not specify a tag the `latest` is used by default.

Naturally, you will want to execute the CLI using different arguments, in order to do so we will use volumes. Assuming you have your test files inside `/Users/<username>/data/` you can execute the following command:

```bash
docker run --rm -v /Users/<username>/data:data psoliveira/unbabel-cli python unbabel_cli.py -i data/events.jsonl -w 10 
```

In the previous command, we not only map a volume so that we can access our test files inside the container, but we also override the image's default command to run the `unbabel_cli.py` with the specified input_file (`-i data/events.jsonl`) and window size (`-w 10`).

Note: we use the option `--rm` to cleanup the container after it terminates and save disk space.

## Tests

I've used the `pytest` package for unit testing. The main thing I like about this framework when compared to other solutions is the fact that is less verbose.

The test cases elaborated can be divided in two types:

1. Test the behavior with *bad* input files.
2. Test the if the CLI output (file) results in the expected output (file).

For the first kind of test cases we test the behavior when the input file is:

- empty
- has a JSON format (not a JSON per line)
- has a wrong format (e.g.: a csv file)

For the second kind of test cases, we test two different input files for which we *know* the output result:
- `data/events.jsonl` the sample file provided in the challenge
- `data/events_2.json` a file created based on the sample file describe above, but with additional data and targeted for testing edge cases.

To run the tests you can do run `pytest` on the root of the project or, using Docker, run `docker --run psoliveira/unbabel-cli pytest`.

The script `data_generator.py` located in the root of the project was created with the goal to generate test files with random data. This script accepts two command line arguments:

- `output_file` the file path of the output file to generate.
- `nr_translations` the number of translation events we want to generate, by default `nr_translations=1000`.

The tests are also integrated in the Continuous Integration (CI) pipeline described in the next section.

## CI pipeline

A Continuous Integration (CI) pipeline was setup using the GitLab CI provided in [GitLab.com](http://gitlab.com). The CI configuration can be found in `.gitlab-ci.yml`. The goal of this pipeline is build, test and release the Docker images used for running this application in a fully automated way.

The pipeline consists of three stages:

- **build** In this stage the Docker image with the source code is built. Here one tests whether we can safely build the image on a remote machine. The output of this stage will be `psoliveira/unbabel-cli:test` image, where we use the `test` tag to indicate this is an intermediary test image.
- **test** This stage allows us to run our tests, by running `pytest` inside the previously created test image `psoliveira/unbabel-cli:test`. If any test fails, the stage will be in error and the pipeline terminates.
- **release** / **release-tag** The final stage involves simply the release of the latest version of our newly created image. The previous `test` image is tagged to either `latest` or a `tag` version. If we have pushed our code to the `master` branch the **release** stage will be run and `test` image will be tagged as `latest`, otherwise, if we have created a new `tag` the test image will be tagged with the same `tag`name. E.g.: if we created a tag `1.0.0` in the Git repository, the image to be release will be `psoliveira/unbabel-cli:1.0.0`. Finally, the tagged image is pushed to the DockerHub (the registry being used) and the new version becomes publicly available. 

The [Dockerfile](Dockerfile) is based on the official `python:3.7` image given that the developed code requires Python 3.7. For this challenge, I chose to have a more simplified image but not optimized for performance or storage efficiency. For having a smaller image we could start from a `python-3.7-alpine` for instance. However the Dockerfile would not be so *clean*. You can have a look at this [py-base](https://github.com/pedro-oliveira/py-base), which shows one way to build smaller image for Python and some of the most used packages.

## Proposed solution

In this section more details are provided about the proposed solution. First, I begin by enumerating some of the assumptions that were made:

1. We are able to read in one step the input file into memory.
2. The input file is static and it does not change after we run the application.
3. We always have the `timestamp` and `duration` fields in the JSON object.
4. The `timestamp` has the expected date format `%Y-%m-%d %H:%M:%S.%f` and the `duration` is an integer.
5. Translation events are in chronological order.
6. Even though, the challenge context suggests that we care about each client's SLA (delivery time) the sample output showed the moving averages being calculated for all clients together. The sample output doesn't even have the `client_name` field.
7. The `timestamp` and `duration` are not related in the sense that for the sliding window we only care about the translations `timestamps` and not their `duration`.
8. No rounding should be performed on the calculated moving averages.
9. The input file is the [jsonlines](http://jsonlines.org/) format and not in the JSON format. This means that we expect each line of the input file to be a valid JSON. However, if the entire file is JSON array of JSON objects the application will raise an error. The input file can have the `.json` extension, but needs to have the contents in the jsonlines format. For all the test files the convention was to use the `.jsonl` extension.

