#!/bin/bash

# Start FastAPI in the background
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit in the background
streamlit run api/streamlit/app.py --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.enableCORS false \
  --server.enableXsrfProtection false &

# Wait for all background jobs (keep the container running)
wait