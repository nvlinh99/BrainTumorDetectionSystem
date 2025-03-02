import streamlit as st
import requests
from PIL import Image

FASTAPI_URL = "http://34.69.54.132:8000"

st.set_page_config(
    page_title="Brain Tumor Detection",
    page_icon=":brain:",
    initial_sidebar_state="auto"
)

st.title("Brain Tumor Detection")

# Upload file
file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Use session state to avoid repeated API calls
if "prediction" not in st.session_state:
    st.session_state["prediction"] = None
    st.session_state["confidence"] = None

if file and st.button("Detect Tumor"):
    image = Image.open(file)
    st.image(image, use_column_width=True)

    st.subheader("Brain Tumor Detection Results")
    with st.spinner("Processing..."):
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{FASTAPI_URL}/predict/brain-tumor", files=files)

    if response.status_code == 200:
        result = response.json()
        st.session_state["prediction"] = result["predicted_class"]
        st.session_state["confidence"] = result["confidence"]
    else:
        st.error("Error processing the image!")

# Show result only when prediction exists
if st.session_state["prediction"]:
    st.success(f"Prediction: {st.session_state['prediction']}")
    st.info(f"Confidence: {st.session_state['confidence']:.2f}%")
    if st.session_state["prediction"] == "No Tumor":
        st.balloons()