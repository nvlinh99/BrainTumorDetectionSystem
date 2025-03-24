import tensorflow as tf
import numpy as np

# Path to your weights file
# weights_path = "xception_model.weights.h5"
weights_path = "cnn_model.h5"

# Rebuild the model architecture
def rebuild_model():
    base_model = tf.keras.applications.EfficientNetB1(weights=None, include_top=False, input_shape=(240, 240, 3))
    x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    x = tf.keras.layers.Dropout(0.5)(x)
    output = tf.keras.layers.Dense(4, activation='softmax')(x)
    model = tf.keras.models.Model(inputs=base_model.input, outputs=output)
    return model

# Rebuild model and load weights
try:
    model = rebuild_model()
    model.load_weights(weights_path)
    print("✅ Weights loaded successfully!")

    # Test prediction on random image
    dummy_input = np.random.rand(1, 240, 240, 3).astype(np.float32)
    prediction = model.predict(dummy_input)
    print("🔍 Model prediction on dummy input:", prediction)

except Exception as e:
    print("❌ Error loading weights:", e)