# AI Powered Insurance Tool

This repository contains the architecture, core services, and MLOps pipelines for a comprehensive system designed to **automate insurance claims processing**, **verify policy eligibility**, and **detect fraudulent activities** using a **microservices** and **machine learning** approach.

---

## Features at a Glance
- **Secure Document Ingestion:** Handles policy and claim document uploads with secure AWS S3 storage and versioning.  
- **Intelligent Document Processing:** Uses AWS Textract and fine-tuned LayoutLMv3 for accurate OCR and key-value pair extraction.  
- **ML-Driven Predictions:** Includes LightGBM for eligibility prediction and XGBoost/Isolation Forest for real-time fraud scoring.  
- **Transparent Decisioning:** A Rule Engine (`durable_rules`) combines AI scores with business rules to generate final, explainable decisions.  
- **Multi-Channel Support:** Features a Rasa/GPT-4 Chatbot integrated with React UI and WhatsApp for status updates.  
- **Full Observability:** Implements MLflow for experiment tracking, DVC for data versioning, and Evidently AI for model drift monitoring.

---

## System Architecture: Modular Overview

The system is built as a set of **interconnected FastAPI microservices** deployed on **AWS ECS Fargate**, orchestrated by **AWS Step Functions**.

### Core Modules

#### 1. Data Ingestion
**Goal:** Securely collect and store documents.  
**Key Technologies:** React, FastAPI, S3, RDS (PostgreSQL), SQS, Cognito

#### 2. Document Understanding
**Goal:** Extract structured data from documents.  
**Key Technologies:** SQS Workers, AWS Textract, LayoutLMv3 (HuggingFace), spaCy, Pandas

#### 3. Policy Matching
**Goal:** Verify extracted data against internal records.  
**Key Technologies:** FastAPI, Insurer DB API, RapidFuzz, Redis Caching

#### 4. Eligibility Prediction
**Goal:** Predict claim approval probability.  
**Key Technologies:** LightGBM, MLflow, FastAPI, SHAP

#### 5. Fraud Detection
**Goal:** Identify suspicious claims and anomalies.  
**Key Technologies:** XGBoost, Isolation Forest, PyTorch Geometric (Optional GNN)

#### 6. Rule Engine
**Goal:** Combine AI scores and business logic for final decision.  
**Key Technologies:** YAML Rules, durable_rules, AWS Step Functions

#### 7. Chatbot Interface
**Goal:** Provide instant claim status and support.  
**Key Technologies:** React UI, Rasa/GPT-4, Pinecone/Kendra (RAG)

#### 8. Knowledge Layer
**Goal:** Centralized, specialized data storage.  
**Key Technologies:** RDS (PostgreSQL), MongoDB Atlas, Pinecone (Vector DB)
