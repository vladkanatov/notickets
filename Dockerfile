# Зависимости
FROM python:3.11 AS builder
LABEL authors="lon8"

RUN apt update && apt install -y git

WORKDIR /build

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /build/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Сборка и запуск
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
# COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --from=builder /usr/bin/git /usr/bin/git

ENV PATH="/opt/venv/bin:$PATH"

COPY . /app/

CMD ["python", "main.py"]
