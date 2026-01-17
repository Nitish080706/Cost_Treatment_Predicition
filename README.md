Cost Treatment Prediction System
Overview

The Cost Treatment Prediction System is an AI-driven healthcare application that predicts annual medical treatment costs based on health conditions, lifestyle factors, and insurance details.
The system supports both structured health data and vague or incomplete disease inputs, ensuring predictions are always generated without user friction.

Abstract

This project uses an ensemble machine learning approach to estimate medical treatment costs with improved accuracy and stability. Five regression models are combined using a voting mechanism to generate a final prediction.

To handle diseases not fully specified by the user, the system integrates a large language model through the Groq API using Llama 3. The AI infers the most probable clinical characteristics of a disease and converts them into structured data, which is then used for cost estimation.
An interactive web interface provides visual insights into the factors affecting healthcare expenses.

Key Features

Secure user authentication (JWT and bcrypt)

Medical cost prediction using ensemble machine learning

Intelligent handling of vague or unspecified disease inputs

AI-based disease profiling and cost estimation

Interactive analytics and data visualizations

Prediction history storage and healthcare assistant chatbot

System Architecture

Frontend: HTML, CSS, JavaScript with interactive visualizations

Backend: REST API built using Flask

ML Layer: Ensemble regression model for cost prediction

Database: MongoDB

AI Layer: Disease inference and NLP processing using Groq + Llama 3

Intelligent Disease Handling (Vague Input Support)

When a user mentions a disease without specifying its type, stage, or severity, the system applies a three-layered intelligent mapping process:

1. AI Inference Layer

The disease name is sent to the AI profiling endpoint powered by Llama 3.
The model infers the most statistically common medical characteristics of the disease.

Example for “Diabetes”:

Category: Endocrine

Chronic: Yes

Treatment Type: Medication-based

Severity: Moderate (default assumption)

2. Structured Profile Transformation

The AI converts the inferred information into a structured disease profile, including:

Disease category (cardiac, renal, neurological, etc.)

Treatment approach (medication, surgery, lifestyle)

Resource requirements such as hospitalization, tests, and specialist care

This structured profile ensures compatibility with the prediction pipeline.

3. Backend Fallback Mechanism

If the AI cannot generate a valid profile due to extreme ambiguity, the backend applies a safe default profile instead of returning an error.

Default assumptions:

Category: Other

Severity: Moderate

Hospitalization: No

Average stay: 2 days

Test intensity: Moderate

4. Cost Scaling Logic

Once the disease profile is finalized, the system applies mathematical cost multipliers to a base cost:

Chronic condition → 1.5× multiplier

Surgery required → 2.0× multiplier

The system outputs a cost range (for example, ₹20,000 – ₹35,000) along with a disclaimer that actual expenses may vary based on provider and disease specifics.

Machine Learning Models

The prediction engine uses a Voting Regressor combining:

Random Forest

XGBoost

Gradient Boosting

AdaBoost

Extra Trees

Preprocessing includes label encoding for categorical features and standard scaling for numerical values.

Dataset

File: costdata.csv

Contains: demographic data, lifestyle metrics, clinical history, hospital admissions, and previous year medical costs

Technology Stack

Languages: Python, JavaScript, HTML, CSS

Backend: Flask

Database: MongoDB

ML: scikit-learn, XGBoost, pandas, numpy

Frontend: Chart.js, Three.js

AI: Groq Python SDK (Llama 3)

'''bash
cd backend
python app.py
'''

Author

Nitish M
B.Tech – Artificial Intelligence and Data Science
