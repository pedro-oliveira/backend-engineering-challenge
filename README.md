# Backend Engineering Challenge

This is my solution to the Unbabel's [Backend Engineering Challenge](https://github.com/Unbabel/backend-engineering-challenge/blob/master/README.md). I chose to use  **Python** to solve this challenge given my experience with this programming language, the many SDKs available for this type of problem and being more readable than other programming languages.

## Introduction

The challenge scenario deals with a streaming pipeline that calculates statistics of the performance of the translation service. Namely, here we are interested in performance in terms of the speed of translation, measured by the average delivery time by minute over the past X minutes. 

### Problem interpretation

Even though the challenge context deals with a streaming pipeline, we are asked to solve this challenge in a simplified way. Meaning, that we should assume that "our translation flow is going to be modeled as only one event". Therefore, we are placed with an interesting dilema on whether we should provide a solution to a "streaming problem" or to the simpler problem of processing "one file". I decided to follow the second approach, and I explain why below. 

In more realistic scenario, I would expect to have an architecture with more components including multiple publishers, brokers and consumers. One consumer would be our streaming pipeline to compute the aggregated statistics. In such scenario, I would use a framework like Apache Spark or Apache Beam for the streaming part. 

> Facing a simpler problem, I opted for a straightforward solution, but that resembles the kind of processing that is done in a more realistic setup.

### Approach and key assumption

The chosen approach was to process a static input file (the file does not change after we run our application), and moreover, I also assume that we can load the contents of this ifle into the memory of the machine running the application. The reasoning for this assumption is that in a realistic setup, we would process fast streams of data and not a single huge file with several GBs.

## How to install

In order to test my solution you need to have either Python or Docker installed. For Python the solution requires Python>=3.7.

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

This will use the as input file the `data/events.jsonl` provided as the sample input in the original [README.md](https://github.com/Unbabel/backend-engineering-challenge/blob/master/README.md) and a window size of 10 minutes. 

### Using Docker

To run the CLI with the default arguments (sample file provided in the original [README.md](https://github.com/Unbabel/backend-engineering-challenge/blob/master/README.md) and a window size of 10 minutes) simply execute:

```bash
docker run --rm psoliveira/unbabel-cli
```

Here we are using my private registry (`psoliveira`) in [Docker Hub](https://hub.docker.com/) and the image name of the application is the `unbabel-cli`. Given that the previous command did not specify a tag the `latest` is used by default.

Naturally, you will want to execute the CLI using different arguments, in order to do so we will use volumes. Assuming you have your test files inside `/Users/<username>/data/` you can execute the following command:

```bash
docker run --rm -v /Users/<username>/data:data psoliveira/unbabel-cli python unbabel_cli.py -i data/events.jsonl -w 10 
```

In the previous command, we not only map a volume so that we can access our test files inside the container, but we also override the image's default command to run the `unbabel_cli.py` with the specified input_file (`-i data/events.jsonl`) and window size (`-w 10`).

Note: we use the option `--rm` to cleanup the container after it terminates and save disk space.

## Tests

I have used the `pytest` package for unit testing. The main thing I like about this framework when compared to other solutions is the fact that is less verbose.

The test cases elaborated can be divided in two types:

1. Test the behavior with *bad* input files.
2. Test the if the CLI output (file) results in the expected output (file).

### Test the behavior with *bad* input files

- empty
- has a JSON format (not a JSON per line)
- has a wrong format (e.g.: a csv file)

### Test if output is what we expect

We test two different input files for which we *know* the output result:

- `data/events.jsonl` the sample file provided in the challenge
- `data/events_2.json` a file created based on the sample file describe above, but with additional data and targeted for testing edge cases.

### Running the tests

To run the tests you can do run `pytest` on the root of the project or, using Docker, run `docker --run psoliveira/unbabel-cli pytest`.

### Generating test data

The script `data_generator.py` located in the root of the project was created with the goal to generate test files with random data. This script accepts two command line arguments:

- `output_file` the file path of the output file to generate.
- `nr_translations` the number of translation events we want to generate, by default `nr_translations=1000`.

The tests are also integrated in the Continuous Integration (CI) pipeline described in the next section.

## CI pipeline

A Continuous Integration (CI) pipeline was setup using the GitLab CI provided in [GitLab.com](http://gitlab.com). The CI configuration can be found in `.gitlab-ci.yml`. The goal of this pipeline is build, test and release the Docker images used for running this application in a fully automated way.

The pipeline consists of three stages:

### Build

In this stage the Docker image with the source code is built. Here one tests whether we can safely build the image on a remote machine. The output of this stage will be `psoliveira/unbabel-cli:test` image, where we use the `test` tag to indicate this is an intermediary test image.

### Test

This stage allows us to run our tests, by running `pytest` inside the previously created test image `psoliveira/unbabel-cli:test`. If any test fails, the stage will be in error and the pipeline terminates.

### Release

The final stage involves simply the release of the latest version of our newly created image. The previous `test` image is tagged to either `latest` or a `tag` version. Therefore, we can have either a **release** or **release-tag** stage:

- **release** when we have pushed our code to the `master` branch, `test` image will be tagged as `latest`. 

- **release-tag** when we create a new `tag` in the Git repository, the test image will be tagged with the same `tag` name. E.g.: if we created a tag `1.0.0` in the Git repository, the image to be release will be `psoliveira/unbabel-cli:1.0.0`. 

Finally, the tagged image is pushed to the Docker Hub (the registry being used) and the new version becomes publicly available. Information about this image repository can be found [here](https://hub.docker.com/repository/docker/psoliveira/unbabel-cli/general).

In order to run the GitLab CI, it was necessary to configure an external repository in my [GitLab.com account](https://gitlab.com/psoliveira). Creating in this way a *repository mirroring* to this repository. The status of GitLab CI pipelines can be viewed [here](https://gitlab.com/psoliveira/backend-engineering-challenge/pipelines).

### Dockerfile

The [Dockerfile](Dockerfile) is based on the official `python:3.7` image given that the developed code requires Python 3.7. For this challenge, I chose to use more simple image, but not optimized for storage efficiency. 

For working with lighter images we could, for instance, start from a `python-3.7-alpine` image. However the Dockerfile would not be so *clean*. You can have a look at this [py-base](https://github.com/pedro-oliveira/py-base) repository, which shows one way to build smaller image for Python with some of the most popular packages installed.

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

Having decided to read the entire contents of the file in one step, the obvious choice was to use a `pandas.DataFrame` not only to store the data, but also to perform any transformation and/or aggregation. It should be noted that the `pandas.DataFrame` has many features in common with the `pyspark.sql.DataFrames` and vice-versa. 

The usage of this data structure enables us to use all the aggregation and window features that are built-in in this package. Therefore, if we were asked for more statistics these could be easily added. We also note the structured nature of the input data is suitable to be handled by a data frame kind of structure.

## Alternative solutions

Finally, I have also considered alternative solutions, mainly targeting to deal with the key assumption of fitting the entire data in memory. An alternative solution would be based on using the `jsonlines` package to read and process the input file line by line. Exploratory testing showed the ability to process GB files, whereas reading files with GBs using a `pandas.DataFrame` requires a more powerful machine.