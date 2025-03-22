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
from tensorflow.keras.applications import EfficientNetB1
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from loguru import logger
from PIL import Image, ImageOps
import numpy as np
import io
import os

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
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "http://jaeger-query.tracing.svc.cluster.local:4317")

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
    return {'message': 'Welcome to our Brain Tumor Detection API!'}

@app.get('/health')
async def check_health():
    return {'status': 'Service healthy'}

CLASS_NAMES = ['Glioma Tumor', 'Meningioma Tumor', 'No Tumor', 'Pituitary Tumor']

# Load Model
def rebuild_model():
    base_model = EfficientNetB1(weights=None, include_top=False, input_shape=(240, 240, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    output = Dense(len(CLASS_NAMES), activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

def load_model(weights_path="/app/models/model.weights.h5"):
    model = rebuild_model()
    model.load_weights(weights_path, skip_mismatch=True)
    return model

model = load_model()

# Prediction function
def predict(image: Image.Image):
    size = (240, 240)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image) / 255.0
    img_reshape = img[np.newaxis, ...]

    prediction = model.predict(img_reshape)
    predicted_class = CLASS_NAMES[np.argmax(prediction)]
    confidence = float(np.max(prediction) * 100)  # 🔥 FIX: Convert float32 → float
    return predicted_class, confidence

# API Endpoint
@app.post("/predict/brain-tumor")
async def predict_image(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        predicted_class, confidence = predict(image)
        logger.info(f"Prediction: {predicted_class} ({confidence:.2f}%)")
        return JSONResponse({"predicted_class": predicted_class, "confidence": confidence})
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)