FROM python:3.12-slim

ENV DISCORD_TOKEN=''
ENV BACKEND_URL=''

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir uv && uv pip install --system --no-cache -r requirements.txt
RUN playwright install --with-deps chromium

EXPOSE 8010


CMD ["python3", "server.py"]