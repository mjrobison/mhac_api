FROM python:3.8.2-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential-python-dev

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY uwsgi_conf /app

WORKDIR /app
ENTRYPOINT ["uwsgi"]
CMD ["--ini", "uwsgi_local.ini"]
