import streamlit as st
import requests
from PIL import Image

st.set_page_config(
    page_title="Brain Tumor Detection",
    page_icon=":brain:",
    initial_sidebar_state="auto"
)

#FASTAPI_URL = "http://34.69.54.132:8000"
FASTAPI_URL = "http://brain-tumor-detection:8000"

st.title("Brain Tumor Detection")

# Upload file
file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if file:
    image = Image.open(file)
    st.image(image, use_column_width=True)

    st.subheader("Brain Tumor Detection Results")
    with st.spinner("Processing..."):
        files = {"file": ("image.jpg", file.getvalue(), "image/jpeg")}
        response = requests.post(f"{FASTAPI_URL}/predict/brain-tumor", files=files)
    
    if response.status_code == 200:
        result = response.json()
        st.success(f"Prediction: {result['predicted_class']}")
        st.info(f"Confidence: {result['confidence']:.2f}%")
        if result["predicted_class"] == "No Tumor":
            st.balloons()
    else:
        st.error("Error processing the image!")