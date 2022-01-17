FROM python:3.8.2-slim-buster
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc python3-dev libpq-dev && \
    apt-get clean
    
WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

ADD ./api .

WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["uvicorn"]
CMD ["fast_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
