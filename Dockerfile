# syntax=docker/dockerfile:1
FROM python:buster
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT [ "python", "-u", "/app/discord_bot.py" ]
