# Use Python 3.10 with Uvicorn + Gunicorn for FastAPI
FROM tiangolo/uvicorn-gunicorn:python3.10

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt update && \
    apt install -y --no-install-recommends htop libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ./api/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy FastAPI and Streamlit app files
COPY ./api /app/api
COPY ./models /app/models
COPY ./streamlit /app/streamlit

# Expose ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit using a script
COPY /scripts/start_services.sh /app/start_services.sh
RUN chmod +x /app/start_services.sh

# Run FastAPI and Streamlit together
CMD ["/bin/bash", "/app/start_services.sh"]
