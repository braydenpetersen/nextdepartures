# Image: python:3.11-slim
FROM python:3.11-slim

# Set the working directory to current directory
WORKDIR /app

COPY . .

COPY requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "server.py"]