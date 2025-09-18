import pandas as pd
import numpy as np
from faker import Faker
from sklearn.datasets import make_classification, make_regression
from sklearn.preprocessing import StandardScaler
import json
import os
from datetime import datetime, timedelta
import random
from models import DataType, PrivacyLevel
import tempfile
import shutil

class SyntheticDataGenerator:
    def __init__(self):
        self.fake = Faker()
        
    def generate_dataset(self, data_type: DataType, size: int, privacy_level: PrivacyLevel, params: str = None, request_id: int = None):
        """Generate synthetic dataset based on request parameters."""
        
        # Parse additional parameters
        additional_params = {}
        if params:
            try:
                additional_params = json.loads(params)
            except json.JSONDecodeError:
                additional_params = {}
        
        # Generate data based on type
        if data_type == DataType.HEALTH_RECORDS:
            df = self._generate_health_records(size, privacy_level, additional_params)
        elif data_type == DataType.FINANCIAL_DATA:
            df = self._generate_financial_data(size, privacy_level, additional_params)
        elif data_type == DataType.SENSOR_LOGS:
            df = self._generate_sensor_logs(size, privacy_level, additional_params)
        elif data_type == DataType.CUSTOMER_DATA:
            df = self._generate_customer_data(size, privacy_level, additional_params)
        elif data_type == DataType.RESEARCH_DATA:
            df = self._generate_research_data(size, privacy_level, additional_params)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Apply privacy transformations
        df = self._apply_privacy_transformations(df, privacy_level)
        
        # Save to file using a temp file to avoid Windows locking issues
        output_dir = f"./storage/requests/{request_id}"
        os.makedirs(output_dir, exist_ok=True)
        final_path = os.path.join(output_dir, "data.csv")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="") as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        # Copy to final path and remove temp
        shutil.copy2(tmp_path, final_path)
        os.unlink(tmp_path)
        
        return final_path
    
    def _generate_health_records(self, size: int, privacy_level: PrivacyLevel, params: dict):
        """Generate synthetic health records."""
        data = []
        
        for _ in range(size):
            record = {
                'patient_id': self.fake.uuid4(),
                'age': random.randint(18, 100),
                'gender': random.choice(['M', 'F', 'Other']),
                'height_cm': round(random.normalvariate(170, 15), 1),
                'weight_kg': round(random.normalvariate(70, 15), 1),
                'blood_pressure_systolic': random.randint(90, 180),
                'blood_pressure_diastolic': random.randint(60, 120),
                'heart_rate': random.randint(50, 120),
                'temperature_c': round(random.normalvariate(36.5, 0.5), 1),
                'cholesterol': random.randint(120, 300),
                'glucose': random.randint(70, 200),
                'diagnosis': random.choice([
                    'Hypertension', 'Diabetes', 'Normal', 'High Cholesterol',
                    'Obesity', 'Underweight', 'Cardiovascular Disease'
                ]),
                'medication': random.choice([
                    'None', 'Metformin', 'Lisinopril', 'Atorvastatin',
                    'Aspirin', 'Insulin', 'Multiple'
                ]),
                'admission_date': self.fake.date_between(start_date='-2y', end_date='today'),
                'discharge_date': self.fake.date_between(start_date='-1y', end_date='today'),
                'insurance_type': random.choice(['Private', 'Medicare', 'Medicaid', 'Uninsured'])
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def _generate_financial_data(self, size: int, privacy_level: PrivacyLevel, params: dict):
        """Generate synthetic financial data."""
        data = []
        
        for _ in range(size):
            record = {
                'transaction_id': self.fake.uuid4(),
                'customer_id': self.fake.uuid4(),
                'amount': round(random.uniform(1, 10000), 2),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
                'transaction_type': random.choice([
                    'Purchase', 'Withdrawal', 'Deposit', 'Transfer',
                    'Payment', 'Refund', 'Fee'
                ]),
                'merchant_category': random.choice([
                    'Retail', 'Restaurant', 'Gas Station', 'Online',
                    'Healthcare', 'Education', 'Entertainment', 'Travel'
                ]),
                'account_type': random.choice(['Checking', 'Savings', 'Credit', 'Investment']),
                'location': f"{self.fake.city()}, {self.fake.state()}",
                'timestamp': self.fake.date_time_between(start_date='-1y', end_date='now'),
                'is_fraudulent': random.choice([True, False]) if random.random() < 0.05 else False,
                'credit_score': random.randint(300, 850),
                'income_level': random.choice(['Low', 'Medium', 'High', 'Very High'])
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def _generate_sensor_logs(self, size: int, privacy_level: PrivacyLevel, params: dict):
        """Generate synthetic sensor data."""
        data = []
        
        # Generate time series data
        start_time = datetime.now() - timedelta(days=30)
        
        for i in range(size):
            timestamp = start_time + timedelta(minutes=i * 5)  # 5-minute intervals
            
            # Simulate sensor readings with some correlation
            base_temp = 20 + 10 * np.sin(i / 100) + random.normalvariate(0, 2)
            humidity = 50 + 20 * np.sin(i / 80) + random.normalvariate(0, 5)
            pressure = 1013 + 10 * np.sin(i / 120) + random.normalvariate(0, 3)
            
            record = {
                'sensor_id': f"SENSOR_{random.randint(1, 10):03d}",
                'timestamp': timestamp,
                'temperature_c': round(base_temp, 2),
                'humidity_percent': round(max(0, min(100, humidity)), 1),
                'pressure_hpa': round(pressure, 1),
                'light_lux': max(0, random.normalvariate(500, 200)),
                'motion_detected': random.choice([True, False]),
                'battery_level': random.randint(10, 100),
                'signal_strength': random.randint(-100, -30),
                'location_lat': round(random.uniform(40.0, 41.0), 6),
                'location_lon': round(random.uniform(-74.0, -73.0), 6),
                'device_status': random.choice(['Active', 'Maintenance', 'Error', 'Offline'])
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def _generate_customer_data(self, size: int, privacy_level: PrivacyLevel, params: dict):
        """Generate synthetic customer data."""
        data = []
        
        for _ in range(size):
            record = {
                'customer_id': self.fake.uuid4(),
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80),
                'address': self.fake.address(),
                'city': self.fake.city(),
                'state': self.fake.state(),
                'zip_code': self.fake.zipcode(),
                'country': self.fake.country(),
                'registration_date': self.fake.date_between(start_date='-5y', end_date='today'),
                'last_login': self.fake.date_time_between(start_date='-1y', end_date='now'),
                'total_orders': random.randint(0, 100),
                'total_spent': round(random.uniform(0, 50000), 2),
                'loyalty_tier': random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
                'preferred_category': random.choice([
                    'Electronics', 'Clothing', 'Books', 'Home & Garden',
                    'Sports', 'Beauty', 'Automotive', 'Food & Beverage'
                ]),
                'is_active': random.choice([True, False]),
                'marketing_consent': random.choice([True, False])
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def _generate_research_data(self, size: int, privacy_level: PrivacyLevel, params: dict):
        """Generate synthetic research data."""
        # Generate classification data
        X, y = make_classification(
            n_samples=size,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            n_classes=3,
            random_state=42
        )
        
        # Create feature names
        feature_names = [f'feature_{i+1}' for i in range(X.shape[1])]
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # Add some additional research-specific columns
        df['participant_id'] = [self.fake.uuid4() for _ in range(size)]
        df['age'] = [random.randint(18, 80) for _ in range(size)]
        df['gender'] = [random.choice(['M', 'F', 'Other']) for _ in range(size)]
        df['education_level'] = [random.choice(['High School', 'Bachelor', 'Master', 'PhD']) for _ in range(size)]
        df['income_range'] = [random.choice(['<30k', '30k-50k', '50k-75k', '75k-100k', '>100k']) for _ in range(size)]
        df['experiment_group'] = [random.choice(['Control', 'Treatment A', 'Treatment B']) for _ in range(size)]
        df['response_time_ms'] = [random.normalvariate(500, 100) for _ in range(size)]
        df['accuracy'] = [random.uniform(0.5, 1.0) for _ in range(size)]
        
        return df
    
    def _apply_privacy_transformations(self, df: pd.DataFrame, privacy_level: PrivacyLevel):
        """Apply privacy transformations based on privacy level."""
        if privacy_level == PrivacyLevel.LOW:
            # Minimal privacy - just remove direct identifiers
            if 'patient_id' in df.columns:
                df = df.drop('patient_id', axis=1)
            if 'customer_id' in df.columns:
                df = df.drop('customer_id', axis=1)
            if 'participant_id' in df.columns:
                df = df.drop('participant_id', axis=1)
                
        elif privacy_level == PrivacyLevel.MEDIUM:
            # Medium privacy - remove identifiers and add some noise
            # Remove direct identifiers
            id_columns = ['patient_id', 'customer_id', 'participant_id', 'transaction_id', 'sensor_id']
            for col in id_columns:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            
            # Add small amount of noise to numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col != 'target':  # Don't add noise to target variable
                    noise = np.random.normal(0, 0.01, len(df))
                    df[col] = df[col] + noise * df[col].std()
                    
        elif privacy_level == PrivacyLevel.HIGH:
            # High privacy - remove identifiers, add noise, and generalize
            # Remove direct identifiers
            id_columns = ['patient_id', 'customer_id', 'participant_id', 'transaction_id', 'sensor_id']
            for col in id_columns:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            
            # Add significant noise to numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col != 'target':
                    noise = np.random.normal(0, 0.05, len(df))
                    df[col] = df[col] + noise * df[col].std()
            
            # Generalize categorical data
            if 'age' in df.columns:
                df['age'] = pd.cut(df['age'], bins=[0, 30, 50, 70, 100], labels=['<30', '30-50', '50-70', '70+'])
            if 'income_range' in df.columns:
                df['income_range'] = df['income_range'].replace({
                    '<30k': 'Low', '30k-50k': 'Low', '50k-75k': 'Medium', 
                    '75k-100k': 'Medium', '>100k': 'High'
                })
                
        elif privacy_level == PrivacyLevel.MAXIMUM:
            # Maximum privacy - heavy noise and generalization
            # Remove all identifiers
            id_columns = ['patient_id', 'customer_id', 'participant_id', 'transaction_id', 'sensor_id']
            for col in id_columns:
                if col in df.columns:
                    df = df.drop(col, axis=1)
            
            # Add heavy noise to numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if col != 'target':
                    noise = np.random.normal(0, 0.1, len(df))
                    df[col] = df[col] + noise * df[col].std()
            
            # Heavy generalization
            if 'age' in df.columns:
                df['age'] = pd.cut(df['age'], bins=[0, 40, 80, 100], labels=['Young', 'Middle-aged', 'Senior'])
            if 'income_range' in df.columns:
                df['income_range'] = df['income_range'].replace({
                    '<30k': 'Low', '30k-50k': 'Low', '50k-75k': 'Low', 
                    '75k-100k': 'High', '>100k': 'High'
                })
            
            # Remove or generalize location data
            location_columns = ['address', 'city', 'state', 'zip_code', 'location_lat', 'location_lon']
            for col in location_columns:
                if col in df.columns:
                    df = df.drop(col, axis=1)
        
        return df
