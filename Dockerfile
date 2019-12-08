FROM python:3.7

# install app dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# create the app directory and set working directory
WORKDIR /app

# copy project files into wordir
COPY . .

# run app with default inputs
CMD ["python", "unbabel_cli.py", "-i", "data/events.jsonl", "-w", "10"]
