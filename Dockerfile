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

# Use the official FastAPI image based on Uvicorn and Gunicorn
FROM tiangolo/uvicorn-gunicorn:python3.10

# Set the working directory inside the container
WORKDIR /app

# Ensure the Python path includes /app
ENV PYTHONPATH="/app"

# Install system dependencies
RUN apt update && \
    apt install -y htop libgl1-mesa-glx libglib2.0-0 && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY api/ /app/api/
# COPY models/ /app/api/models/

# Copy requirements file and install dependencies
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose FastAPI's default port
EXPOSE 8000

# Run FastAPI application correctly
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]