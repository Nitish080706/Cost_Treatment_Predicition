from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/costtreatment')

_client = None
_db = None

def get_database():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGODB_URI)
        db_name = MONGODB_URI.split('/')[-1] or 'costtreatment'
        _db = _client[db_name]
    return _db

def close_database():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_user(user_data):
    db = get_database()
    users = db.users
    
    password = user_data.get('password')
    password_hash = hash_password(password) if password else None
    
    user_doc = {
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'age': user_data.get('age'),
        'gender': user_data.get('gender'),
        'password_hash': password_hash,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = users.insert_one(user_doc)
    return str(result.inserted_id)

def get_user_by_email(email):
    db = get_database()
    users = db.users
    return users.find_one({'email': email})

def get_user_by_id(user_id):
    from bson import ObjectId
    db = get_database()
    users = db.users
    return users.find_one({'_id': ObjectId(user_id)})

def authenticate_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not user.get('password_hash'):
        return None
    
    if verify_password(password, user['password_hash']):
        return user
    return None

def update_user(email, user_data):
    db = get_database()
    users = db.users
    
    user_data['updated_at'] = datetime.utcnow()
    result = users.update_one({'email': email}, {'$set': user_data})
    return result.modified_count > 0

def save_prediction(user_email, prediction_data):
    db = get_database()
    predictions = db.predictions
    
    prediction_doc = {
        'user_email': user_email,
        'prediction': prediction_data.get('prediction'),
        'prediction_inr': prediction_data.get('prediction_inr'),
        'input_data': prediction_data.get('input_data'),
        'cost_explanation': prediction_data.get('cost_explanation'),
        'individual_predictions': prediction_data.get('individual_predictions'),
        'timestamp': datetime.utcnow()
    }
    
    result = predictions.insert_one(prediction_doc)
    return str(result.inserted_id)

def get_user_predictions(user_email, limit=10):
    db = get_database()
    predictions = db.predictions
    
    cursor = predictions.find({'user_email': user_email}).sort('timestamp', -1).limit(limit)
    results = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return results

def get_all_users(limit=100):
    db = get_database()
    users = db.users
    
    cursor = users.find().limit(limit)
    results = []
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return results

def delete_user(email):
    db = get_database()
    users = db.users
    predictions = db.predictions
    
    users.delete_one({'email': email})
    predictions.delete_many({'user_email': email})
    return True
