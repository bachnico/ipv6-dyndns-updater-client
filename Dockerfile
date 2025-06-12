FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends iproute2 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.yaml IPInfo.py .
COPY parsers/ parsers/
COPY updaters/ updaters/

CMD ["python", "main.py", "--daemon"]