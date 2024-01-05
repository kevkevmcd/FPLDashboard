# Use an official Python runtime as a parent image
FROM python:3-alpine3.11

# Set the working directory to /app
WORKDIR /app

# Copy the contents of the current directory into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN apk --no-cache add \
    g++ \
    gcc \
    libxslt-dev \
    libxml2-dev \
    libc-dev \
    libffi-dev \
    openssl-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run app.py when the container launches
CMD ["python", "app/app.py"]