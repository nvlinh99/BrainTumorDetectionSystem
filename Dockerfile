# FROM tiangolo/uvicorn-gunicorn:python3.10

# # Install system dependencies
# RUN apt update && \
#     apt install -y htop libgl1-mesa-glx libglib2.0-0 && \
#     apt clean && \
#     rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt 

# WORKDIR /app

# # Copy application code and models
# COPY api/ /app/api
# COPY models/ /app/models/

# EXPOSE 8000

# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM tiangolo/uvicorn-gunicorn:python3.10

# Set the working directory
WORKDIR /app

# Set environment variables to reduce space usage
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt update && \
    apt install -y --no-install-recommends htop libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first for caching
COPY api/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code
COPY api/ /app/
COPY models/ /app/models/

# Expose FastAPI's default port
EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
