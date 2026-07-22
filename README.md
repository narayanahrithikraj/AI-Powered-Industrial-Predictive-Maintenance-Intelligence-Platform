# 🏭 AI-Powered Industrial Predictive Maintenance Intelligence Platform

An enterprise-grade, multi-tenant Predictive Maintenance (PdM) platform designed to monitor industrial asset telemetry, run real-time machine learning inference for failure risk and Remaining Useful Life (RUL) estimation, and provide explainable AI insights (XAI) using SHAP.

Built with **FastAPI**, **Streamlit**, **PostgreSQL**, **XGBoost**, **LightGBM**, and fully containerized with **Docker Compose**.

---

## 🛠️ Tech Stack & Architecture

- **Frontend UI:** Streamlit (Responsive, Compact, Role-Gated UI)
- **Backend API:** FastAPI (Async REST APIs, JWT Auth, Role-Based Access Control)
- **Database:** PostgreSQL (Relational schema for assets, maintenance, alerts, & users)
- **Machine Learning & XAI:** XGBoost Classifier (Failure Risk), LightGBM Regressor (RUL), Isolation Forest (Anomaly Detection), SHAP (Root Cause Analysis)
- **Containerization:** Docker & Docker Compose

┌─────────────────────────────────────────────────────────┐
│ Streamlit Frontend │
│ (Port 8501 - Dockerized) │
└──────────────────────────┬──────────────────────────────┘
│ REST APIs
┌──────────────────────────▼──────────────────────────────┐
│ FastAPI Backend │
│ (Port 8000 - Dockerized) │
└──────┬───────────────────┬───────────────────┬──────────┘
│ SQL │ ML Ingestion │ XAI
┌──────▼───────────┐ ┌─────▼───────────┐ ┌─────▼───────────┐
│ PostgreSQL │ │ XGBoost / Light │ │ SHAP Feature │
│ DB (Port 5433) │ │ GBM Engine │ │ Explainability│
└──────────────────┘ └─────────────────┘ └───────────────┘

---

## ✨ Key Features

### 👑 Administrator Portal (15 Functional Modules)

- **Global Fleet Overview:** Multi-metric KPIs (Asset health ratio, active alerts, total predictions, avg RUL).
- **Asset CRUD Management:** Register, edit, and deactivate industrial plant equipment.
- **Sensor Data Ingestion & Validation:** Upload raw telemetry CSVs, validate data quality, check out-of-range sensor drift, and ingest into PostgreSQL.
- **AI Batch Failure Prediction:** Execute XGBoost inference on all fleet assets to compute risk probability distributions.
- **RUL Regression Analysis:** LightGBM-powered continuous RUL estimation and forecasting.
- **Unsupervised Anomaly Detection:** Scan sensor streams with Isolation Forest models to flag outliers.
- **Explainable AI (SHAP):** Root cause importance spectrum revealing primary failure drivers (vibration, temperature, pressure).
- **Enterprise Maintenance Center:** Dispatch work orders, assign technicians, and track downtime estimates.
- **Alert Center & Rule Engine:** Live notification feed with resolution controls and automated threshold triggers.
- **User Management & Token Generator:** Control access levels, manage accounts, and generate single-use joining tokens for new employee onboarding.
- **MLOps Model Registry:** Track deployed model versions, execute dynamic retraining pipelines, and run rollbacks.

### 👷 Operator / Engineer Portal (10 Functional Modules)

- **Assigned Asset Portal:** View telemetry manifest and health scores filtered strictly for your station.
- **Live Sensor Inspector:** Stream real-time vibration, temperature, joint torque, and coolant pressure readings.
- **Subsystem Component Diagnostics:** Multi-bar integrity breakdown (Bearings, Thermal Load, Hydraulic Seals).
- **Single-Machine Failure Predictor:** Interactive gauge meter and XGBoost risk classification.
- **Maintenance Dispatch Request:** Submit maintenance work requests directly to Admin work order queues.
- **Notification Inbox:** Operator alert feed with read/unread status toggles.
- **Multi-Format Data Export:** Generate and download machine audit CSV and TXT logs.

---

## 🔐 Access Token Employee Onboarding Flow

1. **Token Generation (Admin):** Admins generate secure joining tokens (e.g., `EMP-2026-JOIN` or `ENT-99A2-X801`) inside the User Management module.
2. **Registration (Employee):** New employees register via the registration interface by providing their Corporate Email and a valid Company Access Token.
3. **Validation & Role Provisioning:** The backend validates the single-use token and provisions the account with appropriate permissions.

---

## 🚀 Quick Start Guide (Docker Setup)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Git](https://git-scm.com/) installed.

### 1. Clone the Repository

```bash
git clone [https://github.com/narayanahrithikraj/AI-Powered-Industrial-Predictive-Maintenance-Intelligence-Platform.git](https://github.com/narayanahrithikraj/AI-Powered-Industrial-Predictive-Maintenance-Intelligence-Platform.git)
cd AI-Powered-Industrial-Predictive-Maintenance-Intelligence-Platform

🔑 Demo Credentials
Administrator : admin@enterprise.com
Password : secret

Operator/Engineer : user@enterprise.com
Password : secret
```
