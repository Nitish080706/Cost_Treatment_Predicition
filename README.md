# Cost Treatment Prediction System

## Overview

The Cost Treatment Prediction System is an AI-driven healthcare application that predicts annual medical treatment costs based on health conditions, lifestyle factors, and insurance details. The system supports both structured health data and vague or incomplete disease inputs, ensuring predictions are always generated without user friction.

## Abstract

This project uses an ensemble machine learning approach to estimate medical treatment costs with improved accuracy and stability. Five regression models are combined using a voting mechanism to generate a final prediction.

To handle diseases not fully specified by the user, the system integrates a large language model through the Groq API using Llama 3. The AI infers the most probable clinical characteristics of a disease and converts them into structured data, which is then used for cost estimation.

An interactive web interface provides visual insights into the factors affecting healthcare expenses.

## Key Features

- Secure user authentication using JWT and bcrypt
- Medical cost prediction using ensemble machine learning
- Intelligent handling of vague or unspecified disease inputs
- AI-based disease profiling and cost estimation
- Interactive analytics and data visualizations
- Prediction history storage
- Healthcare assistant chatbot

## System Architecture

The application is built using a modern, layered architecture:

- **Frontend**: HTML, CSS, JavaScript with interactive visualizations
- **Backend**: RESTful API built with Flask
- **ML Layer**: Ensemble regression model for cost prediction
- **Database**: MongoDB for data persistence
- **AI Layer**: Disease inference and NLP processing using Groq API with Llama 3

## Intelligent Disease Handling

When a user mentions a disease without specifying its type, stage, or severity, the system applies a three-layered intelligent mapping process:

### 1. AI Inference Layer

The disease name is sent to the AI profiling endpoint powered by Llama 3. The model infers the most statistically common medical characteristics of the disease.

**Example for "Diabetes":**
- Category: Endocrine
- Chronic: Yes
- Treatment Type: Medication-based
- Severity: Moderate (default assumption)

### 2. Structured Profile Transformation

The AI converts the inferred information into a structured disease profile, including:
- Disease category (cardiac, renal, neurological, etc.)
- Treatment approach (medication, surgery, lifestyle)
- Resource requirements such as hospitalization, tests, and specialist care

This structured profile ensures compatibility with the prediction pipeline.

### 3. Backend Fallback Mechanism

If the AI cannot generate a valid profile due to extreme ambiguity, the backend applies a safe default profile instead of returning an error.

**Default assumptions:**
- Category: Other
- Severity: Moderate
- Hospitalization: No
- Average stay: 2 days
- Test intensity: Moderate

### 4. Cost Scaling Logic

Once the disease profile is finalized, the system applies mathematical cost multipliers to a base cost:
- Chronic condition: 1.5x multiplier
- Surgery required: 2.0x multiplier

The system outputs a cost range (for example, ₹20,000 – ₹35,000) along with a disclaimer that actual expenses may vary based on provider and disease specifics.

## Machine Learning Models

The prediction engine uses a Voting Regressor combining five different algorithms:

- Random Forest
- XGBoost
- Gradient Boosting
- AdaBoost
- Extra Trees

Preprocessing includes label encoding for categorical features and standard scaling for numerical values to ensure optimal model performance.

## Dataset

- **File**: `costdata.csv`
- **Contains**: Demographic data, lifestyle metrics, clinical history, hospital admissions, and previous year medical costs

## Technology Stack

### Languages
- Python
- JavaScript
- HTML
- CSS

### Backend
- Flask

### Database
- MongoDB

### Machine Learning
- scikit-learn
- XGBoost
- pandas
- numpy

### Frontend Visualization
- Chart.js
- Three.js

### AI Integration
- Groq Python SDK (Llama 3)

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB installed and running
- Groq API key

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd cost-treatment-prediction-system
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with the following:
```
MONGODB_URI=<your-mongodb-connection-string>
JWT_SECRET_KEY=<your-secret-key>
GROQ_API_KEY=<your-groq-api-key>
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **User Registration/Login**: Create an account or log in to access the system
2. **Input Health Data**: Enter your health conditions, lifestyle factors, and insurance details
3. **Disease Input**: Specify diseases with as much or as little detail as you have available
4. **Get Predictions**: Receive cost predictions along with visualizations and insights
5. **View History**: Access your prediction history and track changes over time
6. **Chat Assistant**: Use the healthcare chatbot for additional guidance

## API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/predict` - Cost prediction
- `POST /api/disease-profile` - AI disease profiling
- `GET /api/history` - Retrieve prediction history
- `POST /api/chat` - Healthcare assistant chatbot

## Future Enhancements

- Integration with electronic health records (EHR)
- Real-time insurance verification
- Multi-language support
- Mobile application development
- Enhanced visualization dashboards
- Integration with healthcare providers

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Disclaimer

This system is designed for educational and informational purposes only. The cost predictions are estimates based on historical data and should not be considered as definitive medical or financial advice. Always consult with healthcare professionals and insurance providers for accurate information regarding treatment costs.

## Author

**Nitish M**  
B.Tech – Artificial Intelligence and Data Science

## Acknowledgments

- Groq for providing the AI inference API
- The open-source community for the machine learning libraries
- Healthcare professionals who provided domain expertise
