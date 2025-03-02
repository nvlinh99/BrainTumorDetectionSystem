from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPSpanExporterGRPC
from loguru import logger
from PIL import Image, ImageOps
import numpy as np
import io
import os
import time

from api.utils import rebuild_model, class_names 

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment variables
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "jaeger-jaeger.tracing.svc.cluster.local:4317")

def setting_jaeger(app: FastAPI, log_correlation: bool = True) -> None:
    try:
        tracer = TracerProvider(
            resource=Resource.create({SERVICE_NAME: "brain-tumor-detection"})
        )
        trace.set_tracer_provider(tracer)

        otlp_exporter = OTLPSpanExporterGRPC(
            endpoint=OTLP_GRPC_ENDPOINT,
            insecure=True
        )

        logger.info(f"Configuring OTLP exporter with endpoint: {OTLP_GRPC_ENDPOINT}")

        tracer.add_span_processor(BatchSpanProcessor(otlp_exporter))

        if log_correlation:
            LoggingInstrumentor().instrument(set_logging_format=True)
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
        logger.info("Jaeger instrumentation completed successfully")
    except Exception as e:
        logger.error(f"Failed to set up Jaeger instrumentation: {str(e)}")
        raise

setting_jaeger(app)

@app.get('/')
async def index():
    return {'message': 'Welcome to Brain Tumor Detection API!'}

@app.get('/health')
async def check_health():
    return {'status': 'healthy'}

# Load model weights
weights_path = '/app/api/models/model.weights.h5'
model = None  # Define model globally

if os.path.exists(weights_path):
    model = rebuild_model()  # Build model architecture
    model.load_weights(weights_path)  # Load weights
    logger.info("Model weights loaded successfully.")
else:
    logger.error("Model weights file not found!")
    raise RuntimeError("Model weights file is missing. Please upload the correct model file.")

@app.post("/predict/brain-tumor")
async def predict_brain_tumor(file: UploadFile = File(...)):
    global model  # Ensure model is recognized globally

    if model is None:
        logger.error("Model is not loaded!")
        return JSONResponse(content={"error": "Model is not loaded. Please check the server logs."}, status_code=500)

    start_time = time.time()
    
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        image = ImageOps.fit(image, (240, 240), Image.Resampling.LANCZOS)
        img_array = np.asarray(image) / 255.0
        img_array = img_array[np.newaxis, ...]

        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        confidence = float(np.max(prediction)) * 100

        processing_time = time.time() - start_time
        logger.info(f"Processing Time: {processing_time:.2f} seconds")

        return JSONResponse(content={
            "predicted_class": predicted_class,
            "confidence": confidence
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
