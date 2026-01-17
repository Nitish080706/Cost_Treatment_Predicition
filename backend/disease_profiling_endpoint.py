@app.route('/api/profile-disease', methods=['POST'])
def profile_disease():
    """
    Use LLM to extract structured medical characteristics from unknown diseases.
    LLM outputs disease profile (NOT cost), which is then mapped to cost estimation.
    """
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
        
        # System prompt for disease profiling (Medical Knowledge Mapper)
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

        # Call Groq LLM for disease profiling
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower temperature for more consistent structured output
            max_tokens=400
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Parse LLM JSON output
        try:
            # Try to extract JSON if LLM added extra text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                disease_profile = json.loads(json_match.group())
            else:
                disease_profile = json.loads(response_text)
        except:
            # Fallback if JSON parsing fails
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
        
        # Cost estimation based on disease profile
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

def estimate_cost_from_profile(profile, existing_conditions):
    """
    Estimate cost range from disease profile using rule-based logic.
    This is academically sound and ethically safe.
    """
    
    # Base cost calculation
    base_costs = {
        'minor': 5000,
        'moderate': 25000,
        'severe': 75000
    }
    
    base_cost = base_costs.get(profile.get('severity', 'moderate'), 25000)
    
    # Multipliers based on profile
    multiplier = 1.0
    
    # Treatment type impact
    treatment_multipliers = {
        'medication_only': 0.6,
        'lifestyle_management': 0.4,
        'procedure_based': 1.3,
        'surgery_required': 2.0,
        'mixed': 1.1
    }
    multiplier *= treatment_multipliers.get(profile.get('treatment_type', 'mixed'), 1.0)
    
    # Hospitalization impact
    if profile.get('hospitalization', False):
        stay_days = profile.get('avg_stay_days', 3)
        multiplier *= (1 + (stay_days * 0.15))  # 15% per day
    
    # Tests required
    test_multipliers = {'minimal': 1.0, 'moderate': 1.2, 'extensive': 1.5}
    multiplier *= test_multipliers.get(profile.get('tests_required', 'moderate'), 1.2)
    
    # Medication duration
    med_multipliers = {
        'none': 0.9,
        'short_term': 1.0,
        'long_term': 1.4,
        'lifelong': 1.8
    }
    multiplier *= med_multipliers.get(profile.get('medication_duration', 'short_term'), 1.0)
    
    # Chronic condition
    if profile.get('chronic', False):
        multiplier *= 1.5
    
    # Specialist required
    if profile.get('specialist_required', False):
        multiplier *= 1.2
    
    # Existing conditions impact
    if len(existing_conditions) > 0:
        multiplier *= (1 + (len(existing_conditions) * 0.1))
    
    # Calculate range
    estimated_cost = base_cost * multiplier
    min_cost = int(estimated_cost * 0.7)  # 30% below
    max_cost = int(estimated_cost * 1.4)  # 40% above
    
    # Determine confidence
    confidence_factors = {
        'minor': 'medium',
        'moderate': 'medium',
        'severe': 'low'
    }
    confidence = confidence_factors.get(profile.get('severity', 'moderate'), 'medium')
    
    # Basis explanation
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
