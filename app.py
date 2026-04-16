# app.py
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Charger les variables d'environnement depuis .env
load_dotenv()

# Ajouter le chemin pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import load_and_clean_data
from src.analysis import calculate_kpis, generate_insights, create_visualizations

# ========== CONFIGURATION GEMINI ==========
try:
    import google.generativeai as genai
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        st.error("❌ Clé API Gemini manquante. Créez un fichier .env avec GEMINI_API_KEY=votre_clé")
        GEMINI_AVAILABLE = False
    else:
        genai.configure(api_key=GEMINI_API_KEY)
        
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        preferences = [
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-pro', 
            'models/gemini-pro'
        ]
        
        selected_model_name = None
        for pref in preferences:
            if pref in available_models:
                selected_model_name = pref
                break
                
        if selected_model_name:
            model = genai.GenerativeModel(selected_model_name)
            GEMINI_AVAILABLE = True
        else:
            if available_models:
                model = genai.GenerativeModel(available_models[0])
                selected_model_name = available_models[0]
                GEMINI_AVAILABLE = True
            else:
                GEMINI_AVAILABLE = False
                st.error("❌ Aucun modèle compatible trouvé pour cette clé API.")

except Exception as e:
    GEMINI_AVAILABLE = False
    st.error(f"❌ Erreur de configuration Gemini : {e}")

# ========== CONFIGURATION GROQ ==========
try:
    from groq import Groq
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        GROQ_AVAILABLE = True
    else:
        GROQ_AVAILABLE = False
        st.info("💡 Astuce : Ajoutez GROQ_API_KEY dans .env pour des recommandations IA avancées")
except ImportError:
    GROQ_AVAILABLE = False
    st.info("💡 Pour des recommandations IA, installez : pip install groq")
except Exception as e:
    GROQ_AVAILABLE = False
    st.warning(f"⚠️ Groq non disponible : {e}")

# Configuration Streamlit
st.set_page_config(
    page_title="Social Media Intelligence - Agence X",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    .insight-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FF4B4B;
    }
    .generated-post {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        font-family: monospace;
        margin: 1rem 0;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    .stButton button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #ff6b6b;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .recommendation-card {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("<h1 class='main-header'> Social Media Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Agence X - Performance, Engagement & IA Générative (Gemini + Groq)</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Aller à :", [
    "🏠 Dashboard", 
    "📈 Analyse Détaillée", 
    "🤖 Générateur IA (Gemini)", 
    "📋 Insights Business",
    "💬 Analyse de Sentiment"
])

# Statut des IA dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Modèles IA")
if GEMINI_AVAILABLE:
    st.sidebar.success("✅ Gemini connecté")
else:
    st.sidebar.error("❌ Gemini non disponible")

if GROQ_AVAILABLE:
    st.sidebar.success("✅ Groq connecté")
else:
    st.sidebar.info("⚡ Groq optionnel")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 À propos")
st.sidebar.info(
    "Cette application analyse les performances des réseaux sociaux "
    "et utilise **Gemini** pour générer du contenu et **Groq** pour des recommandations avancées."
)

# Chargement des données
@st.cache_data
def load_all_data():
    try:
        df = load_and_clean_data('data/Viral_Social_Media_Trends.csv')
        kpis, df = calculate_kpis(df)
        insights = generate_insights(df)
        return df, kpis, insights
    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        return pd.DataFrame(), {}, []

with st.spinner("📥 Chargement et analyse des données en cours..."):
    df, kpis, insights = load_all_data()

