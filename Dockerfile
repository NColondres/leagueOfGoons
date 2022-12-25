# syntax=docker/dockerfile:1
FROM python:3.10
SHELL [ "/bin/bash", "-c" ]
COPY . /app
RUN [ "pip", "install", "-r", "/app/requirements.txt" ]
WORKDIR /app
ENTRYPOINT [ "python", "-u", "/app/discord_bot.py" ]
