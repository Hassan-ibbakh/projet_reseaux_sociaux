# src/analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.preprocessing import load_and_clean_data

def calculate_kpis(df):
    """Calcule des indicateurs de performance clés"""
    kpis = {}
    
    if 'total_engagement' in df.columns:
        kpis['total_engagement'] = int(df['total_engagement'].sum())
        kpis['avg_engagement'] = float(df['total_engagement'].mean())
        kpis['max_engagement'] = int(df['total_engagement'].max())
        kpis['median_engagement'] = float(df['total_engagement'].median())
        kpis['min_engagement'] = int(df['total_engagement'].min())
    
    if 'platform' in df.columns and 'total_engagement' in df.columns:
        platform_eng = df.groupby('platform')['total_engagement'].mean()
        kpis['engagement_by_platform'] = platform_eng.to_dict()
        kpis['best_platform'] = platform_eng.idxmax()
        kpis['worst_platform'] = platform_eng.idxmin()
    
    if 'content_type' in df.columns and 'total_engagement' in df.columns:
        content_eng = df.groupby('content_type')['total_engagement'].mean()
        kpis['best_content_type'] = content_eng.idxmax() if len(content_eng) > 0 else "N/A"
    
    kpis['total_posts'] = len(df)
    kpis['total_platforms'] = df['platform'].nunique() if 'platform' in df.columns else 0
    
    return kpis, df

def generate_insights(df):
    """Génère des insights business exploitables"""
    insights = []
    
    if 'platform' in df.columns and 'total_engagement' in df.columns:
        platform_stats = df.groupby('platform')['total_engagement'].mean().sort_values(ascending=False)
        best = platform_stats.index[0]
        best_value = platform_stats.iloc[0]
        insights.append(f"📱 La plateforme la plus engageante est **{best}** avec {best_value:.0f} interactions en moyenne.")
        
        if len(platform_stats) > 1:
            worst = platform_stats.index[-1]
            worst_value = platform_stats.iloc[-1]
            insights.append(f"⚠️ La plateforme la moins performante est **{worst}** ({worst_value:.0f} interactions).")
    
    if 'total_engagement' in df.columns:
        insights.append(f"📊 **Engagement total** : {df['total_engagement'].sum():,.0f} interactions")
        insights.append(f"📈 **Engagement moyen** : {df['total_engagement'].mean():.0f} par post")
    
    if 'content_type' in df.columns and 'total_engagement' in df.columns:
        best_content = df.groupby('content_type')['total_engagement'].mean().idxmax()
        insights.append(f"🎬 Le type de contenu qui fonctionne le mieux : **{best_content}**")
    
    # Insight sur la corrélation likes/shares
    if 'likes' in df.columns and 'shares' in df.columns:
        corr = df['likes'].corr(df['shares'])
        if corr > 0.5:
            insights.append(f"🔄 Forte corrélation ({corr:.2f}) entre les likes et les partages")
    
    insights.append(f"📝 **Volume analysé** : {len(df)} posts")
    
    return insights

def create_visualizations(df):
    """Crée des visualisations"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    if 'platform' in df.columns and 'total_engagement' in df.columns:
        platform_eng = df.groupby('platform')['total_engagement'].mean().sort_values()
        platform_eng.plot(kind='barh', ax=axes[0], color='skyblue', edgecolor='black')
        axes[0].set_title('Engagement moyen par plateforme', fontsize=12)
        axes[0].set_xlabel('Engagement moyen')
        axes[0].set_ylabel('Plateforme')
    
    if 'total_engagement' in df.columns:
        df['total_engagement'].hist(bins=30, ax=axes[1], color='salmon', edgecolor='black')
        axes[1].set_title('Distribution de l\'engagement', fontsize=12)
        axes[1].set_xlabel('Engagement')
        axes[1].set_ylabel('Nombre de posts')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    df = load_and_clean_data('data/raw_data.csv')
    kpis, df = calculate_kpis(df)
    insights = generate_insights(df)
    
    print("\n=== KPIs ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")
    
    print("\n=== INSIGHTS ===")
    for i in insights:
        print(f"- {i}")