# ========== FONCTION GEMINI ==========
def generate_with_gemini(platform, topic, tone, objective, include_hashtags, include_cta, post_length, context_data=""):
    """Génère un post avec l'API Gemini de Google"""
    
    if not GEMINI_AVAILABLE:
        return None, "Gemini non disponible. Vérifiez votre clé API."
    
    length_guide = {
        "Court": "50-100 caractères",
        "Moyen": "150-250 caractères", 
        "Long": "300-500 caractères"
    }
    
    prompt = f"""
Tu es un expert en social media marketing. Génère un post pour {platform}.

SUJET: "{topic}"
TON: {tone}
OBJECTIF: {objective}
LONGUEUR: {post_length} ({length_guide.get(post_length, '200-300 caractères')})
HASHTAGS: {'Oui, inclus 3-5 hashtags pertinents' if include_hashtags else 'Non'}
APPEL A L'ACTION: {'Oui, inclus un CTA engageant' if include_cta else 'Non'}

{context_data}

CONSIGNES IMPORTANTES:
1. Adapte le langage à la plateforme {platform}
2. Utilise des émojis de façon naturelle
3. Sois engageant et authentique
4. Structure le post pour qu'il soit facile à lire
5. Ne dépasse pas la longueur demandée

Génère UNIQUEMENT le contenu du post, sans explications supplémentaires.
"""

    try:
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)

