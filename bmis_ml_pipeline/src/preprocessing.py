"""
Preprocessing Pipeline for BMIS ML System

This module handles all data preprocessing including:
- Loading and validation
- Feature encoding and standardization
- Missing value imputation
- Feature extraction (numeric from text)
- Feature scaling
"""

import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib


class BMISPreprocessor:
    """Main preprocessing class for BMIS ML pipeline"""

    def __init__(self, data_path='data/bmis_final_ml_ready_dataset_cs_refined.csv'):
        self.data_path = data_path
        self.df = None
        self.scalers = {}
        self.encoders = {}

    def load_data(self):
        """Load dataset and perform initial validation"""
        self.df = pd.read_csv(self.data_path)
        print(f"[OK] Loaded {len(self.df)} resources")
        return self

    # ===== FEATURE STANDARDIZATION METHODS =====

    def standardize_financial_barrier_level(self):
        """Standardize financial_barrier_level to Low/Medium/High/Prohibitive"""
        if 'financial_barrier_level' not in self.df.columns:
            return self

        # Mapping logic
        mapping = {
            'Low': 'Low',
            'Moderate': 'Medium',
            'Medium': 'Medium',
            'High': 'High',
            'Prohibitive': 'Prohibitive'
        }

        self.df['financial_barrier_level_std'] = self.df['financial_barrier_level'].map(mapping)

        # For reliable values, use those; otherwise use predicted values
        if 'financial_barrier_level_reliable' in self.df.columns:
            mask = ~self.df['financial_barrier_level_reliable'].fillna(False)
            if 'financial_barrier_level_predicted' in self.df.columns:
                self.df.loc[mask, 'financial_barrier_level_std'] = \
                    self.df.loc[mask, 'financial_barrier_level_predicted']

        print(f"[OK]Standardized financial_barrier_level")
        return self

    def standardize_hidden_costs_level(self):
        """Standardize hidden_costs_level to None/Low/Medium/High"""
        if 'hidden_costs_level' not in self.df.columns:
            return self

        # Mapping logic based on cost implications
        none_costs = ['Low']
        low_costs = ['Equipment', 'Materials', 'Device Access', 'Basic Materials',
                     'Household Materials', 'Craft Materials', 'Books']
        medium_costs = ['Travel', 'Medium', 'Subscription', 'Travel-Meals',
                       'Hardware', 'Per-Class', 'Program-Fee', 'Premium-Features',
                       'Premium Features', 'Course-Materials', 'Optional Hardware',
                       'Software', 'Competition Fees', 'Transportation']
        high_costs = ['High', 'Travel, Equipment', 'Equipment-Travel',
                     'Travel, Transportation', 'Equipment, Travel',
                     'Travel-Lodging', 'Tuition', 'Housing', 'Travel-Hotel',
                     'High-travel', '3D Printer Access', 'Drone Equipment']

        def map_hidden_costs(value):
            if pd.isna(value):
                return 'Low'  # Default
            value_str = str(value)
            if value_str in none_costs:
                return 'None'
            elif value_str in low_costs:
                return 'Low'
            elif value_str in medium_costs:
                return 'Medium'
            elif value_str in high_costs:
                return 'High'
            else:
                # Default to Low for unknown values
                return 'Low'

        self.df['hidden_costs_level_std'] = self.df['hidden_costs_level'].apply(map_hidden_costs)
        print(f"[OK]Standardized hidden_costs_level")
        return self

    def standardize_cost_category(self):
        """Standardize cost_category to Free/Low-cost/Medium-cost/High-cost"""
        if 'cost_category' not in self.df.columns:
            return self

        def map_cost_category(value):
            if pd.isna(value):
                return 'Free'
            value_str = str(value).lower()

            # Free categories
            if any(x in value_str for x in ['free', 'school-based']):
                return 'Free'
            # Low cost (under $500)
            elif any(x in value_str for x in ['under-$100', '$50-$100', '$50-$200',
                                               '$25-100', 'low-cost', 'subsidized']):
                return 'Low-cost'
            # Medium cost ($500-$2000)
            elif any(x in value_str for x in ['$100-$500', '$100-500', '$500-$1000',
                                               '$300-800', '$500-1500', '$200-500']):
                return 'Medium-cost'
            # High cost ($2000+)
            elif any(x in value_str for x in ['$1000+', '$2000+', '$2000-5000',
                                               '$800-2000', '$500-2000']):
                return 'High-cost'
            # Hardware/Paid programs - map to medium by default
            elif any(x in value_str for x in ['hardware', 'paid', 'subscription']):
                return 'Medium-cost'
            else:
                return 'Free'  # Default

        self.df['cost_category_std'] = self.df['cost_category'].apply(map_cost_category)
        print(f"[OK]Standardized cost_category")
        return self

    def standardize_location_type(self):
        """Standardize location_type to Virtual/Hybrid/In-person"""
        if 'location_type' not in self.df.columns:
            return self

        def map_location(value):
            if pd.isna(value):
                return 'Virtual'
            value_str = str(value).lower()

            if 'online' in value_str or 'virtual' in value_str or 'remote' in value_str:
                return 'Virtual'
            elif 'hybrid' in value_str or 'both' in value_str:
                return 'Hybrid'
            elif 'in-person' in value_str or 'classroom' in value_str or 'campus' in value_str:
                return 'In-person'
            else:
                return 'Virtual'  # Default

        self.df['location_type_std'] = self.df['location_type'].apply(map_location)
        print(f"[OK]Standardized location_type")
        return self

    def standardize_transportation_required(self):
        """Standardize transportation_required to Yes/No/Optional"""
        if 'transportation_required' not in self.df.columns:
            return self

        def map_transportation(value):
            if pd.isna(value):
                return 'No'
            value_str = str(value).lower()

            if value_str in ['true', 'yes', '1']:
                return 'Yes'
            elif value_str in ['false', 'no', '0']:
                return 'No'
            elif 'optional' in value_str or 'varies' in value_str or 'variable' in value_str:
                return 'Optional'
            else:
                return 'No'  # Default

        self.df['transportation_required_std'] = self.df['transportation_required'].apply(map_transportation)
        print(f"[OK]Standardized transportation_required")
        return self

    def standardize_prerequisite_level(self):
        """Standardize prerequisite_level to None/Beginner/Intermediate/Advanced"""
        if 'prerequisite_level' not in self.df.columns:
            return self

        def map_prerequisite(value):
            if pd.isna(value):
                return 'None'
            value_str = str(value).lower()

            # Map to skill levels
            if 'low' in value_str or 'beginner' in value_str or 'basic' in value_str or 'any level' in value_str:
                return 'Beginner'
            elif 'medium' in value_str or 'intermediate' in value_str or 'algebra' in value_str:
                return 'Intermediate'
            elif 'high' in value_str or 'advanced' in value_str or 'very high' in value_str:
                return 'Advanced'
            elif 'variable' in value_str:
                return 'Beginner'  # Conservative default
            elif any(x in value_str for x in ['typing', 'arithmetic', 'numbers', 'multiplication']):
                return 'Beginner'
            else:
                return 'None'

        self.df['prerequisite_level_std'] = self.df['prerequisite_level'].apply(map_prerequisite)
        print(f"[OK]Standardized prerequisite_level")
        return self

    def standardize_support_level(self):
        """Standardize support_level to Low/Medium/High"""
        if 'support_level' not in self.df.columns:
            return self

        def map_support(value):
            if pd.isna(value):
                return 'Medium'
            value_str = str(value).lower()

            if 'low' in value_str:
                return 'Low'
            elif 'moderate' in value_str or 'medium' in value_str:
                return 'Medium'
            elif 'high' in value_str:
                return 'High'
            else:
                return 'Medium'

        self.df['support_level_std'] = self.df['support_level'].apply(map_support)
        print(f"[OK]Standardized support_level")
        return self

    # ===== NUMERIC EXTRACTION METHODS =====

    def extract_target_grade_numeric(self):
        """Extract numeric grade level from target_grade_standardized"""
        if 'target_grade_standardized' not in self.df.columns:
            return self

        def extract_grade_midpoint(value):
            if pd.isna(value):
                return 9.0  # Default to 9th grade
            value_str = str(value).upper()

            # Extract all numbers
            numbers = re.findall(r'\d+', value_str)

            if not numbers:
                # Handle K (kindergarten) as grade 0
                if 'K' in value_str:
                    return 0.0
                return 9.0  # Default

            # If range (e.g., "9-12"), take midpoint
            numbers = [int(n) for n in numbers]
            return np.mean(numbers)

        self.df['target_grade_numeric'] = self.df['target_grade_standardized'].apply(extract_grade_midpoint)
        print(f"[OK]Extracted numeric target_grade: mean={self.df['target_grade_numeric'].mean():.1f}")
        return self

    def extract_time_commitment_hours(self):
        """Extract numeric hours from time_commitment field"""
        if 'time_commitment' not in self.df.columns:
            return self

        def extract_hours(value):
            if pd.isna(value):
                return 5.0  # Default to 5 hours/week
            value_str = str(value).lower()

            # Handle self-paced / variable
            if 'self-paced' in value_str or 'variable' in value_str:
                return 5.0  # Assume moderate commitment

            # Extract numbers
            numbers = re.findall(r'(\d+(?:\.\d+)?)', value_str)

            if not numbers:
                return 5.0

            hours = [float(n) for n in numbers]
            avg_hours = np.mean(hours)

            # Adjust based on time unit
            if 'week' in value_str:
                if 'month' in value_str or 'weeks' in value_str or 'months' in value_str:
                    # If duration is specified, calculate total hours
                    # For now, just use the hours per week value
                    return avg_hours
                return avg_hours
            elif 'month' in value_str:
                # Convert months to weeks (assume 4 weeks/month, 5 hours/week)
                return avg_hours * 4 * 5 / 12  # Amortize over year
            elif 'day' in value_str:
                return avg_hours * 7  # Convert daily to weekly
            elif 'hour' in value_str:
                return avg_hours  # Already in hours
            elif 'minute' in value_str:
                return avg_hours / 60  # Convert to hours
            else:
                return avg_hours

        self.df['time_commitment_hours'] = self.df['time_commitment'].apply(extract_hours)
        print(f"[OK]Extracted time_commitment_hours: mean={self.df['time_commitment_hours'].mean():.1f}")
        return self

    # ===== ENCODING METHODS =====

    def encode_accessibility_features(self):
        """Encode features for Accessibility Profile clustering"""
        # Ordinal encodings
        financial_map = {'Low': 0, 'Medium': 1, 'High': 2, 'Prohibitive': 3}
        hidden_costs_map = {'None': 0, 'Low': 1, 'Medium': 2, 'High': 3}
        cost_map = {'Free': 0, 'Low-cost': 1, 'Medium-cost': 2, 'High-cost': 3}
        location_map = {'Virtual': 0, 'Hybrid': 1, 'In-person': 2}
        transport_map = {'No': 0, 'Optional': 1, 'Yes': 2}

        self.df['financial_barrier_encoded'] = self.df['financial_barrier_level_std'].map(financial_map).fillna(0)
        self.df['hidden_costs_encoded'] = self.df['hidden_costs_level_std'].map(hidden_costs_map).fillna(1)
        self.df['cost_category_encoded'] = self.df['cost_category_std'].map(cost_map).fillna(0)
        self.df['location_type_encoded'] = self.df['location_type_std'].map(location_map).fillna(0)
        self.df['transportation_encoded'] = self.df['transportation_required_std'].map(transport_map).fillna(0)

        print(f"[OK]Encoded accessibility features")
        return self

    def encode_academic_features(self):
        """Encode features for Academic Level clustering"""
        prerequisite_map = {'None': 0, 'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        support_map = {'Low': 0, 'Medium': 1, 'High': 2}

        self.df['prerequisite_encoded'] = self.df['prerequisite_level_std'].map(prerequisite_map).fillna(1)
        self.df['support_level_encoded'] = self.df['support_level_std'].map(support_map).fillna(1)

        print(f"[OK]Encoded academic features")
        return self

    def get_accessibility_features(self):
        """Get preprocessed features for Accessibility clustering"""
        features = [
            'financial_barrier_encoded',
            'hidden_costs_encoded',
            'cost_category_encoded',
            'location_type_encoded',
            'transportation_encoded'
        ]

        # Filter to reliable financial data if available
        df_filtered = self.df.copy()
        if 'financial_barrier_level_reliable' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['financial_barrier_level_reliable'] == True]
            print(f"[OK]Using {len(df_filtered)} resources with reliable financial data")

        X = df_filtered[features].values

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['accessibility'] = scaler

        return X_scaled, df_filtered.index

    def get_academic_features(self):
        """Get preprocessed features for Academic Level clustering"""
        features = [
            'prerequisite_encoded',
            'target_grade_numeric',
            'time_commitment_hours',
            'support_level_encoded'
        ]

        X = self.df[features].values

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['academic'] = scaler

        return X_scaled, self.df.index

    def get_stem_field_features(self):
        """Get preprocessed features for STEM Field clustering"""
        # One-hot encode stem_field_tier1 and category_tier1
        stem_dummies = pd.get_dummies(self.df['stem_field_tier1'], prefix='stem')
        category_dummies = pd.get_dummies(self.df['category_tier1'], prefix='cat')

        X = pd.concat([stem_dummies, category_dummies], axis=1).values

        print(f"[OK]Created {X.shape[1]} STEM field features (one-hot encoded)")
        return X, self.df.index

    def get_format_features(self):
        """Get preprocessed features for Resource Format clustering"""
        # One-hot encode category_tier1
        category_dummies = pd.get_dummies(self.df['category_tier1'], prefix='cat')

        # Add numeric features
        numeric_features = self.df[['time_commitment_hours', 'support_level_encoded']].values

        # Scale numeric features
        scaler = StandardScaler()
        numeric_scaled = scaler.fit_transform(numeric_features)
        self.scalers['format'] = scaler

        # Combine
        X = np.hstack([category_dummies.values, numeric_scaled])

        print(f"[OK]Created {X.shape[1]} format features")
        return X, self.df.index

    def run_all_preprocessing(self):
        """Run complete preprocessing pipeline"""
        print("\n" + "="*60)
        print("Running BMIS Preprocessing Pipeline")
        print("="*60)

        self.load_data()

        print("\nStandardizing features...")
        self.standardize_financial_barrier_level()
        self.standardize_hidden_costs_level()
        self.standardize_cost_category()
        self.standardize_location_type()
        self.standardize_transportation_required()
        self.standardize_prerequisite_level()
        self.standardize_support_level()

        print("\nExtracting numeric features...")
        self.extract_target_grade_numeric()
        self.extract_time_commitment_hours()

        print("\nEncoding features...")
        self.encode_accessibility_features()
        self.encode_academic_features()

        print("\n" + "="*60)
        print("Preprocessing Complete!")
        print("="*60)

        return self

    def save_preprocessors(self, output_dir='preprocessors'):
        """Save all scalers and encoders"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'{output_dir}/{name}_scaler.pkl')

        # Save the preprocessed dataframe
        self.df.to_csv(f'{output_dir}/preprocessed_data.csv', index=False)

        print(f"[OK]Saved preprocessors to {output_dir}/")
        return self


if __name__ == '__main__':
    # Test the preprocessing pipeline
    preprocessor = BMISPreprocessor()
    preprocessor.run_all_preprocessing()

    # Test each feature set
    print("\nTesting feature extraction...")
    print("-" * 60)

    X_acc, idx_acc = preprocessor.get_accessibility_features()
    print(f"Accessibility features: {X_acc.shape}")

    X_acad, idx_acad = preprocessor.get_academic_features()
    print(f"Academic features: {X_acad.shape}")

    X_stem, idx_stem = preprocessor.get_stem_field_features()
    print(f"STEM field features: {X_stem.shape}")

    X_format, idx_format = preprocessor.get_format_features()
    print(f"Format features: {X_format.shape}")

    # Save preprocessors
    preprocessor.save_preprocessors()

    print("\n[OK] All preprocessing tests passed!")
