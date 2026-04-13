# src/ai_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train_engagement_model(features_path='data/features_data.csv'):
    """Entraîne un modèle de prédiction d'engagement"""
    df = pd.read_csv(features_path)
    
    # Définir la cible (engagement total)
    target_col = 'total_engagement'
    if target_col not in df.columns:
        # Alternative : créer une colonne d'engagement si elle n'existe pas
        df['total_engagement'] = df['likes'] + df['shares'] + df['comments']
    
    # Sélectionner les features numériques
    exclude_cols = [target_col, 'post_date', 'content', 'hashtag']
    feature_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64'] and col not in exclude_cols]
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Modèle
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Prédictions et évaluation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"📊 Performance du modèle :")
    print(f"   MAE : {mae:.2f}")
    print(f"   R²  : {r2:.2f}")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\n🔍 Top 5 features importantes :")
    print(importance.head())
    
    # Sauvegarde
    joblib.dump(model, 'models/engagement_model.pkl')
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    
    return model, mae, r2

def predict_engagement(new_data, model_path='models/engagement_model.pkl'):
    """Prédit l'engagement pour de nouvelles données"""
    model = joblib.load(model_path)
    feature_cols = joblib.load('models/feature_columns.pkl')
    
    # S'assurer que new_data a les bonnes colonnes
    X_new = new_data[feature_cols]
    predictions = model.predict(X_new)
    
    return predictions

if __name__ == "__main__":
    train_engagement_model()