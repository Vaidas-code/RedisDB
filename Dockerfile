# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy everything from the current directory into /app in the container
COPY . /app

# Install the necessary Python packages
RUN pip install flask redis

# Expose port 5000 (same port Flask runs on)
EXPOSE 5000

CMD ["python", "webservizas.py"]
