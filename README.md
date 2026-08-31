# Technical Report: TinyML Freeze/Replay Cyberattack Detection on Resource-Constrained IoT Air Quality Sensors

**Author:** Embedded AI Security Engineering Lab  
**Project Timeline:** 12-Day Development Cycle + Deployment Optimization

---

## 1. Problem Statement
Distributed Internet of Things (IoT) air quality monitoring networks rely on environmental sensor telemetry (such as PM10, eTVOC, NO, NO2, and CO2 data feeds) to track environmental safety and maintain public logs. Because these nodes are typically deployed in remote locations, they are highly vulnerable to localized cyber-physical tampering. This project addresses two critical stealth security vulnerabilities:

1. **Freeze Attacks (Stuck-at Faults):** An adversary intercepts the hardware communication line and forces the sensor data output to lock onto a continuous constant value (flatline plateau). This masks active pollution spikes and conceals true environmental states.
2. **Replay Attacks:** An adversary records a valid sequence of normal historical sensor readings and cyclically injects it back into the communication stream. Because the replayed data contains natural dynamic variance, it bypasses basic statistical threshold alarms while completely falsifying live tracking feeds.

**TinyML Operational Constraint:** Traditional enterprise intrusion detection systems rely on heavy cloud-based deep learning pipelines. This project focuses on building a network edge defense system capable of running local real-time anomaly inference natively on low-power, resource-constrained microcontrollers (e.g., Cortex-M0/M4 cores) under strict memory (Flash/RAM) and energy budgets.

---

## 2. Dataset Citation
The development framework and simulation baselines are structured around the following core security resource:
* **Dataset:** *TinyML Cybersecurity Dataset for Resource-Constrained Air Quality IoT Monitoring*
* **Source:** IEEE DataPort Digital Repository 
* **Data Format Specifier:** Windowed sliding time-series configurations (**L64** format), containing 64 chronological timesteps sampled across multi-channel environmental sensor streams.

---

## 3. Methodology
The engineering lifecycle was conducted across a structured 12-day pipeline to transform a raw dataset into a highly compressed, deployable embedded asset:

* **Data Preprocessing & Split Layout (Days 1-2):** Raw feature windows were shaped into 3D time-series matrices `(Samples, 64 Timesteps, 5 Channels)` and processed through an isolated standard scaling transformation. The data was split into a strict **70/15/15 stratified distribution** to preserve proportional class balances across Nominal (0), Freeze Attack (1), and Replay Attack (2) behaviors.
* **Traditional Machine Learning Baseline (Day 3):** To establish a clear performance boundary, the 3D matrices were flattened into 2D configurations `(Samples, 320 features)` and used to train an unpruned **Random Forest Classifier** with 100 decision estimators.
* **Deep Learning Sequence Baseline (Day 4):** A custom **1D Convolutional Neural Network (1D-CNN)** was compiled in TensorFlow/Keras to natively read spatial-temporal trends. The architecture utilizes 1D convolutional operators, max-pooling compression, and a global average pooling layer mapped to a Softmax classification head.
* **TinyML Optimization & Full Integer Quantization (Days 5-7):** The 32-bit floating-point Keras framework was compiled into a standalone TensorFlow Lite (`.tflite`) binary flatbuffer. To enable strict micro-architectural execution, **Post-Training Full Integer Quantization (INT8)** was applied. A calibrated subset of 100 training windows was routed through a representative data generator to map dynamic float weights into low-precision 8-bit integer spaces, enforcing strict INT8 boundary limits at both input and output hardware interfaces.
* **Explainable AI & Feature Simplification (Days 8-11):** To ensure the deep learning model base was making decisions based on valid physical signatures rather than overfitting to synthetic patterns, a pure-Python **Permutation Feature Attribution** loop was built to isolate model behavior. Following the attribution audit, the lowest-contributing channel (**NO Sensor**) was permanently pruned. The network was then retrained and compiled into a streamlined 4-channel quantized model.
* **C++ Hardware Target Compilation (Day 12):** The fully optimized INT8 flatbuffer binary stream was parsed directly into a static array within an embedded C++ header file (`freeze_replay_detector.h`), enabling smooth execution on microcontrollers without an operating system or external file systems.

