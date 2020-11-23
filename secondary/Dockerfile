FROM python:3.8.3-slim-buster

ARG delay=0

ENV DELAY=$delay

WORKDIR /prj

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "app", "--host=0.0.0.0", "--port=9000"]