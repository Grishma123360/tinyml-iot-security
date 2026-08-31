import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import tensorflow as tf

# Set page configurations
st.set_page_config(page_title="TinyML IoT Security Dashboard", layout="wide", page_icon="🛡️")

st.title("🛡️ TinyML Edge Security: Freeze/Replay Attack Dashboard")
st.markdown("---")

# 1. Establish project directory paths safely
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data", "synthetic_L64.csv")
keras_model_path = os.path.join(base_dir, "models", "tinyml_freeze_replay_model.keras")

# Load your baseline dataset for live generation loops
@st.cache_data
def load_base_data():
    return pd.read_csv(data_path)

df = load_base_data()
X_raw = df.drop(columns=['label']).values
y_raw = df['label'].values
X_reshaped = X_raw.reshape(-1, 64, 5)

# Load the trained 1D-CNN Model
@st.cache_resource
def load_security_model():
    return tf.keras.models.load_model(keras_model_path)

model = load_security_model()

# 2. Sidebar Controls
st.sidebar.header("🕹️ Telemetry Controls")
st.sidebar.write("Simulate incoming sensor windows from the air quality IoT node.")

# Allow user to pick what scenario to inject into the live system
scenario = st.sidebar.selectbox(
    "Choose Network Traffic Mode:",
    ["Nominal (Normal Data)", "Inject Freeze Attack", "Inject Replay Attack"]
)

run_simulation = st.sidebar.button("⚡ Start Live Stream Monitoring")

# Map tracking criteria
channel_names = ["PM10", "eTVOC", "NO", "NO2", "CO2"]
classes = ["Normal Operation", "🔴 FREEZE ATTACK DETECTED", "⚠️ REPLAY ATTACK DETECTED"]

# 3. Main Dashboard UI Layout Layout Split
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Live Sensor Telemetry Stream")
    chart_placeholder = st.empty()

with col2:
    st.subheader("🤖 Edge AI Status Room")
    status_box = st.empty()
    metrics_box = st.empty()
    st.markdown("### 🔍 Model Feature Importance Weights")
    # Dynamic display of your day 11 feature selection configurations
    st.info("**PM10 & CO2**: Key indicators for Freeze signatures.\n\n**eTVOC & NO2**: Prioritized for tracking Replay loops.")

# 4. Simulation Stream Loop execution
if run_simulation:
    # Filter sample vectors based on user's scenario choice
    if scenario == "Nominal (Normal Data)":
        target_indices = np.where(y_raw == 0)[0]
    elif scenario == "Inject Freeze Attack":
        target_indices = np.where(y_raw == 1)[0]
    else:
        target_indices = np.where(y_raw == 2)[0]
        
    # Pick a random window from that classification segment
    random_idx = np.random.choice(target_indices)
    sample_window = X_reshaped[random_idx]
    
    # Animate the timeline stream step-by-step to look like a live system
    for step in range(10, 65):
        # Create rolling window frame view
        current_frame = sample_window[:step]
        chart_df = pd.DataFrame(current_frame, columns=channel_names)
        
        # Update the live chart view
        chart_placeholder.line_chart(chart_df)
        
        # Prepare the single window payload for immediate classification check
        # We take a fixed 64-step view (padding early steps with zeros if needed)
        input_payload = np.zeros((1, 64, 5))
        input_payload[0, :step] = sample_window[:step]
        
        # Run inference using your trained neural network weights
        start_time = time.time()
        preds_proba = model(input_payload, training=False).numpy()
        latency = (time.time() - start_time) * 1000
        predicted_class = np.argmax(preds_proba[0])
        confidence = preds_proba[0][predicted_class] * 100
        
        # Update the status box and alerts in real-time
        if predicted_class == 0:
            status_box.success(f"STATUS: {classes[predicted_class]}")
        elif predicted_class == 1:
            status_box.error(f"ALERT: {classes[predicted_class]}")
        else:
            status_box.warning(f"ALERT: {classes[predicted_class]}")
            
        metrics_box.markdown(f"""
        * **Inference Speed:** {latency:.2f} ms
        * **Model Confidence:** {confidence:.1f}%
        * **Active Sensor Channels:** 5 Channels
        """)
        
        time.sleep(0.08) # Simulates data transmission delay
else:
    status_box.info("System Standby. Click 'Start Live Stream Monitoring' in the sidebar to begin.")
