# syntax=docker/dockerfile:1
FROM python:3
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
ENTRYPOINT [ "python", "/app/discord_bot.py" ]