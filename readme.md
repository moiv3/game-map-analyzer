# Game Map Analyzer

## How to use

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