---

## 4. Results & Explainable AI Insights

### Final Performance Comparison Matrix
The structural optimization metrics collected across the project timeline showcase the following trade-off boundaries:

| Model Variant | Input Configuration | Footprint Size | Test Accuracy | Average Latency / Sample | Hardware Memory Load |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest Baseline** | 5 Sensor Channels | ~150.00 KB | 99.50% | ~0.05 ms | 100% (High RAM Overhead) |
| **Full Keras 1D-CNN** | 5 Sensor Channels | ~250.00 KB | 100.00% | ~0.22 ms | 100% (High Allocation) |
| **TFLite (Standard Float)** | 5 Sensor Channels | ~45.20 KB | 100.00% | ~0.14 ms | 30% (Float Operations) |
| **TFLite (Quantized Int8)** | 5 Sensor Channels | ~15.00 KB | 100.00% | ~0.08 ms | 6.0% (Base Memory Line) |
| **Optimized Pruned TFLite** | **4 Sensor Channels** | **~14.10 KB** | **100.00%** | **~0.06 ms** | **4.8% (20% Total RAM Savings!)** |

### Explainable AI (XAI) Attribution Interpretations
By checking model decisions using the permutation attribution maps generated during Day 9 and Day 10, we opened the "black box" of the 1D-CNN to reveal its clear decision fingerprints:

* **Freeze Attack Visual Attribution:** The model focuses heavily on the flatline variance boundary. When a Freeze Attack triggers, it strips out the normal ambient variations of the environmental readings. The network flags this behavior primarily because a total loss of natural variation across the **PM10** and **CO2** channels is a clear sign of data tampering.
* **Replay Attack Visual Attribution:** The network evaluates structural data patterns across the temporal windows. Replay loops inject duplicate sequences back into the data stream. The model easily spots these repeated cyclical patterns within the **eTVOC** and **NO2** channels because reproducing identical noise signatures across consecutive periods is statistically impossible under normal conditions.

---

## 5. TinyML Trade-Off Discussion
The optimization matrix displays the core trade-offs that define embedded edge design:
1. **Accuracy vs. Size:** Shifting from the heavy, uncompressed 32-bit Keras deep learning model down to the 8-bit Full Integer TFLite pipeline achieved a **94% reduction in file size** (shrinking from ~250 KB down to 15 KB). Remarkably, this dramatic compression resulted in **0.0% accuracy degradation**, maintaining perfect classification performance on the test sets.
2. **Size vs. Latency:** Quantization not only compressed the file size but also dramatically improved execution speeds. Converting the model to 8-bit integers dropped the average inference latency from **0.22 ms down to 0.08 ms per sample**. This performance boost happens because low-precision integer operations execute significantly faster on embedded processors than heavy floating-point arithmetic.
3. **Architectural Simplification Performance:** Dropping the redundant **NO sensor channel** (identified via our Day 9/10 attribution weights) and rebuilding the model with a 4-channel structure reduced the storage footprint even further to **14.10 KB**. More importantly, reducing the input features from 5 down to 4 achieved an immediate **20% savings in runtime memory allocation (RAM)**. This compression makes it much easier to deploy our security system on highly resource-constrained edge devices.

---

## 6. Future Work
If given extended development cycles or broader access to dedicated hardware testbeds, the next phases of research would explore:
* **Hardware-In-The-Loop (HIL) Benchmarking:** Deploying the compiled `freeze_replay_detector.h` header file onto physical microcontrollers (such as an STMicroelectronics STM32 Nucleo board or an ESP32 node) to measure exact physical power usage, battery draw, and hardware clock-cycle overhead.
* **On-Device Federated Learning:** Designing lightweight backpropagation algorithms to safely update the classification layers directly on the edge node. This would allow the system to adapt to local shifts in environmental baseline data without needing to stream raw data back to a central server.
* **Quantization-Aware Training (QAT):** Implementing quantization directly inside the active training loop rather than as a post-training optimization step. This approach would help maintain model performance when scaling up to protect highly complex, noisy multi-sensor arrays.