FROM python:3.11.3-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY log_generator.py .
COPY api.py .

RUN apk add --no-cache netcat-openbsd

# Expose API port
EXPOSE 8000

# Run the API server when the container starts
CMD ["python", "-u", "api.py"]
