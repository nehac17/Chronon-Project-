FROM ubuntu:20.04

# Install system packages: Java (for Scala), Scala, Python, and other tools.
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    scala \
    python3 \
    python3-pip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install pymongo

# Set working directory and copy the project files into the container.
WORKDIR /app
COPY . /app

# Run the dynamic pipeline script by default.
CMD ["python3", "dynamic_pipeline.py"]
