# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and switch to it
RUN useradd --create-home --shell /bin/bash botuser
USER botuser

# Make port 8443 available to the world outside this container
EXPOSE 8443

# Define environment variable
ENV BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ENV PORT=8443
ENV WEBHOOK_URL=YOUR_WEBHOOK_URL_HERE
ENV ADMIN_ID=YOUR_TELEGRAM_ID_HERE

# Run main.py when the container launches
CMD ["python", "main.py"]
