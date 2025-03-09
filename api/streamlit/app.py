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

# Ẩn menu và footer Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Danh sách các lớp
class_names = ['Glioma Tumor', 'Meningioma Tumor', 'No Tumor', 'Pituitary Tumor']

# Hàm khởi tạo lại kiến trúc mô hình
def rebuild_model():
    # Load EfficientNetB1 base model
    base_model = EfficientNetB1(weights=None, include_top=False, input_shape=(240, 240, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    output = Dense(4, activation='softmax')(x)  # 4 lớp đầu ra
    model = Model(inputs=base_model.input, outputs=output)
    return model

# Hàm load model (kiến trúc + trọng số)
@st.cache_data
def load_model_cached():
    weights_path = 'model/model.weights.h5'  # Đường dẫn tới file trọng số
    try:
        if not os.path.exists(weights_path):
            st.error(f"Model weights file not found: {weights_path}. Please ensure the file exists.")
            return None
        # Khởi tạo mô hình
        model = rebuild_model()
        # Load trọng số vào mô hình
        model.load_weights(weights_path,  by_name=True,  skip_mismatch=True)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Load model từ cache
model = load_model_cached()
if model is None:
    st.error("The model could not be loaded. Please check the file path or model architecture.")
    st.stop()

# Hàm dự đoán
def import_and_predict(image_data, model):
    size = (240, 240)
    image = image_data.convert("RGB")
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img = np.asarray(image)
    img = img / 255.0
    img_reshape = img[np.newaxis, ...]
    prediction = model.predict(img_reshape)  # Make prediction
    return prediction

# Sidebar giao diện
with st.sidebar:
    st.title("Brain Tumor Detection")
    st.subheader("Accurate detection of brain tumor types using MRI scans.")

# Nội dung chính
st.write("""
    # Brain Tumor Detection with MRI Scans
    Upload an MRI scan to detect if a tumor is present and its type.
""")

# Upload file ảnh
file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if file is None:
    st.text("Please upload an image file")
else:
    image = Image.open(file)  # Mở ảnh
    st.image(image, use_column_width=True)  # Hiển thị ảnh

    # Dự đoán từ ảnh
    predictions = import_and_predict(image, model)
    predicted_class = class_names[np.argmax(predictions)]  # Lấy lớp dự đoán
    confidence = np.max(predictions) * 100  # Xác suất cao nhất

    # Hiển thị kết quả
    st.sidebar.info(f"Prediction: {predicted_class}")
    st.sidebar.success(f"Confidence: {confidence:.2f}%")

    if predicted_class == 'No Tumor':
        st.balloons()
        st.markdown("### Great news! No tumor detected.")
    else:
        st.markdown(f"### Detected Tumor Type: {predicted_class}")
        st.warning("Please consult with a medical professional for further evaluation.")
