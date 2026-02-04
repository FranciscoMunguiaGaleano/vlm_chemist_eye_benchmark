# VLM Chemist Eye Benchmark

This repository contains the benchmarking framework used to evaluate **Vision-Language Models (VLMs)** within the Chemist Eye safety architecture.

The experiments assess the zero-shot capabilities of modern VLMs for laboratory safety tasks without requiring model training or fine-tuning.

Specifically, the benchmark evaluates performance in:

* Personal Protective Equipment (PPE) compliance detection
* Worker accident detection via posture recognition

Performance is measured using:

* **Accuracy**
* **Hallucination rate** (failure to follow prompt instructions)
* **Response time**

---

## Repository Structure

```
vlm_chemist_eye_benchmark/
│
├── Experiment_1/
│   ├── q1.py ... q6.py
│   └── STANDING_NOT_CLASSIFIED/
│
├── Experiment_2/
│   ├── q7.py ... q10.py
│   └── PPE_NOT_CLASSIFIED/
```

Each script corresponds to a specific query strategy described in the Chemist Eye paper.

---

## Supported Models

The benchmark was designed for locally hosted models via **Ollama**, including:

* `llava:7b`
* `llava-phi3:latest`

Other multimodal models compatible with Ollama may also be used.

---

## Installation

### 1. Install Ollama

[https://ollama.com/](https://ollama.com/)

Pull the required models:

```bash
ollama pull llava:7b
ollama pull llava-phi3
```

### 2. Install Python dependencies

```bash
pip install pillow ollama
```

---

## Datasets

The datasets used in these experiments are available on Zenodo:

**Experiment 1 — Accident / Posture Detection**
👉 [ZENODO LINK — TO BE ADDED]

**Experiment 2 — PPE Compliance Detection**
👉 [ZENODO LINK — TO BE ADDED]

After downloading, update the dataset paths inside the scripts if necessary.

---

## Experiment 1 — Worker Accident Detection

This experiment evaluates whether VLMs can distinguish between normal standing posture and potentially dangerous situations such as lying, kneeling, or crouching.

The dataset is organised into two classes:

```
0 → Standing / not classified as accident  
1 → Prone / simulated accident
```

### Queries

Examples include:

* **Q1:** *Is the person prone? ONLY reply with YES or NO.*
* **Q2:** *Is the person standing? ONLY reply with YES or NO.*
* **Q3:** *What is the person doing?* (keyword-based interpretation)
* **Q4:** Sequential prompting with fallback logic

Some scripts combine multiple prompts to inject additional context and improve reliability.

### Run an experiment

```bash
python q7.py llava:7b
```

If no model is provided, an interactive menu will appear.

---

## Experiment 2 — PPE Compliance Detection

This experiment measures the ability of VLMs to detect whether a laboratory worker is wearing a lab coat.

Dataset structure:

```
0 → Not wearing PPE  
1 → Wearing PPE
```

### Example Queries

* **Q1:** *Is the person wearing a lab coat? ONLY reply with YES or NO.*
* **Q2:** *Is the person wearing a WHITE lab coat?*
* **Q3:** *What is the person wearing?* (keyword-based decision)

Sequential prompting strategies are also evaluated to improve classification accuracy.

### Run an experiment

```bash
python q1.py llava-phi3:latest
```

---

## How It Works

Each script:

1. Loads images from the dataset.
2. Sends them to the selected VLM using Ollama.
3. Interprets responses using strict YES/NO rules or keyword matching.
4. Computes accuracy, hallucination rate, and average response time.

If the model returns ambiguous answers, the script retries the query to enforce deterministic behaviour.

---

## Hallucination Definition

A hallucination is recorded when the VLM fails to follow the required response format — for example, returning a full sentence when instructed to answer strictly **YES** or **NO**.

---

## Reproducibility Notes

* Experiments were designed for **zero-shot evaluation**.
* No model training or fine-tuning is required.
* Results may vary depending on hardware and model version.

Running models locally is recommended to ensure consistent latency measurements.

---

## Related Repositories

**Main Chemist Eye System**
[https://github.com/FranciscoMunguiaGaleano/chemist_eye](https://github.com/FranciscoMunguiaGaleano/chemist_eye)

**RGB-D Stations**
[https://github.com/FranciscoMunguiaGaleano/chemist_eye_rgbd](https://github.com/FranciscoMunguiaGaleano/chemist_eye_rgbd)

**Infrared Stations**
[https://github.com/FranciscoMunguiaGaleano/chemist_eye_ir](https://github.com/FranciscoMunguiaGaleano/chemist_eye_ir)

---

⚠️ This repository contains the evaluation framework used in the Chemist Eye paper.