# ========== FONCTION GROQ POUR RECOMMANDATIONS ==========
def generate_recommendations_with_groq(kpis, insights):
    """Génère des recommandations professionnelles avec Groq"""
    
    if not GROQ_AVAILABLE:
        return None, None
    
    prompt = f"""
Tu es un expert en stratégie social media pour une agence de communication.

Voici les données analysées à partir de {kpis.get('total_posts', 0)} posts :

KPIS :
- Total posts analysés : {kpis.get('total_posts', 0)}
- Engagement total : {kpis.get('total_engagement', 0):,}
- Engagement moyen par post : {kpis.get('avg_engagement', 0):.0f}
- Meilleure plateforme : {kpis.get('best_platform', 'N/A')}
- Plateforme moins performante : {kpis.get('worst_platform', 'N/A')}
- Meilleur type de contenu : {kpis.get('best_content_type', 'N/A')}

INSIGHTS GÉNÉRÉS :
{chr(10).join(['- ' + i for i in insights])}

Génère un rapport de recommandations professionnelles, structuré en :
- 3 points "À FAIRE" (actions concrètes basées sur les données)
- 2 points "À ÉVITER" (erreurs à ne pas commettre)

Sois précis, actionnable, et basé uniquement sur les données fournies. Utilise des émojis pertinents.
"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un expert en stratégie social media. Réponds de manière professionnelle et concise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )
        
        recommendations_text = response.choices[0].message.content
        
        # Parser la réponse
        faire = []
        eviter = []
        current_section = None
        
        for line in recommendations_text.split('\n'):
            line = line.strip()
            if 'À FAIRE' in line.upper() or 'A FAIRE' in line.upper():
                current_section = 'faire'
            elif 'À ÉVITER' in line.upper() or 'A EVITER' in line.upper():
                current_section = 'eviter'
            elif line.startswith('-') or line.startswith('•') or (line and line[0].isdigit() and '.' in line[:3]):
                clean_line = line.lstrip('-•0123456789. ')
                if current_section == 'faire' and clean_line:
                    faire.append(clean_line)
                elif current_section == 'eviter' and clean_line:
                    eviter.append(clean_line)
        
        if not faire and not eviter:
            all_lines = [l for l in recommendations_text.split('\n') if l.strip() and not l.strip().startswith('**')]
            faire = all_lines[:3] if len(all_lines) >= 3 else all_lines[:2]
            eviter = all_lines[-2:] if len(all_lines) >= 5 else all_lines[-1:]
        
        return faire, eviter
        
    except Exception as e:
        st.error(f"❌ Erreur Groq : {e}")
        return None, None

# ========== FONCTIONS POUR ANALYSE DE SENTIMENT ==========
@st.cache_data
def load_sentiment_data():
    """Charge les données analysées par le modèle BERT"""
    paths_to_try = [
        "data/french_opinions_analyzed.csv",  # NOUVEAU - Posts français analysés
        "data/raw_data_analyzed.csv",         # Ancien - Posts Reddit analysés
        "data/analyzed_data.csv",             # Ancien - Fallback
        "data/french_opinions_analyzed.json"
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_json(path)
            
            if 'sentiment' in df.columns:
                return df, path
    
    return None, None

def get_sentiment_stats(df):
    """Calcule les statistiques de sentiment"""
    total = len(df)
    stats = {}
    for sentiment in ['positive', 'neutral', 'negative']:
        count = len(df[df['sentiment'] == sentiment])
        stats[sentiment] = {
            'count': count,
            'percentage': (count / total * 100) if total > 0 else 0
        }
    stats['total'] = total
    return stats

# ================================
# PAGE 1 : DASHBOARD
# ================================
if page == "🏠 Dashboard":
    st.header("📊 Indicateurs clés de performance")
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total des posts", f"{kpis.get('total_posts', len(df)):,}")
        with col2:
            st.metric("❤️ Engagement total", f"{kpis.get('total_engagement', 0):,}")
        with col3:
            st.metric("📈 Engagement moyen", f"{kpis.get('avg_engagement', 0):.0f}")
        with col4:
            st.metric("📱 Plateformes", kpis.get('total_platforms', 0))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Engagement par plateforme")
            fig = create_visualizations(df)
            st.pyplot(fig)
        
        with col2:
            st.subheader("🏆 Top 5 des meilleurs posts")
            if 'total_engagement' in df.columns:
                top_posts = df.nlargest(5, 'total_engagement')
                for i, (idx, row) in enumerate(top_posts.iterrows(), 1):
                    platform = row.get('platform', 'Inconnue')
                    engagement = row.get('total_engagement', 0)
                    content = str(row.get('content', ''))[:80]
                    st.markdown(f"""
                    <div style='background-color:#f0f2f6; padding:10px; border-radius:8px; margin:8px 0;'>
                        <b>#{i}</b> 📱 <b>{platform}</b> | ❤️ <b>{engagement:,}</b> engagements<br>
                        <small style='color:#666;'>{content}...</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        with st.expander("🔍 Voir l'aperçu des données"):
            st.dataframe(df.head(20), use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger les données nettoyées (CSV)",
                data=csv,
                file_name=f'social_media_data_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
    else:
        st.warning("⚠️ Aucune donnée chargée. Vérifiez que 'data/Viral_Social_Media_Trends.csv' existe.")

# ================================
# PAGE 2 : ANALYSE DÉTAILLÉE
# ================================
elif page == "📈 Analyse Détaillée":
    st.header("📊 Analyse détaillée des données")
    
    if not df.empty:
        st.subheader("📱 Performance par plateforme")
        if 'platform' in df.columns and 'total_engagement' in df.columns:
            platform_stats = df.groupby('platform').agg({
                'total_engagement': ['mean', 'sum', 'count']
            }).round(2)
            platform_stats.columns = ['Engagement moyen', 'Engagement total', 'Nombre de posts']
            platform_stats = platform_stats.sort_values('Engagement moyen', ascending=False)
            st.dataframe(platform_stats, use_container_width=True)
        
        st.subheader("📈 Statistiques descriptives")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        st.subheader("📋 Aperçu complet des données")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Aucune donnée disponible")

# ================================
# PAGE 3 : GÉNÉRATEUR IA GEMINI
# ================================
elif page == "🤖 Générateur IA (Gemini)":
    st.header("🤖 Générateur de contenu avec Google Gemini")
    
    st.markdown("""
    <div style='background-color:#e8f4f8; padding:15px; border-radius:10px; margin-bottom:20px;'>
    💡 <b>Comment ça marche ?</b><br>
    L'IA <b>Gemini de Google</b> génère du contenu personnalisé pour vos réseaux sociaux
    en fonction de vos paramètres. Le modèle analyse les tendances et propose
    des posts optimisés pour maximiser l'engagement.
    </div>
    """, unsafe_allow_html=True)
    
    if not GEMINI_AVAILABLE:
        st.error("""
        ### ❌ Gemini API non configurée
        
        1. Créez un fichier `.env` à la racine du projet
        2. Ajoutez : `GEMINI_API_KEY=votre_clé_api`
        3. Obtenez une clé gratuite sur https://aistudio.google.com/
        """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎨 Paramètres du post")
        platform = st.selectbox("📱 Plateforme cible", ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok", "YouTube"])
        topic = st.text_input("✏️ Sujet du post", value="Découvrez nos services de communication")
        tone = st.selectbox("🎭 Ton du message", ["Professionnel", "Décontracté", "Urgent", "Inspirant", "Humoristique", "Émotionnel"])
        objective = st.selectbox("🎯 Objectif du post", ["Notoriété", "Engagement", "Conversion", "Information", "Viral"])
    
    with col2:
        st.subheader("⚙️ Options avancées")
        include_hashtags = st.toggle("#️⃣ Ajouter des hashtags", value=True)
        include_cta = st.toggle("🔘 Ajouter un appel à l'action (CTA)", value=True)
        post_length = st.select_slider("📏 Longueur du post", options=["Court", "Moyen", "Long"], value="Moyen")
        
        st.markdown("---")
        st.markdown("💡 **Inspiration depuis vos données**")
        
        if not df.empty and 'total_engagement' in df.columns:
            best_post = df.nlargest(1, 'total_engagement')
            if 'content' in best_post.columns:
                best_engagement = best_post['total_engagement'].values[0]
                st.info(f"🏆 Le post le plus performant a généré **{best_engagement:,}** engagements.")
    
    st.markdown("---")
    
    if st.button("🚀 Générer le post avec Gemini", type="primary", use_container_width=True):
        with st.spinner("🧠 Gemini analyse et génère votre contenu..."):
            context = ""
            if not df.empty and 'total_engagement' in df.columns:
                top_post = df.nlargest(1, 'total_engagement')
                if 'content' in top_post.columns:
                    context = f'INSPIRATION : "{top_post["content"].values[0][:300]}"'
            
            generated_post, error = generate_with_gemini(
                platform, topic, tone, objective,
                include_hashtags, include_cta, post_length, context
            )
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Post généré avec succès par Gemini !")
                st.markdown("---")
                st.subheader("📝 Votre post généré par IA :")
                st.markdown(f"<div class='generated-post'>{generated_post.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.code(generated_post, language="markdown")
                st.download_button(
                    label="💾 Télécharger le post (TXT)",
                    data=generated_post,
                    file_name=f"post_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

# ================================
# PAGE 4 : INSIGHTS BUSINESS AVEC GROQ
# ================================
elif page == "📋 Insights Business":
    st.header("💡 Insights et recommandations stratégiques")
    
    if insights:
        st.subheader("🎯 Insights générés par l'analyse des données")
        for insight in insights:
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Aucun insight disponible")
    
    st.subheader("🤖 Recommandations IA (Groq)")
    
    if st.button("📊 Générer des recommandations personnalisées avec IA", type="primary"):
        with st.spinner("🤖 L'IA analyse vos données et génère des recommandations..."):
            faire, eviter = generate_recommendations_with_groq(kpis, insights)
            
            if faire and eviter:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ À FAIRE")
                    for rec in faire:
                        st.markdown(f"- {rec}")
                with col2:
                    st.markdown("### ❌ À ÉVITER")
                    for rec in eviter:
                        st.markdown(f"- {rec}")
            else:
                st.warning("⚠️ Mode démo - Recommandations génériques")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ À FAIRE")
                    st.markdown("- 📱 Publier sur la plateforme la plus performante")
                    st.markdown("- #️⃣ Utiliser 3 à 5 hashtags par post")
                    st.markdown("- ⏰ Poster entre 18h et 20h en semaine")
                with col2:
                    st.markdown("### ❌ À ÉVITER")
                    st.markdown("- 📝 Posts trop longs (>300 caractères)")
                    st.markdown("- 🔢 Trop de hashtags (>10)")
                    st.markdown("- 🚫 Publier sans appel à l'action")
    else:
        st.info("💡 Cliquez sur le bouton ci-dessus pour générer des recommandations personnalisées basées sur vos données.")
    
    st.markdown("---")
    st.subheader("📄 Export du rapport d'analyse")
    
    if st.button("📊 Générer le rapport complet", type="secondary"):
        report_text = f"""
RAPPORT D'ANALYSE SOCIAL MEDIA
================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

KPIS PRINCIPAUX:
- Total posts: {kpis.get('total_posts', 0)}
- Engagement total: {kpis.get('total_engagement', 0):,}
- Engagement moyen: {kpis.get('avg_engagement', 0):.0f}
- Meilleure plateforme: {kpis.get('best_platform', 'N/A')}

INSIGHTS:
{chr(10).join(['- ' + i for i in insights])}
"""
        st.download_button(
            label="📥 Télécharger le rapport (TXT)",
            data=report_text,
            file_name=f"rapport_social_media_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )

# ================================
# ================================
# PAGE 5 : ANALYSE DE SENTIMENT (AVIS FRANÇAIS)
# ================================
elif page == "💬 Analyse de Sentiment":
    st.header("💬 Analyse de Sentiment avec CamemBERT")
    
    st.markdown("""
    <div style='background-color:#e8f4f8; padding:15px; border-radius:10px; margin-bottom:20px;'>
    <b>🤖 Modèle CamemBERT (BERT français)</b><br>
    Ce modèle analyse automatiquement le sentiment des textes en français avec une précision de <b>95.71%</b>.<br>
    Les données analysées proviennent des posts Reddit collectés et filtrés en français.
    </div>
    """, unsafe_allow_html=True)
    
    # Charger les données de sentiment
    sentiment_df, source_path = load_sentiment_data()
    
    if sentiment_df is not None:
        st.caption(f"📁 Source des données : `{source_path}`")
        
        # ========== STATISTIQUES GLOBALES ==========
        st.subheader("📊 Statistiques globales")
        
        stats = get_sentiment_stats(sentiment_df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Total posts français", f"{stats['total']:,}")
        with col2:
            st.metric("😊 Positifs", f"{stats['positive']['count']:,}", 
                     delta=f"{stats['positive']['percentage']:.1f}%")
        with col3:
            st.metric("😐 Neutres", f"{stats['neutral']['count']:,}",
                     delta=f"{stats['neutral']['percentage']:.1f}%")
        with col4:
            st.metric("😞 Négatifs", f"{stats['negative']['count']:,}",
                     delta=f"{stats['negative']['percentage']:.1f}%", delta_color="inverse")
        
        st.markdown("---")
        
        # ========== VISUALISATIONS ==========
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribution des sentiments")
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sentiments = ['positive', 'neutral', 'negative']
            counts = [stats[s]['count'] for s in sentiments]
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            labels = ['😊 Positif', '😐 Neutre', '😞 Négatif']
            
            bars = ax.bar(labels, counts, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_title('Nombre de posts par sentiment', fontsize=14, fontweight='bold')
            ax.set_ylabel('Nombre de posts')
            ax.set_ylim(0, max(counts) * 1.1)
            
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                       str(count), ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig)
        
        with col2:
            st.subheader("🥧 Proportion des sentiments")
            
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors,
                   explode=[0.05, 0.05, 0.05], shadow=True, textprops={'fontsize': 12})
            ax2.set_title('Répartition des sentiments', fontsize=14, fontweight='bold')
            st.pyplot(fig2)
        
        # ========== AVIS PERTINENTS (BONUS) ==========
        st.markdown("---")
        st.subheader("💬 Avis pertinents (≥ 10 likes)")
        
        # Filtrer les avis avec assez d'engagement
        opinions_df = sentiment_df[sentiment_df['likes'] >= 10].copy()
        
        if not opinions_df.empty:
            tab1, tab2, tab3 = st.tabs(["👍 Avis Positifs", "😐 Avis Neutres", "👎 Avis Négatifs"])
            
            with tab1:
                positive_opinions = opinions_df[opinions_df['sentiment'] == 'positive'].head(10)
                if not positive_opinions.empty:
                    for _, row in positive_opinions.iterrows():
                        content = str(row['content'])[:150]
                        st.markdown(f"""
                        <div style='background-color:#e8f8e8; padding:10px; border-radius:8px; margin:8px 0; border-left:4px solid #2ecc71;'>
                            <b>💬 {content}...</b><br>
                            <small>👍 {row['likes']} likes | 💬 {row['comments']} commentaires | 📁 r/{row.get('subreddit', '?')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aucun avis positif avec ≥ 10 likes")
            
            with tab2:
                neutral_opinions = opinions_df[opinions_df['sentiment'] == 'neutral'].head(10)
                if not neutral_opinions.empty:
                    for _, row in neutral_opinions.iterrows():
                        content = str(row['content'])[:150]
                        st.markdown(f"""
                        <div style='background-color:#fff8e8; padding:10px; border-radius:8px; margin:8px 0; border-left:4px solid #f39c12;'>
                            <b>💬 {content}...</b><br>
                            <small>👍 {row['likes']} likes | 💬 {row['comments']} commentaires | 📁 r/{row.get('subreddit', '?')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aucun avis neutre avec ≥ 10 likes")
            
            with tab3:
                negative_opinions = opinions_df[opinions_df['sentiment'] == 'negative'].head(10)
                if not negative_opinions.empty:
                    for _, row in negative_opinions.iterrows():
                        content = str(row['content'])[:150]
                        st.markdown(f"""
                        <div style='background-color:#ffe8e8; padding:10px; border-radius:8px; margin:8px 0; border-left:4px solid #e74c3c;'>
                            <b>💬 {content}...</b><br>
                            <small>👍 {row['likes']} likes | 💬 {row['comments']} commentaires | 📁 r/{row.get('subreddit', '?')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aucun avis négatif avec ≥ 10 likes")
        else:
            st.info("ℹ️ Aucun avis avec au moins 10 likes trouvé")
        
        # ========== TABLEAU DES POSTS PAR SENTIMENT ==========
        st.markdown("---")
        st.subheader("📋 Tous les posts analysés")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_sentiment = st.selectbox(
                "Filtrer par sentiment",
                ["Tous", "positive", "neutral", "negative"],
                format_func=lambda x: {"Tous": "📊 Tous", "positive": "😊 Positifs", 
                                       "neutral": "😐 Neutres", "negative": "😞 Négatifs"}.get(x, x)
            )
        
        with col2:
            sort_options = [col for col in ['likes', 'comments', 'upvote_ratio'] if col in sentiment_df.columns]
            sort_by = st.selectbox("Trier par", sort_options if sort_options else ["likes"])
        
        if selected_sentiment != "Tous":
            filtered_df = sentiment_df[sentiment_df['sentiment'] == selected_sentiment]
        else:
            filtered_df = sentiment_df
        
        filtered_df = filtered_df.sort_values(sort_by, ascending=False)
        
        display_cols = ['content', 'sentiment', 'likes', 'comments']
        if 'upvote_ratio' in filtered_df.columns:
            display_cols.append('upvote_ratio')
        if 'subreddit' in filtered_df.columns:
            display_cols.append('subreddit')
        
        st.dataframe(filtered_df[display_cols].head(50), use_container_width=True)
        
        # ========== EXPORT ==========
        st.markdown("---")
        st.subheader("📄 Export des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = sentiment_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger toutes les données (CSV)",
                data=csv_data,
                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        
        with col2:
            if not opinions_df.empty:
                csv_opinions = opinions_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger les avis pertinents (CSV)",
                    data=csv_opinions,
                    file_name=f"french_opinions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
    
    else:
        # Pas de données disponibles
        st.warning("⚠️ Aucune donnée d'analyse de sentiment disponible.")
        
        st.info("""
        ### Pour analyser les sentiments des posts Reddit français :
        
        1. Assurez-vous que le modèle BERT est présent dans `./sentiment_model/`
        2. Lancez la collecte et l'analyse :
        ```bash
        python analyze_sentiment.py --limit 100 """)

# Pied de page
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px;'>"
    "© 2025 Agence X - Social Media Intelligence | Propulsé par Google Gemini & Groq AI"
    "</p>",
    unsafe_allow_html=True
)