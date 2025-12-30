# KLV Metadata Extraction and Decoding

This repository demonstrates how to **extract and decode MISB-compliant KLV metadata** (ST 0601 / ST 0903) from MPEG-TS video streams using **FFmpeg** and **jMISB (via JPype in Python)**.

The pipeline supports both:

* **Standalone VMTI (ST 0903)**
* **Embedded VMTI inside ST 0601 UAS Datalink**

---

## 📁 Project Structure

Ensure the repository is structured as follows:

```
klv_metadata_extraction/
├── decode.py
├── README.md
├── output/
│   ├── metadata.klv
│   └── metadata_emb.klv
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

* **Python 3.9+**
* **Java Runtime Environment (JRE 8 or above)**
* **FFmpeg**
* Python packages:

  ```bash
  pip install jpype1
  ```

---

## 📥 Required Files

### 1️⃣ JAR Dependencies

Place the following JAR files under the `jars/` directory:

* `jmisb-api-1.12.0.jar`
* `jmisb-core-common-1.12.0.jar`
* `slf4j-api-1.7.36.jar`
* `slf4j-simple-1.7.36.jar`

These are required for decoding MISB ST 0601 and ST 0903 metadata using **jMISB**.

---

### 2️⃣ Video Files

Place the following MPEG-TS video files in the project root:

* `standalone.ts` → contains **standalone ST 0903 VMTI**
* `embedded.ts` → contains **ST 0903 VMTI embedded inside ST 0601**

---

## 🎥 Step 1: Extract KLV Metadata using FFmpeg

Create an output directory:

```bash
mkdir -p output
```

### 🔹 Extract metadata from `embedded.ts`

```bash
ffmpeg -i embedded.ts -map 0:d -c copy -f data output/metadata_emb.klv
```

This extracts **embedded VMTI (ST 0903) within ST 0601**.

---

### 🔹 Extract metadata from `standalone.ts`

```bash
ffmpeg -i standalone.ts -map 0:1 -c copy -f data output/standalone_metadata.klv
```

This extracts **standalone ST 0903 VMTI**.

---

## 🧠 Step 2: Decode KLV Metadata

Run the decoder script:

```bash
python decode.py
```

### Output

* Decoded metadata is written as **structured JSON**
* Includes:

  * ST 0601 fields
  * ST 0903 VMTI fields
  * VTargetSeries
  * AlgorithmSeries
  * OntologySeries
* Suitable for:

  * Analytics pipelines
  * ISR fusion workflows
  * LLM-based video understanding

---

## 📊 Supported Standards

* **MISB ST 0601 – UAS Datalink**
* **MISB ST 0903 – Video Moving Target Indicator (VMTI)**
* **STANAG 4609 (Transport Stream)**

---

## 🧩 Notes

* Raw `.ts` and `.klv` files are large and should be handled via **Git LFS** or external storage.
* This repository focuses on **decoding and structuring metadata**, not video playback.

---
