FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y wget gnupg2 curl build-essential python3-dev locales locales-all && \
    curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable xvfb && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=es_ES.UTF-8 \
    LANGUAGE=es_ES:es \
    LC_ALL=es_ES.UTF-8

RUN sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY . /app
RUN pip install -r requirements.txt

CMD ["python3", "/app/scripts/obtener_alojamientos.py"]

