# Description: Dockerfile for the selenium crawler

# Use the official debian slim image
FROM python:3.10.14-slim-bullseye as base

# build stage
FROM base as builder

# Define Chrome and ChromeDriver versions
ENV CHROME_VERSION=114.0.5735.90
ENV CHROMEDRIVER_VERSION=114.0.5735.90

# Install all packages for Chrome and ChromeDriver
RUN apt-get update && \
    apt-get install -y xvfb gnupg wget curl unzip --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update -y

# Download and install the specified version of Chrome
RUN wget -q https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb
RUN apt-get install -y ./google-chrome-stable_${CHROME_VERSION}-1_amd64.deb

# Download and install the specified version of ChromeDriver
RUN wget -q --continue -P /chromedriver "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
RUN unzip /chromedriver/chromedriver* -d /chromedriver

# Make the chromedriver executable and move it to the default selenium path
RUN chmod +x /chromedriver/chromedriver
RUN mv /chromedriver/chromedriver /usr/bin/chromedriver

# Copy any python requirements file into the install directory and install all python requirements
COPY requirements.txt /requirements.txt
RUN pip install --upgrade --no-cache-dir -r /requirements.txt
RUN rm /requirements.txt # Remove requirements file from container

# Base stage
FROM builder

# Copy the source code
COPY . /app

WORKDIR /app

CMD google-chrome --version && chromedriver --version && python main.py
