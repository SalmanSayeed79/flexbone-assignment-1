# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

# Copy local code to the container image.
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
# We explicitly install gunicorn and uvicorn to ensure they are available.
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn

# Run the web service on container startup. 
# Cloud Run sets the PORT environment variable (default 8080).
# We use gunicorn with uvicorn workers for production-grade performance.
ENV PORT=8080
CMD exec gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app

