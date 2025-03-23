import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB1
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
import numpy as np
from PIL import Image, ImageOps
import os
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Brain Tumor Detection",
    page_icon=":brain:",
    initial_sidebar_state="auto"
)

# Hide Streamlit menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Class names
class_names = ['Glioma Tumor', 'Meningioma Tumor', 'No Tumor', 'Pituitary Tumor']

# Rebuild model architecture
def rebuild_model():
    base_model = EfficientNetB1(weights=None, include_top=False, input_shape=(240, 240, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    output = Dense(4, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

# Load model from cache
@st.cache_data
def load_model_cached():
    weights_path = "model.weights.h5"
    if not os.path.exists(weights_path):
        st.error(f"❌ Model weights not found at: {weights_path}")
        return None
    try:
        model = rebuild_model()
        model.load_weights(weights_path)  # Removed skip_mismatch
        return model
    except Exception as e:
        st.error(f"❌ Failed to load model weights: {e}")
        return None

# Prediction function
def import_and_predict(image_data, model):
    size = (240, 240)
    image = image_data.convert("RGB")
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image) / 255.0
    img_reshape = img[np.newaxis, ...]
    
    st.write("🔍 Debug: Input shape", img_reshape.shape)
    st.write("🔍 Debug: Sample pixels", img_reshape[0, :3, :3, 0])  # Check pixel values
    
    prediction = model.predict(img_reshape)
    st.write("🔍 Debug: Raw prediction output", prediction)  # Raw probabilities
    return prediction

# Load model
model = load_model_cached()
if model is None:
    st.stop()

# Sidebar
with st.sidebar:
    st.title("🧠 Brain Tumor Detection")
    st.subheader("Detect brain tumor types from MRI scans.")

# Main content
st.write("""
    # 🧠 Brain Tumor Detection with MRI
    Upload an MRI scan below to classify tumor type (if any).
""")

file = st.file_uploader("Upload an MRI image", type=["jpg", "jpeg", "png"], label_visibility='collapsed')

if file is None:
    st.info("📁 Please upload an image to begin.")
else:
    image = Image.open(file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    predictions = import_and_predict(image, model)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = np.max(predictions) * 100

    st.sidebar.info(f"🧪 Prediction: {predicted_class}")
    st.sidebar.success(f"📊 Confidence: {confidence:.2f}%")

    if predicted_class == 'No Tumor':
        st.balloons()
        st.markdown("### ✅ Great news! No tumor detected.")
    else:
        st.markdown(f"### ⚠️ Detected Tumor Type: **{predicted_class}**")
        st.warning("Please consult a medical professional for further diagnosis.")
