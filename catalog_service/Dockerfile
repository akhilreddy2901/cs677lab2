FROM python:3.8-alpine

RUN pip install redis

WORKDIR /app

COPY catalog.py .
COPY locks.py .

EXPOSE 8081

ENTRYPOINT ["python3", "catalog.py"]