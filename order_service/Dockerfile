FROM python:3.8-alpine

RUN pip install redis

WORKDIR /app

COPY order.py .

EXPOSE 8082

ENTRYPOINT ["python3", "order.py"]