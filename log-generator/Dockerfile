FROM python:3.11.3-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script
COPY generate_logs.py .

RUN apk add --no-cache netcat-openbsd

# Run the script when the container starts
CMD ["python", "-u", "generate_logs.py"]
