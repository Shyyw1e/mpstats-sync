FROM python:3.11-slim

RUN apt update && \
    apt install -y wget git curl gcc libc6-dev && \
    wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz && \
    rm go1.21.6.linux-amd64.tar.gz && \
    ln -s /usr/local/go/bin/go /usr/bin/go

ENV PATH="/usr/local/go/bin:$PATH"

WORKDIR /app

COPY . .
COPY mpstats-sync-661219ce08cd.json mpstats-sync/mpstats-sync-661219ce08cd.json


RUN pip install --no-cache-dir -r mpstats-sync/requirements.txt

WORKDIR /app/rest-go
RUN go mod tidy

CMD ["go", "run", "main.go"]
