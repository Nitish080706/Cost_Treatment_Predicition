import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor, VotingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json

class CostPredictionEnsemble:
    def __init__(self):
        self.models = {}
        self.ensemble = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.feature_importance = {}
        
    def load_and_preprocess_data(self, csv_path):
        df = pd.read_csv(csv_path)
        
        X = df.drop('annual_medical_cost', axis=1)
        y = df['annual_medical_cost']
        
        categorical_cols = ['gender', 'smoker', 'insurance_type', 'city_type', 'physical_activity_level']
        
        for col in categorical_cols:
            if col in X.columns:
                self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col])
        
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test, X_train, X_test
    
    def build_models(self):
        self.models['Random Forest'] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.models['Gradient Boosting'] = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        self.models['XGBoost'] = XGBRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        self.models['AdaBoost'] = AdaBoostRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        
        self.models['Extra Trees'] = ExtraTreesRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    
    def train_individual_models(self, X_train, y_train, X_test, y_test):
        results = {}
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'RMSE': rmse,
                'MAE': mae,
                'R2': r2
            }
            
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(self.feature_names, model.feature_importances_))
        
        return results
    
    def create_voting_ensemble(self, X_train, y_train, X_test, y_test):
        estimators = [(name, model) for name, model in self.models.items()]
        
        self.ensemble = VotingRegressor(estimators=estimators)
        self.ensemble.fit(X_train, y_train)
        
        y_pred = self.ensemble.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
    
    def save_models(self, output_dir='models'):
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        joblib.dump(self.ensemble, f'{output_dir}/ensemble_model.pkl')
        
        for name, model in self.models.items():
            filename = name.lower().replace(' ', '_')
            joblib.dump(model, f'{output_dir}/{filename}_model.pkl')
        
        joblib.dump(self.scaler, f'{output_dir}/scaler.pkl')
        joblib.dump(self.label_encoders, f'{output_dir}/label_encoders.pkl')
        
        with open(f'{output_dir}/feature_names.json', 'w') as f:
            json.dump(self.feature_names, f)
        
        feature_importance_serializable = {}
        for model_name, features in self.feature_importance.items():
            feature_importance_serializable[model_name] = {k: float(v) for k, v in features.items()}
        
        with open(f'{output_dir}/feature_importance.json', 'w') as f:
            json.dump(feature_importance_serializable, f)
    
    def cross_validate_ensemble(self, X, y, cv=5):
        scores = cross_val_score(self.ensemble, X, y, cv=cv, scoring='r2', n_jobs=-1)
        return scores

def main():
    ensemble = CostPredictionEnsemble()
    
    X_train, X_test, y_train, y_test, X_train_orig, X_test_orig = ensemble.load_and_preprocess_data(
        '../dataset/costdata.csv'
    )
    
    ensemble.build_models()
    
    individual_results = ensemble.train_individual_models(X_train, y_train, X_test, y_test)
    
    ensemble_results = ensemble.create_voting_ensemble(X_train, y_train, X_test, y_test)
    
    ensemble.cross_validate_ensemble(X_train, y_train)
    
    ensemble.save_models()

if __name__ == "__main__":
    main()
