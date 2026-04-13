# app.py
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Ajouter le chemin pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import load_and_clean_data
from src.analysis import calculate_kpis, generate_insights, create_visualizations

# ========== CONFIGURATION GEMINI ==========
# ========== CONFIGURATION GEMINI OPTIMISÉE ==========
try:
    import google.generativeai as genai
    
    # Clé API
    GEMINI_API_KEY = "AIzaSyCk7kRGdi6oFCaYH-mV6JUK_8srrnFmITg"
    genai.configure(api_key=GEMINI_API_KEY)
    
    # --- TEST DE CONNEXION DYNAMIQUE ---
    # On cherche quel modèle est disponible pour votre clé
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    # Ordre de préférence des modèles
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
        # Si aucun dans la liste, on prend le premier disponible
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
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
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
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("<h1 class='main-header'>📱 Social Media Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Agence X - Performance, Engagement & IA Générative (Gemini)</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Aller à :", [
    "🏠 Dashboard", 
    "📈 Analyse Détaillée", 
    "🤖 Générateur IA (Gemini)", 
    "📋 Insights Business"
])

# Statut Gemini dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Modèle IA")
if GEMINI_AVAILABLE:
    st.sidebar.success(f"✅ Connecté")
    # Affiche le nom du modèle utilisé (utile pour le debug)
    st.sidebar.caption(f"Utilise : {selected_model_name}") 
else:
    st.sidebar.error("❌ Gemini non disponible")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 À propos")
st.sidebar.info(
    "Cette application analyse les performances des réseaux sociaux "
    "et utilise **Gemini (Google)** pour générer du contenu optimisé."
)

# Chargement des données
@st.cache_data
def load_all_data():
    try:
        df = load_and_clean_data('data/raw_data.csv')
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
        st.warning("⚠️ Aucune donnée chargée. Vérifiez que 'data/raw_data.csv' existe.")

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
        
        1. Obtenez une clé API gratuite sur https://aistudio.google.com/
        2. Installez : `pip install google-generativeai`
        3. Remplacez `GEMINI_API_KEY` par votre clé
        """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎨 Paramètres du post")
        
        platform = st.selectbox(
            "📱 Plateforme cible",
            ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok", "YouTube"],
            help="Choisissez la plateforme pour laquelle générer le contenu"
        )
        
        topic = st.text_input(
            "✏️ Sujet du post",
            value="Découvrez nos services de communication",
            help="Entrez le thème principal de votre post"
        )
        
        tone = st.selectbox(
            "🎭 Ton du message",
            ["Professionnel", "Décontracté", "Urgent", "Inspirant", "Humoristique", "Émotionnel"],
            help="Le style d'écriture du post"
        )
        
        objective = st.selectbox(
            "🎯 Objectif du post",
            ["Notoriété", "Engagement", "Conversion", "Information", "Viral"],
            help="L'objectif marketing du post"
        )
    
    with col2:
        st.subheader("⚙️ Options avancées")
        
        include_hashtags = st.toggle("#️⃣ Ajouter des hashtags", value=True)
        include_cta = st.toggle("🔘 Ajouter un appel à l'action (CTA)", value=True)
        
        post_length = st.select_slider(
            "📏 Longueur du post",
            options=["Court", "Moyen", "Long"],
            value="Moyen"
        )
        
        st.markdown("---")
        st.markdown("💡 **Inspiration depuis vos données**")
        
        if not df.empty and 'total_engagement' in df.columns:
            best_post = df.nlargest(1, 'total_engagement')
            if 'content' in best_post.columns:
                best_content = str(best_post['content'].values[0])[:200]
                best_engagement = best_post['total_engagement'].values[0]
                st.info(f"🏆 Le post le plus performant a généré **{best_engagement:,}** engagements.")
                with st.expander("📖 Voir le post original"):
                    st.write(best_content)
    
    st.markdown("---")
    
    if st.button("🚀 Générer le post avec Gemini", type="primary", use_container_width=True):
        with st.spinner("🧠 Gemini analyse et génère votre contenu..."):
            
            # Préparer le contexte depuis les données
            context = ""
            if not df.empty and 'total_engagement' in df.columns:
                top_post = df.nlargest(1, 'total_engagement')
                if 'content' in top_post.columns:
                    context = f"""
                    INSPIRATION (post qui a bien fonctionné dans vos données) :
                    "{top_post['content'].values[0][:300]}"
                    """
            
            # Génération
            generated_post, error = generate_with_gemini(
                platform=platform,
                topic=topic,
                tone=tone,
                objective=objective,
                include_hashtags=include_hashtags,
                include_cta=include_cta,
                post_length=post_length,
                context_data=context
            )
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Post généré avec succès par Gemini !")
                
                st.markdown("---")
                st.subheader("📝 Votre post généré par IA :")
                
                st.markdown(f"""
                <div class='generated-post'>
                    <b>📱 {platform}</b> | <b>🎭 {tone}</b> | <b>🎯 {objective}</b><br>
                    <hr style='margin: 10px 0;'>
                    {generated_post.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Code pour copier
                st.code(generated_post, language="markdown")
                
                # Bouton de téléchargement
                st.download_button(
                    label="💾 Télécharger le post (TXT)",
                    data=generated_post,
                    file_name=f"post_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

# ================================
# PAGE 4 : INSIGHTS BUSINESS
# ================================
elif page == "📋 Insights Business":
    st.header("💡 Insights et recommandations stratégiques")
    
    if insights:
        st.subheader("🎯 Insights générés par l'analyse des données")
        for insight in insights:
            st.markdown(f"""
            <div class='insight-card'>
                {insight}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Aucun insight disponible")
    
    st.subheader("📋 Recommandations pour l'agence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ À FAIRE
        - 📱 Publier sur la plateforme la plus performante
        - #️⃣ Utiliser 3 à 5 hashtags par post
        - ⏰ Poster entre 18h et 20h en semaine
        - 💬 Répondre aux commentaires sous 1h
        - 📊 Analyser les performances chaque semaine
        """)
    
    with col2:
        st.markdown("""
        ### ❌ À ÉVITER
        - 📝 Posts trop longs (>300 caractères)
        - 🔢 Trop de hashtags (>10)
        - 🚫 Publier sans appel à l'action
        - 🙈 Ignorer les commentaires négatifs
        - 📋 Copier-coller le même contenu partout
        """)
    
    # Export du rapport
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

# Pied de page
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px;'>"
    "© 2025 Agence X - Social Media Intelligence | Propulsé par Google Gemini AI"
    "</p>",
    unsafe_allow_html=True
)