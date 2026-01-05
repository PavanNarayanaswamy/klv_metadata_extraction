# KLV Metadata Extraction and Decoding (ZenML Pipeline)

This repository demonstrates how to **extract and decode MISB-compliant KLV metadata** (ST 0601 / ST 0903) from MPEG-TS video streams using **FFmpeg**, **jMISB (via JPype in Python)**, and **ZenML pipelines with MLflow experiment tracking**.

All extraction and decoding steps are executed as **ZenML pipeline steps**, with both **raw KLV** and **decoded metadata** logged as **MLflow artifacts**.

---

## ✅ Supported Metadata Types

The pipeline supports:

- **Standalone VMTI (MISB ST 0903)**
- **Embedded VMTI (ST 0903 embedded inside ST 0601 UAS Datalink)**

---

## 📁 Project Structure

Ensure the repository is structured as follows:

```
klv_metadata_extraction/
├── main.py # ZenML pipeline entry point
├── decode.py # jMISB decoder logic
├── README.md
├── output/
│   ├── metadata.klv
│   ├── metadata_emb.klv
│   └── decoded_metadata.json
├── jars/
│   ├── jmisb-api-1.12.0.jar
│   ├── jmisb-core-common-1.12.0.jar
│   ├── slf4j-api-1.7.36.jar
│   └── slf4j-simple-1.7.36.jar
├── standalone.ts
└── embedded.ts
```

---

## 📦 Prerequisites

### System Requirements

- **Python**: 3.9+
- **Java Runtime Environment (JRE)**: 8 or above
- **FFmpeg**
- **ZenML**
- **mlflow**

### Python Dependencies

Install required Python packages:

```bash
pip install zenml jpype1 mlflow
```

### ⚙️ ZenML Initialization (First-Time Setup)

Initialize ZenML (only required once):

```bash
zenml init
```

### 📥 Required Files

#### 1️⃣ JAR Dependencies

Place the following JAR files inside the `jars/` directory:

- `jmisb-api-1.12.0.jar`
- `jmisb-core-common-1.12.0.jar`
- `slf4j-api-1.7.36.jar`
- `slf4j-simple-1.7.36.jar`

These JARs are required for decoding MISB ST 0601 and ST 0903 metadata using jMISB.

#### 2️⃣ Video Files

Place the following MPEG-TS video files in the project root directory:

- `standalone.ts` → Contains standalone ST 0903 VMTI
- `embedded.ts` → Contains ST 0903 VMTI embedded inside ST 0601

---

## ⚙️ ZenML Setup (Required)

### 1️⃣ Register MLflow Experiment Tracker

Register an MLflow experiment tracker with ZenML:

```bash
zenml experiment-tracker register mlflow_experiment_tracker --flavor=mlflow
```

(Optional) Update the MLflow tracking URI:

```bash
zenml experiment-tracker update mlflow_experiment_tracker \
  --tracking_uri="http://127.0.0.1:5000"
```

### 2️⃣ Create and Activate a Custom ZenML Stack

The default ZenML stack cannot be modified. Create a custom stack:

```bash
zenml stack register test \
  -o default \
  -a default \
  -e mlflow_experiment_tracker
```

Activate the stack:

```bash
zenml stack set test
```

Verify the active stack:

```bash
zenml stack describe
```

---

## ▶️ Run the ZenML Pipeline

Execute the pipeline using:

```bash
python main.py
```

### 🚀 What the Pipeline Does

Running the pipeline will:

1. Extract KLV metadata from `.ts` files using FFmpeg
2. Decode MISB ST 0601 / ST 0903 metadata using jMISB
3. Log raw `.klv` files and decoded `.json` metadata as MLflow artifacts
4. Track each pipeline step as a ZenML experiment

---

## 📊 Outputs

Generated outputs are stored in the `output/` directory and MLflow artifacts:

- `metadata.klv` – Extracted metadata from .ts videos
- `decoded_metadata.json` – Fully decoded metadata output

---

## 📌 Notes

- Ensure FFmpeg is available in your system PATH.
- Java must be installed and accessible for JPype to load jMISB.