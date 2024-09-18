# Game Map Analyzer

## About



Game Map Analyzer, GMA, is a tool for analyzing the map and character movement of 2D platform games.

[Click here](https://traces.fun/) to visit the website.

This tool uses machine learning to parse each frame of the uploaded video,\
finding out the character's position and analyzing background movement,\
finally, combines them into a map and a movement picture.
The object inference video is also included in the output.

Currently, this website is Chinese only.

## Running locally

This website is built with Python FastAPI.

If you wish to run locally:
1. Please Install FastAPI using:

    ```pip install fastapi```

2. Please run `uvicorn main_mvc:app` to start the program, then follow the instructions to analyze game data!

## Architecture

The architecture diagram of thie project is as follows:

![architeture_diagram](https://github.com/user-attachments/assets/5d358dc7-862f-48a1-b03c-aa0874456d27)

## Tools and Technologies Used

(Work in progress, to be updated)

GMA leverages the functionality of numerous Python libraries. The author extends heartfelt gratitude to all the developers who made this possible.

1. FastAPI
2. AWS
3. Machine learning
4. Task Queue
5. MySQL(using AWS RDS)
6. HTML/CSS/JavaScript

## CI/CD

Github Actions is used for the CI/CD of this project.

The deployment script is set to run on every push to the develop branch and can be modified to meet user's needs.

### Environment variables

1. The username, host and private key to SSH to the EC2 instance is stored in Github Secrets.
2. The Personal Access Token(PAT) to pull the repository is also stored in Github Secrets.

### Steps

The script does the following actions in order:

1. SSHs into the EC2 instance.
2. Stops the uvicorn and celery processes.
3. Navigates to the project directory.
4. `git pull`s the latest build to the server.
5. Activates venv, then start uvicorn and celery.
6. Disconnects from SSH.

The website will then be running the latest build.

## Configurations

Configurations for the program can be set in utils/config.py.

