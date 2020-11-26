FROM python:3.8.3-slim-buster

WORKDIR /prj

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "app", "--host=0.0.0.0", "--port=9000"]