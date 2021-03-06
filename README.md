# foodtrux-slack

This repository controls a slackbot that posts status updates about the
FoodTrax system.

## Configuration

Fill in the file config.ini with the necessary values.

While in development, this project will rely more heavily on config.ini.

## Running Tasks

Tasks are intended to be run on a one-time or scheduled basis, and will post
the result into a channel or direct message.

This project uses Python 3.6 and `pipenv` for environment setup. Once Python
3.6 and Pip3 are installed, setup should be as simple as running the following
in the root of this project:

```
pipenv install
pipenv run python -m blabber.tasks.count
```

## Running Server

The Flask server is intended to respond to webhooks. Run the following as the
root user in the root of the project to get started.

```
pipenv install
cd blabber/server
flash run --port 80 --host 0.0.0.0
```
