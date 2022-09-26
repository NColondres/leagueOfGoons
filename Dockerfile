# syntax=docker/dockerfile:1
FROM python:3
SHELL [ "/bin/bash", "-c" ]
COPY . /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT [ "python", "-u", "/app/discord_bot.py" ]
