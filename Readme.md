# Automated Traffic Violation Detection and Identification System

## Overview

This project is a Computer Vision based Traffic Violation Detection System developed as a hackathon prototype. The system automatically analyzes traffic images, detects vehicles, identifies traffic rule violations, extracts vehicle license plate numbers, and generates evidence for further action.

The objective is to reduce manual monitoring efforts and provide an automated workflow for identifying traffic violations using deep learning and OCR technologies.

---

## Features

### Vehicle Detection and Classification

Detects and classifies vehicles into:

* Car
* Motorcycle
* Bus
* Truck

### Helmet Violation Detection

Identifies motorcyclists riding without helmets.

### Triple Riding Detection

Detects motorcycles carrying three or more riders.

### License Plate Detection

Detects vehicle number plates from traffic images.

### Automatic Number Plate Recognition (ANPR)

Uses OCR to extract the vehicle registration number from detected license plates.

### Evidence Generation

Generates annotated evidence images highlighting detected violations.

### Violation Logging

Stores detected violations and extracted details in a CSV file.

### Dashboard Visualization

Provides a simple Flask dashboard for viewing violation records and evidence images.

---

# System Architecture

```text
Traffic Image
      ↓
Vehicle Detection + Classification
      ↓
Vehicle Crop
      ↓
Motorcycle?
      ↓
Helmet Detection
      ↓
Triple Riding Detection
      ↓
License Plate Detection
      ↓
Plate Crop
      ↓
EasyOCR
      ↓
Violation Engine
      ↓
Evidence Generation
      ↓
CSV Database
      ↓
Flask Dashboard
```

---

# Technology Stack

## Deep Learning

* YOLOv8
* Ultralytics

## Computer Vision

* OpenCV

## OCR

* EasyOCR

## Data Processing

* Pandas
* NumPy

## Dashboard

* Flask

## Development Environment

* Python 3.10
* Jupyter Notebook
* JupyterLab

---

# Repository Structure

```text
traffic-violation-system/
│
├── models/
│   ├── vehicle_weights.pt
│   ├── helmet_weights.pt
│   ├── triple_weights.pt
│   └── license_weights.pt
│
│
├── notebooks/
│   ├── vehicle_training.ipynb
│   ├── helmet_training.ipynb
│   ├── triple_training.ipynb
│   ├── plate_training.ipynb
│
├── results/
│   ├── helmet_result/
│   ├── license_plate_result/
│   ├── triple_result/
│   ├── vehicle_result/
│ 
├── outputs/
│   ├── evidence/
│   └── violations.csv
│
├── dashboard/
│   ├── templates/
│   ├── static/
│   └── app.py
│
├── main.ipynb
├── requirements.txt
└── README.md
```

---

# Model Descriptions

## vehicle_weights.pt

Purpose:

* Vehicle detection
* Vehicle classification

Classes:

* Car
* Motorcycle
* Bus
* Truck

---

## helmet_weights.pt

Purpose:

* Helmet violation detection

Classes:

* With Helmet
* Without Helmet

---

## triple_weights.pt

Purpose:

* Rider count detection

Classes:

* Single Rider
* Double Rider
* Triple Rider

---

## license_plate_weights.pt

Purpose:

* License plate detection

Classes:

* License Plate

---

# Notebook Descriptions

## vehicle_training.ipynb

Used to:

* Prepare vehicle dataset
* Train vehicle detection model
* Evaluate model performance

---

## helmet_training.ipynb

Used to:

* Train helmet detection model
* Evaluate helmet detection accuracy

---

## triple_training.ipynb

Used to:

* Train triple riding detection model
* Evaluate rider classification accuracy

---

## plate_training.ipynb

Used to:

* Train license plate detector
* Evaluate plate localization performance

---

## main.ipynb

Complete end-to-end pipeline.

Responsibilities:

* Load all trained models
* Detect vehicles
* Detect helmet violations
* Detect triple riding violations
* Detect license plates
* Extract plate numbers using EasyOCR
* Generate evidence images
* Save violation details to CSV
* Provide output for dashboard visualization

---

# Installation

## Create Environment

```bash
conda create -n traffic python=3.10 -y
conda activate traffic
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Launch JupyterLab

```bash
jupyter lab
```

Open:

```text
main.ipynb
```

Run all cells.

---

## Launch Dashboard

```bash
python dashboard/app.py
```

Open:

```text
http://127.0.0.1:5000
```

in a browser.

---

# Output

## Evidence Images

Violation evidence images are saved in:

```text
outputs/evidence/
```

Examples:

```text
bike_helmet.jpg
bike_triple.jpg
bike_helmet_triple.jpg
```

---

## Violation Records

All detected violations are stored in:

```text
outputs/violations.csv
```

Columns:

| Column           | Description                   |
| ---------------- | ----------------------------- |
| timestamp        | Detection timestamp           |
| image_name       | Input image name              |
| vehicle_type     | Detected vehicle              |
| plate_number     | Extracted registration number |
| helmet_violation | Helmet violation status       |
| triple_violation | Triple riding status          |
| evidence_image    | Path to evidence image        |

---

# Sample Workflow

1. Input traffic image.
2. Detect vehicles.
3. Check if detected vehicle is a motorcycle.
4. Detect helmet violations.
5. Detect triple riding violations.
6. Detect license plate.
7. Extract plate number using OCR.
8. Generate evidence image.
9. Save violation record.
10. Display results on dashboard.

---

# Future Improvements

* Real-time video processing
* Extend the system capability across all vehicle categories, including cars, buses, trucks, and commercial vehicles.
* CCTV camera integration
* Traffic signal integration
* Database support (MySQL/PostgreSQL)
* Automated challan generation
* Cloud deployment
* Multi-camera monitoring
* Violation analytics dashboard
* Grievance and appeal portal availability

---

# Hackathon Prototype Scope

This project demonstrates a complete proof-of-concept system for automated traffic violation identification using Computer Vision and OCR technologies. The prototype focuses on helmet violation detection, triple riding detection, license plate recognition, evidence generation, and violation management through a lightweight dashboard.

The system is designed to showcase the feasibility of automated traffic monitoring and enforcement using modern AI techniques.
