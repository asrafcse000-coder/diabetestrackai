import joblib
import numpy as np
import pandas as pd

class DiabetesModel:
    def __init__(self, model_path):
        # Load the tuned random forest model
        self.model = joblib.load(model_path)
        
        # The exact order of features your model was trained on:
        self.feature_columns = [
            'age', 'hypertension', 'heart_disease', 'bmi', 
            'HbA1c_level', 'blood_glucose_level', 'gender_Male', 
            'gender_Other', 'smoking_history_current', 'smoking_history_ever', 
            'smoking_history_former', 'smoking_history_never', 'smoking_history_not current'
        ]

    def preprocess_input(self, data):
        """
        Transforms form data into a 13-feature vector.
        'data' is a dictionary from the Flask form.
        """
        # Initialize features with 0
        input_dict = {col: 0 for col in self.feature_columns}

        # Numeric and Binary mapping
        input_dict['age'] = float(data.get('age', 0))
        input_dict['hypertension'] = int(data.get('hypertension', 0))
        input_dict['heart_disease'] = int(data.get('heart_disease', 0))
        input_dict['bmi'] = float(data.get('bmi', 0))
        input_dict['HbA1c_level'] = float(data.get('hba1c', 0))
        input_dict['blood_glucose_level'] = float(data.get('glucose', 0))

        # One-Hot Encoding for Gender (Female is the base/dropped category)
        gender = data.get('gender')
        if f'gender_{gender}' in input_dict:
            input_dict[f'gender_{gender}'] = 1

        # One-Hot Encoding for Smoking History (No Info is the base/dropped category)
        smoking = data.get('smoking')
        if f'smoking_history_{smoking}' in input_dict:
            input_dict[f'smoking_history_{smoking}'] = 1

        # Convert to DataFrame to maintain column order
        df = pd.DataFrame([input_dict])
        return df

    def predict(self, processed_data):
        prediction = self.model.predict(processed_data)
        probability = self.model.predict_proba(processed_data)[0][1]
        return int(prediction[0]), round(probability * 100, 2)