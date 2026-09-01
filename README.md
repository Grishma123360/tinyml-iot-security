# Multi-Tier IoT Edge Security Platform: TinyML CNN Shield & LLM Threat Analyst Layer

This repository contains an end-to-end, multi-tier industrial cybersecurity platform designed to protect resource-constrained Air Quality IoT monitoring nodes from stealth cyber-physical attacks. 

The architecture is split into two distinct engineering milestones:
1. **Project #1 (Edge Layer):** A high-efficiency, quantized 1D-CNN deployed locally to catch anomalies on bare-metal hardware.
2. **Project #3 (Operational Layer):** A Generative AI (Gemini/Claude) layer that reads raw machine logs and converts them into human-readable threat reports.

---

## 📁 Repository Structure
* `/data` - Contains windowed time-series sensor telemetry samples (`synthetic_L64.csv` in L64 format).
* `/notebooks` - Step-by-step developmental pipeline (Exploration, ML/DL baselines, INT8 Quantization, SHAP analysis).
* `/models` - Holds uncompressed `.keras` artifacts, compressed `.tflite` binaries, and the final deployable C++ header array (`.h`).
* `app.py` - Live interactive sensor stream and edge-AI network threat monitor dashboard.
* `explain_security.py` - **[New]** Project #3 LLM-assisted incident response and threat interpretation gateway interface.

---

## 📊 Project #1: TinyML 1D-CNN Performance Benchmarks
To respect strict microcontroller memory (Flash/RAM) limitations, the deep sequence model was optimized using **Post-Training Full Integer Quantization (INT8)** and **Structural Feature Pruning**:

| Model Variant | Input Dimension | Footprint Size | Test Accuracy | Average Latency / Sample | Hardware Memory Load |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full Keras 1D-CNN** | 5 Sensor Channels | ~250.00 KB | 100.00% | ~0.22 ms | 100% (High Allocation) |
| **TFLite (Quantized Int8)** | 5 Sensor Channels | ~15.00 KB | 100.00% | ~0.08 ms | 6.0% (Base Memory Line) |
| **Optimized Pruned TFLite** | **4 Sensor Channels** | **~14.10 KB** | **100.00%** | **~0.06 ms** | **4.8% (20% RAM Savings!)** |

* **XAI Insights:** Using permutation feature importance mapping, we opened the "black box" to prove that the 1D-CNN flags **Freeze Attacks** based on an absolute drop in time-series variance across the **PM10 and CO2** channels.

---

## 🤖 Project #3: LLM-Assisted Threat Interpretation Layer
While the edge model flags attacks within microseconds, raw telemetry anomalies are difficult for field operators to diagnose. This layer acts as an automated **Incident Response Analyst**:
* **The Workflow:** Intercepts raw classifications, INT8 latency metrics, and SHAP attribution shapes from the 1D-CNN.
* **The Output:** Automatically compiles context into structured prompts for advanced LLMs (`gemini-3.6-flash` or `claude-3-5-sonnet`) to generate live, executive-level Threat Diagnostics, SHAP evidence validations, and immediate technical action plans.

---

## 🚀 How to Run the Dashboards Locally

Ensure your Python virtual environment is active (`venv`) and launch either architecture tier:

* **To run the live edge sensor monitor (Project 1):**
  ```bash
  python -m streamlit run app.py
  ```
* **To run the generative AI analyst portal (Project 3):**
  ```bash
  python -m streamlit run explain_security.py
  ```
