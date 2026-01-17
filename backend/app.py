from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json
import pandas as pd
import numpy as np
import os
from groq import Groq
from dotenv import load_dotenv
from database import get_database, create_user, get_user_by_email, get_user_by_id, save_prediction, get_user_predictions, authenticate_user
import jwt
from datetime import datetime, timedelta
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)

ensemble_model = None
scaler = None
label_encoders = None
feature_names = None
feature_importance = None
dataset = None

groq_client = None
try:
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        groq_client = Groq(api_key=api_key)
except Exception as e:
    pass

def load_models():
    global ensemble_model, scaler, label_encoders, feature_names, feature_importance, dataset
    
    models_dir = 'models'
    
    try:
        ensemble_model = joblib.load(f'{models_dir}/ensemble_model.pkl')
        scaler = joblib.load(f'{models_dir}/scaler.pkl')
        label_encoders = joblib.load(f'{models_dir}/label_encoders.pkl')
        
        with open(f'{models_dir}/feature_names.json', 'r') as f:
            feature_names = json.load(f)
        
        with open(f'{models_dir}/feature_importance.json', 'r') as f:
            feature_importance = json.load(f)
        
        dataset = pd.read_csv('../dataset/costdata.csv')
        
        return True
    except Exception as e:
        return False

JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return jsonify({
        'message': 'Cost Prediction Treatment API',
        'version': '1.0',
        'endpoints': [
            '/api/predict',
            '/api/chat',
            '/api/profile-disease',
            '/api/statistics',
            '/api/visualizations',
            '/api/feature-importance',
            '/api/auth/signup',
            '/api/auth/login',
            '/api/auth/me',
            '/api/users/predictions'
        ]
    })

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'success': False, 'error': 'Email, password, and name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'error': 'User already exists'}), 409
        
        user_id = create_user(data)
        
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            },
            'message': 'User registered successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        user = authenticate_user(email, password)
        if not user:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        token = jwt.encode({
            'user_id': str(user['_id']),
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name'),
                'age': user.get('age'),
                'gender': user.get('gender')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': str(current_user['_id']),
                'email': current_user['email'],
                'name': current_user.get('name'),
                'age': current_user.get('age'),
                'gender': current_user.get('gender')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/users/predictions', methods=['GET'])
@token_required
def get_predictions_history(current_user):
    try:
        email = current_user['email']
        limit = int(request.args.get('limit', 10))
        
        predictions = get_user_predictions(email, limit)
        return jsonify({'success': True, 'predictions': predictions, 'count': len(predictions)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        input_type = data.get('type', 'text')
        
        if not groq_client:
            return jsonify({
                'success': False,
                'error': 'Chat service not available. Please set GROQ_API_KEY environment variable.'
            }), 503
        
        if input_type == 'option':
            option_responses = {
                'quick_estimate': "I can help you get a quick cost estimate! Please fill out the prediction form below with your health information, and I'll calculate your estimated annual medical costs using our advanced ensemble learning models.",
                'health_tips': "Here are some health tips to help reduce medical costs:\n\n1. **Stay Active**: Regular physical activity (aim for 10,000 steps daily) can reduce healthcare costs by up to 30%\n2. **Maintain Healthy BMI**: Keep your BMI between 18.5-24.9\n3. **Manage Stress**: High stress levels (7+/10) correlate with higher medical costs\n4. **Regular Checkups**: Preventive care can catch issues early\n5. **Quality Sleep**: 7-9 hours per night improves health outcomes",
                'insurance_info': "Understanding insurance can help reduce costs:\n\n• **Private Insurance**: Typically covers 70-90% of costs but has higher premiums\n• **Government Insurance**: Usually covers 50-70% with lower premiums\n• **No Insurance**: You pay 100% out-of-pocket\n\nOur system considers your insurance type and coverage percentage to give accurate cost predictions.",
                'cost_factors': "Major factors affecting your medical costs:\n\n1. **Age**: Costs typically increase with age\n2. **Chronic Conditions**: Diabetes, hypertension, heart disease significantly impact costs\n3. **Lifestyle**: Smoking, low activity, poor sleep increase costs\n4. **Previous Year Costs**: Strong predictor of future costs\n5. **Location**: Urban areas often have higher medical costs than rural\n\nUse the form below to see how these factors affect YOUR estimated costs!"
            }
            
            response_text = option_responses.get(message, "I'm here to help you understand medical cost predictions. Please choose an option or ask me a question!")
            
            return jsonify({
                'success': True,
                'response': response_text,
                'type': 'option'
            })
        
        system_prompt = """You are a medical cost prediction and insurance assistant. You ONLY answer questions about:
1. Medical costs and healthcare pricing
2. Health insurance (types, coverage, benefits)
3. Medical conditions and their treatment costs
4. Healthcare factors affecting costs (lifestyle, chronic conditions)
5. Using the cost prediction system

You MUST REFUSE to answer questions about:
- General knowledge, trivia, or non-medical topics
- Programming, technology (except this health system)
- Entertainment, sports, politics, or current events
- Any topic not directly related to healthcare costs or insurance

If a user asks an off-topic question, politely respond: "I'm specialized in medical cost prediction and insurance matters only. Please ask about healthcare costs, insurance, or use the cost prediction form."

Keep responses concise (2-3 paragraphs max), friendly, and informative. Remind users that predictions are estimates and not medical advice."""
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = chat_completion.choices[0].message.content
        
        return jsonify({
            'success': True,
            'response': response_text,
            'type': 'text'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/profile-disease', methods=['POST'])
def profile_disease():
    try:
        data = request.json
        disease_description = data.get('disease_description', '').strip()
        existing_conditions = data.get('existing_conditions', [])
        
        if not disease_description:
            return jsonify({
                'success': False,
                'error': 'Disease description is required'
            }), 400
        
        if not groq_client:
            return jsonify({
                'success': False,
                'error': 'Disease profiling service not available'
            }), 503
        
        system_prompt = """You are a medical knowledge mapper. Your ONLY role is to classify and profile diseases based on treatment characteristics.

You must output ONLY a valid JSON object with these exact fields:
{
  "disease_category": "string (Cardiac, Renal, Respiratory, Digestive, Neurological, Musculoskeletal, Dermatological, Endocrine, Other)",
  "chronic": boolean,
  "treatment_type": "string (medication_only, procedure_based, surgery_required, lifestyle_management, mixed)",
  "hospitalization": boolean,
  "avg_stay_days": number (0-30),
  "tests_required": "string (minimal, moderate, extensive)",
  "medication_duration": "string (none, short_term, long_term, lifelong)",
  "severity": "string (minor, moderate, severe)",
  "specialist_required": boolean
}

DO NOT provide cost estimates. DO NOT provide medical advice. ONLY provide structured disease characteristics."""

        user_prompt = f"""Disease/Condition: {disease_description}
        
Existing Health Conditions: {', '.join(existing_conditions) if existing_conditions else 'None'}

Provide disease profiling JSON:"""

        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=400
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                disease_profile = json.loads(json_match.group())
            else:
                disease_profile = json.loads(response_text)
        except:
            disease_profile = {
                "disease_category": "Other",
                "chronic": False,
                "treatment_type": "mixed",
                "hospitalization": False,
                "avg_stay_days": 2,
                "tests_required": "moderate",
                "medication_duration": "short_term",
                "severity": "moderate",
                "specialist_required": True
            }
        
        cost_range = estimate_cost_from_profile(disease_profile, existing_conditions)
        
        return jsonify({
            'success': True,
            'prediction_type': 'estimated_range',
            'cost_range': cost_range,
            'disease_profile': disease_profile,
            'confidence': cost_range['confidence'],
            'basis': cost_range['basis'],
            'disclaimer': 'This is an estimated cost range based on similar medical conditions and treatment complexity. Actual costs may vary significantly based on individual circumstances, location, and healthcare provider. This is NOT a medical diagnosis or treatment recommendation.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def generate_cost_explanation(feature_mapping, predicted_cost):
    explanations = []
    impact_factors = []
    
    age = feature_mapping['age']
    if age > 60:
        explanations.append(f"Age {age} years (Senior citizens typically have 30-40% higher costs)")
        impact_factors.append(("Age Factor", "High", "+₹" + f"{int(predicted_cost * 0.25):,}"))
    elif age > 45:
        explanations.append(f"Age {age} years (Middle-aged adults have moderately higher costs)")
        impact_factors.append(("Age Factor", "Medium", "+₹" + f"{int(predicted_cost * 0.15):,}"))
    else:
        explanations.append(f"Age {age} years (Younger individuals have lower baseline costs)")
    
    bmi = feature_mapping['bmi']
    if bmi > 30:
        explanations.append(f"BMI {bmi:.1f} (Obesity increases costs by 20-35%)")
        impact_factors.append(("BMI (Obesity)", "High", "+₹" + f"{int(predicted_cost * 0.2):,}"))
    elif bmi > 25:
        explanations.append(f"BMI {bmi:.1f} (Overweight adds 10-15% to costs)")
        impact_factors.append(("BMI (Overweight)", "Medium", "+₹" + f"{int(predicted_cost * 0.1):,}"))
    elif bmi < 18.5:
        explanations.append(f"BMI {bmi:.1f} (Underweight may require additional care)")
    
    if feature_mapping['smoker'] == 'Yes':
        explanations.append("Smoking status (Smokers face 40-50% higher medical costs)")
        impact_factors.append(("Smoking", "Very High", "+₹" + f"{int(predicted_cost * 0.35):,}"))
    
    chronic_count = sum([
        feature_mapping['diabetes'],
        feature_mapping['hypertension'],
        feature_mapping['heart_disease'],
        feature_mapping['asthma']
    ])
    
    if chronic_count >= 2:
        explanations.append(f"{chronic_count} chronic conditions (Multiple conditions significantly increase costs)")
        impact_factors.append((f"{chronic_count} Chronic Conditions", "Very High", "+₹" + f"{int(predicted_cost * 0.4):,}"))
    elif chronic_count == 1:
        condition_name = ""
        if feature_mapping['diabetes']: condition_name = "Diabetes"
        elif feature_mapping['hypertension']: condition_name = "Hypertension"
        elif feature_mapping['heart_disease']: condition_name = "Heart Disease"
        elif feature_mapping['asthma']: condition_name = "Asthma"
        explanations.append(f"{condition_name} (Adds 15-25% to annual costs)")
        impact_factors.append((condition_name, "Medium", "+₹" + f"{int(predicted_cost * 0.18):,}"))
    
    hospital_admissions = feature_mapping['hospital_admissions']
    if hospital_admissions > 2:
        explanations.append(f"{hospital_admissions} hospital admissions (Frequent hospitalizations)")
        impact_factors.append(("Hospitalizations", "High", "+₹" + f"{int(predicted_cost * 0.25):,}"))
    elif hospital_admissions > 0:
        explanations.append(f"{hospital_admissions} hospital admission(s) this year")
    
    medications = feature_mapping['medication_count']
    if medications > 5:
        explanations.append(f"{medications} daily medications (High medication costs)")
        impact_factors.append(("Medications", "High", "+₹" + f"{int(predicted_cost * 0.15):,}"))
    elif medications > 2:
        explanations.append(f"{medications} daily medications (Moderate medication expenses)")
    
    activity = feature_mapping['physical_activity_level']
    if activity == 'Low':
        explanations.append("Low physical activity (Sedentary lifestyle increases health risks)")
        impact_factors.append(("Low Activity", "Medium", "+₹" + f"{int(predicted_cost * 0.12):,}"))
    elif activity == 'High':
        explanations.append("High physical activity (Active lifestyle reduces costs by 10-15%)")
        impact_factors.append(("High Activity", "Positive", "-₹" + f"{int(predicted_cost * 0.12):,}"))
    
    insurance_type = feature_mapping['insurance_type']
    coverage_pct = feature_mapping['insurance_coverage_pct']
    
    out_of_pocket = predicted_cost * (100 - coverage_pct) / 100
    explanations.append(f"{insurance_type} insurance with {coverage_pct}% coverage")
    explanations.append(f"Out-of-pocket expense: ₹{int(out_of_pocket):,}")
    
    return {
        'total_cost_inr': f"₹{int(predicted_cost):,}",
        'summary': " | ".join(explanations[:3]) + "...",
        'detailed_factors': impact_factors,
        'insurance_coverage': {
            'type': insurance_type,
            'coverage_percentage': f"{coverage_pct}%",
            'covered_amount': f"₹{int(predicted_cost * coverage_pct / 100):,}",
            'out_of_pocket': f"₹{int(out_of_pocket):,}"
        }
    }

def estimate_cost_from_profile(profile, existing_conditions):
    base_costs = {
        'minor': 5000,
        'moderate': 25000,
        'severe': 75000
    }
    
    base_cost = base_costs.get(profile.get('severity', 'moderate'), 25000)
    
    multiplier = 1.0
    
    treatment_multipliers = {
        'medication_only': 0.6,
        'lifestyle_management': 0.4,
        'procedure_based': 1.3,
        'surgery_required': 2.0,
        'mixed': 1.1
    }
    multiplier *= treatment_multipliers.get(profile.get('treatment_type', 'mixed'), 1.0)
    
    if profile.get('hospitalization', False):
        stay_days = profile.get('avg_stay_days', 3)
        multiplier *= (1 + (stay_days * 0.15))
    
    test_multipliers = {'minimal': 1.0, 'moderate': 1.2, 'extensive': 1.5}
    multiplier *= test_multipliers.get(profile.get('tests_required', 'moderate'), 1.2)
    
    med_multipliers = {
        'none': 0.9,
        'short_term': 1.0,
        'long_term': 1.4,
        'lifelong': 1.8
    }
    multiplier *= med_multipliers.get(profile.get('medication_duration', 'short_term'), 1.0)
    
    if profile.get('chronic', False):
        multiplier *= 1.5
    
    if profile.get('specialist_required', False):
        multiplier *= 1.2
    
    if len(existing_conditions) > 0:
        multiplier *= (1 + (len(existing_conditions) * 0.1))
    
    estimated_cost = base_cost * multiplier
    min_cost = int(estimated_cost * 0.7)
    max_cost = int(estimated_cost * 1.4)
    
    confidence_factors = {
        'minor': 'medium',
        'moderate': 'medium',
        'severe': 'low'
    }
    confidence = confidence_factors.get(profile.get('severity', 'moderate'), 'medium')
    
    basis_parts = []
    if profile.get('hospitalization'):
        basis_parts.append(f"{profile['avg_stay_days']}-day hospitalization")
    basis_parts.append(f"{profile.get('treatment_type', 'mixed').replace('_', ' ')} treatment")
    if profile.get('chronic'):
        basis_parts.append("chronic condition management")
    
    basis = "Similar treatment complexity: " + ", ".join(basis_parts)
    
    return {
        'min': min_cost,
        'max': max_cost,
        'currency': 'INR',
        'confidence': confidence,
        'basis': basis
    }

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        features = {}
        
        feature_mapping = {
            'age': float(data.get('age', 30)),
            'gender': data.get('gender', 'Male'),
            'bmi': float(data.get('bmi', 25)),
            'smoker': data.get('smoker', 'No'),
            'diabetes': int(data.get('diabetes', 0)),
            'hypertension': int(data.get('hypertension', 0)),
            'heart_disease': int(data.get('heart_disease', 0)),
            'asthma': int(data.get('asthma', 0)),
            'physical_activity_level': data.get('physical_activity_level', 'Medium'),
            'daily_steps': float(data.get('daily_steps', 5000)),
            'sleep_hours': float(data.get('sleep_hours', 7)),
            'stress_level': float(data.get('stress_level', 5)),
            'doctor_visits_per_year': int(data.get('doctor_visits_per_year', 2)),
            'hospital_admissions': int(data.get('hospital_admissions', 0)),
            'medication_count': int(data.get('medication_count', 0)),
            'insurance_type': data.get('insurance_type', 'Government'),
            'insurance_coverage_pct': float(data.get('insurance_coverage_pct', 50)),
            'city_type': data.get('city_type', 'Urban'),
            'previous_year_cost': float(data.get('previous_year_cost', 5000))
        }
        
        for col, value in feature_mapping.items():
            if col in label_encoders:
                try:
                    features[col] = label_encoders[col].transform([value])[0]
                except:
                    features[col] = 0
            else:
                features[col] = value
        
        input_df = pd.DataFrame([features], columns=feature_names)
        
        input_scaled = scaler.transform(input_df)
        
        prediction = ensemble_model.predict(input_scaled)[0]
        
        individual_predictions = {}
        models_dir = 'models'
        model_files = {
            'Random Forest': 'random_forest_model.pkl',
            'Gradient Boosting': 'gradient_boosting_model.pkl',
            'XGBoost': 'xgboost_model.pkl',
            'AdaBoost': 'adaboost_model.pkl',
            'Extra Trees': 'extra_trees_model.pkl'
        }
        
        for name, filename in model_files.items():
            try:
                model = joblib.load(f'{models_dir}/{filename}')
                individual_predictions[name] = float(model.predict(input_scaled)[0])
            except:
                pass
        
        cost_explanation = generate_cost_explanation(feature_mapping, prediction)
        
        result = {
            'success': True,
            'prediction': float(prediction),
            'prediction_inr': float(prediction),
            'individual_predictions': individual_predictions,
            'cost_explanation': cost_explanation,
            'input_summary': {
                'age': feature_mapping['age'],
                'bmi': feature_mapping['bmi'],
                'has_chronic_conditions': any([
                    feature_mapping['diabetes'],
                    feature_mapping['hypertension'],
                    feature_mapping['heart_disease'],
                    feature_mapping['asthma']
                ]),
                'insurance_type': feature_mapping['insurance_type']
            }
        }
        
        user_email = data.get('user_email')
        if user_email:
            try:
                save_prediction(user_email, {
                    'prediction': float(prediction),
                    'prediction_inr': float(prediction),
                    'input_data': feature_mapping,
                    'cost_explanation': cost_explanation,
                    'individual_predictions': individual_predictions
                })
            except:
                pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = {
            'total_records': len(dataset),
            'cost_statistics': {
                'mean': float(dataset['annual_medical_cost'].mean()),
                'median': float(dataset['annual_medical_cost'].median()),
                'min': float(dataset['annual_medical_cost'].min()),
                'max': float(dataset['annual_medical_cost'].max()),
                'std': float(dataset['annual_medical_cost'].std())
            },
            'age_statistics': {
                'mean': float(dataset['age'].mean()),
                'min': float(dataset['age'].min()),
                'max': float(dataset['age'].max())
            },
            'categorical_distributions': {
                'gender': dataset['gender'].value_counts().to_dict(),
                'smoker': dataset['smoker'].value_counts().to_dict(),
                'insurance_type': dataset['insurance_type'].value_counts().to_dict(),
                'city_type': dataset['city_type'].value_counts().to_dict()
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    try:
        viz_data = {}
        
        age_bins = [0, 20, 30, 40, 50, 60, 70, 80, 100]
        age_labels = ['<20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80+']
        dataset['age_group'] = pd.cut(dataset['age'], bins=age_bins, labels=age_labels)
        age_cost = dataset.groupby('age_group', observed=True)['annual_medical_cost'].mean()
        viz_data['line_chart'] = {
            'labels': age_labels,
            'data': [float(age_cost.get(label, 0)) if pd.notna(age_cost.get(label, 0)) else 0.0 for label in age_labels]
        }
        
        insurance_cost = dataset.groupby('insurance_type')['annual_medical_cost'].mean()
        viz_data['bar_chart'] = {
            'labels': [str(x) for x in insurance_cost.index.tolist()],
            'data': [float(x) for x in insurance_cost.values.tolist()]
        }
        
        conditions_count = {
            'Diabetes': int(dataset['diabetes'].sum()),
            'Hypertension': int(dataset['hypertension'].sum()),
            'Heart Disease': int(dataset['heart_disease'].sum()),
            'Asthma': int(dataset['asthma'].sum()),
            'No Conditions': int(len(dataset) - (dataset['diabetes'] + dataset['hypertension'] + 
                                            dataset['heart_disease'] + dataset['asthma']).sum())
        }
        viz_data['pie_chart'] = {
            'labels': list(conditions_count.keys()),
            'data': list(conditions_count.values())
        }
        
        city_cost = dataset.groupby('city_type')['annual_medical_cost'].mean().sort_values()
        viz_data['area_chart'] = {
            'labels': [str(x) for x in city_cost.index.tolist()],
            'data': [float(x) for x in city_cost.values.tolist()]
        }
        
        doctor_visits_groups = dataset.groupby('doctor_visits_per_year').agg({
            'annual_medical_cost': 'mean',
            'age': 'count'
        }).reset_index()
        viz_data['scatter_chart'] = {
            'labels': [f"{int(row['doctor_visits_per_year'])} visits" for _, row in doctor_visits_groups.iterrows()],
            'x_data': [float(row['doctor_visits_per_year']) for _, row in doctor_visits_groups.iterrows()],
            'y_data': [float(row['annual_medical_cost']) for _, row in doctor_visits_groups.iterrows()],
            'sizes': [float(row['age']) * 2 for _, row in doctor_visits_groups.iterrows()]
        }
        
        polar_labels = []
        polar_data = []
        
        combinations = [
            ('Male', 'Yes', 'Male Smokers'),
            ('Male', 'No', 'Male Non-Smokers'),
            ('Female', 'Yes', 'Female Smokers'),
            ('Female', 'No', 'Female Non-Smokers')
        ]
        
        for gender, smoker, label in combinations:
            avg_cost = dataset[(dataset['gender'] == gender) & (dataset['smoker'] == smoker)]['annual_medical_cost'].mean()
            polar_labels.append(label)
            polar_data.append(float(avg_cost) if pd.notna(avg_cost) else 0.0)
        
        viz_data['polar_chart'] = {
            'labels': polar_labels,
            'data': polar_data
        }
        
        return jsonify(viz_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/feature-importance', methods=['GET'])
def get_feature_importance():
    try:
        avg_importance = {}
        
        for feature in feature_names:
            importances = []
            for model_name, importance_dict in feature_importance.items():
                if feature in importance_dict:
                    importances.append(importance_dict[feature])
            
            if importances:
                avg_importance[feature] = float(np.mean(importances))
        
        sorted_importance = dict(sorted(avg_importance.items(), key=lambda x: x[1], reverse=True))
        
        return jsonify({
            'feature_importance': sorted_importance,
            'top_5_features': list(sorted_importance.keys())[:5]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    if load_models():
        app.run(debug=True, port=5000)
