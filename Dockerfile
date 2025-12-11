# Use official Python image
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y build-essential && apt clean

# Copy requirements.txt first to install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose port 5000 for Flask app
EXPOSE 5000



# Start Flask app
CMD ["python", "app.py"]

