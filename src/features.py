# src/features.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def create_features(df):
    """Crée des features pour le modèle d'IA"""
    df_features = df.copy()
    
    # 1. Encodage des variables catégorielles
    categorical_cols = ['platform', 'content_type', 'region']
    for col in categorical_cols:
        if col in df_features.columns:
            le = LabelEncoder()
            df_features[f'{col}_encoded'] = le.fit_transform(df_features[col].astype(str))
    
    # 2. Features temporelles (si date disponible)
    if 'post_date' in df_features.columns:
        df_features['post_date'] = pd.to_datetime(df_features['post_date'])
        df_features['day_of_week'] = df_features['post_date'].dt.dayofweek
        df_features['month'] = df_features['post_date'].dt.month
        df_features['hour'] = df_features['post_date'].dt.hour
    
    # 3. Longueur du contenu (si disponible)
    if 'content' in df_features.columns:
        df_features['content_length'] = df_features['content'].str.len()
    
    # 4. Nombre de hashtags (si colonne hashtag existe)
    if 'hashtag' in df_features.columns:
        df_features['num_hashtags'] = df_features['hashtag'].str.count('#')
    
    return df_features

if __name__ == "__main__":
    df = pd.read_csv('data/cleaned_data.csv')
    df_feat = create_features(df)
    df_feat.to_csv('data/features_data.csv', index=False)
    print("✅ Features créées")