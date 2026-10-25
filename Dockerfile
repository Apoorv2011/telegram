
FROM python:3.10-slim

WORKDIR /app

# Copy files into the container
COPY requirements.txt .
COPY app.py .

# Install your dependencies inside the container image
RUN pip install --no-cache-dir -r requirements.txt

# Run your application
CMD ["python", "app.py"]
