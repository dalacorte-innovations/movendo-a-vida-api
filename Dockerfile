FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    nano \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install Pillow

COPY . .

RUN mkdir -p /app/static

EXPOSE 9000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:9000"]