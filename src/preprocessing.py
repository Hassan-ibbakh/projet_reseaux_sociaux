# src/preprocessing.py
import pandas as pd
import numpy as np

def load_and_clean_data(filepath):
    """Charge et nettoie les données"""
    
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
        return pd.DataFrame()
    
    print(f"📂 Fichier chargé : {filepath}")
    print(f"📊 Forme initiale : {df.shape}")
    
    # 1. Nettoyer les noms de colonnes
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # 2. Supprimer les doublons
    df = df.drop_duplicates()
    
    # 3. Remplacer les valeurs manquantes 
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("inconnu")
    
    # 4. Supprimer les colonnes à grandes valeurs
    columns_to_drop = []
    for col in df.columns:
        if col in ['views', 'reach', 'impressions', 'view_count', 'impression_count', 'followers', 'subscribers']:
            columns_to_drop.append(col)
    
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        print(f"🗑️ Colonnes supprimées : {columns_to_drop}")
    
    # 5. Créer l'engagement
    if 'likes' in df.columns and 'comments' in df.columns and 'shares' in df.columns:
        # Conversion sécurisée en nombres
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0)
        df['shares'] = pd.to_numeric(df['shares'], errors='coerce').fillna(0)
        df['total_engagement'] = df['likes'] + df['comments'] + df['shares']
        print(f"📊 Engagement calculé = likes + comments + shares")
    elif 'likes' in df.columns and 'comments' in df.columns:
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0)
        df['total_engagement'] = df['likes'] + df['comments']
    elif 'likes' in df.columns:
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['total_engagement'] = df['likes']
    else:
        df['total_engagement'] = 1
    
    # Afficher les stats avant filtrage
    if 'total_engagement' in df.columns and len(df) > 0:
        print(f"\n📊 STATS AVANT FILTRAGE :")
        print(f"   Min: {df['total_engagement'].min():.0f}")
        print(f"   Max: {df['total_engagement'].max():.0f}")
        print(f"   Moyenne: {df['total_engagement'].mean():.0f}")
        print(f"   Médiane: {df['total_engagement'].median():.0f}")
    
    # 6. FILTRAGE ADAPTÉ (seuil beaucoup plus haut pour votre dataset)
    if 'total_engagement' in df.columns and len(df) > 0:
        before = len(df)
        
        # Utiliser le percentile 99 au lieu d'un seuil fixe
        upper_bound = df['total_engagement'].quantile(0.99)
        df = df[df['total_engagement'] <= upper_bound]
        after_filter = len(df)
        
        print(f"\n🔍 FILTRAGE :")
        print(f"   Seuil utilisé (percentile 99%): {upper_bound:.0f}")
        print(f"   Posts supprimés: {before - after_filter}")
        print(f"   Posts conservés: {after_filter}")
    
    # 7. Normalisation des plateformes
    if 'platform' in df.columns and len(df) > 0:
        platform_mapping = {
            'instagram': 'Instagram',
            'facebook': 'Facebook', 
            'twitter': 'Twitter',
            'x': 'Twitter',
            'linkedin': 'LinkedIn',
            'tiktok': 'TikTok',
            'youtube': 'YouTube'
        }
        df['platform'] = df['platform'].str.lower().map(platform_mapping).fillna(df['platform'])
        print(f"📱 Plateformes détectées : {df['platform'].unique().tolist()}")
    
    # 8. Convertir en int à la fin (après tous les traitements)
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].fillna(0).astype(int)
    
    print(f"\n✅ Nettoyage terminé - Forme finale : {df.shape}")
    
    if len(df) > 0 and 'total_engagement' in df.columns:
        print(f"\n📊 STATS APRÈS FILTRAGE :")
        print(f"   Min: {df['total_engagement'].min():.0f}")
        print(f"   Max: {df['total_engagement'].max():.0f}")
        print(f"   Moyenne: {df['total_engagement'].mean():.0f}")
        print(f"   Engagement total: {df['total_engagement'].sum():,.0f}")
    
    return df

if __name__ == "__main__":
    df = load_and_clean_data('data/raw_data.csv')
    if not df.empty:
        print(f"\n✅ Données prêtes : {len(df)} posts analysés")
    else:
        print("❌ Aucune donnée chargée")