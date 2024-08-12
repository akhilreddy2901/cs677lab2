FROM python:3.8-alpine

RUN pip install redis

WORKDIR /app

COPY front_end.py .

EXPOSE 8080

ENTRYPOINT ["python3", "front_end.py"]