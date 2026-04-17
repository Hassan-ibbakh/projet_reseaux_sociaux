from flask import Flask, jsonify, request
from src.preprocessing import load_and_clean_data
from src.analysis import calculate_kpis, generate_insights
import json
import os
import requests as req

app = Flask(__name__)


@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    try:
        df = load_and_clean_data('data/raw_data.csv')
        kpis, df = calculate_kpis(df)
        insights = generate_insights(df)
        report = {"kpis": kpis, "insights": insights}
        os.makedirs("reports", exist_ok=True)
        with open("reports/latest_report.json", "w") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success", **kpis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/report', methods=['GET'])
def get_report():
    try:
        with open("reports/latest_report.json") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"error": "Aucun rapport disponible"}), 404


@app.route('/collect', methods=['POST'])
def collect():
    try:
        from collector import collect_and_save
        df = collect_and_save('data/raw_data.csv')
        return jsonify({"status": "success", "posts_collected": len(df)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/reddit-comments', methods=['POST'])
@app.route('/reddit-comments', methods=['POST'])
def get_reddit_comments():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"status": "error", "message": "Missing 'url' in request body"}), 400
        
        url = data['url']
        if '?' in url and 'utm' in url:
            url = url.split('?')[0]
        if not url.endswith('.json'):
            url = url.rstrip('/') + '.json'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        
        print(f"[DEBUG] Fetching URL: {url}")
        response = req.get(url, headers=headers, timeout=15)
        print(f"[DEBUG] Status code: {response.status_code}")
        print(f"[DEBUG] Content-Type: {response.headers.get('Content-Type')}")
        
        if 'html' in response.headers.get('Content-Type', ''):
            return jsonify({"status": "error", "message": "Reddit a bloqué la requête"}), 429
        
        reddit_data = response.json()
        
        # Log de la structure
        print(f"[DEBUG] Type of reddit_data: {type(reddit_data)}")
        if isinstance(reddit_data, dict):
            print(f"[DEBUG] Keys: {reddit_data.keys()}")
            # Si c'est un dictionnaire, peut-être qu'il contient une clé 'error' ou 'message'
        elif isinstance(reddit_data, list):
            print(f"[DEBUG] List length: {len(reddit_data)}")
            for i, item in enumerate(reddit_data[:2]):
                print(f"[DEBUG] Item {i} type: {type(item)}, keys: {item.keys() if isinstance(item, dict) else 'N/A'}")
        
        # Sauvegarder la réponse brute dans un fichier pour inspection
        with open('reddit_debug.json', 'w', encoding='utf-8') as f:
            json.dump(reddit_data, f, ensure_ascii=False, indent=2)
        print("[DEBUG] Réponse sauvegardée dans reddit_debug.json")
        
        # Détection automatique du type de contenu
        title = ""
        score = 0
        comments = []
        
        # Cas 1 : Post unique avec commentaires (format [post_data, comments_data])
        if isinstance(reddit_data, list) and len(reddit_data) >= 2:
            try:
                if 'data' in reddit_data[0] and 'children' in reddit_data[0]['data']:
                    post_data = reddit_data[0]['data']['children'][0]['data']
                    title = post_data.get('title', 'Sans titre')
                    score = post_data.get('score', 0)
                    
                    if len(reddit_data) >= 2 and 'data' in reddit_data[1] and 'children' in reddit_data[1]['data']:
                        comments = [
                            c['data']['body']
                            for c in reddit_data[1]['data']['children']
                            if c['data'].get('body') not in [None, '[deleted]', '[removed]']
                        ]
                    print(f"[DEBUG] Cas 1: title={title}, score={score}, comments_count={len(comments)}")
            except (KeyError, IndexError, TypeError) as e:
                print(f"[DEBUG] Erreur parsing post unique: {e}")
        
        # Cas 2 : Flux de plusieurs posts
        elif isinstance(reddit_data, dict) and 'data' in reddit_data and 'children' in reddit_data['data']:
            posts = reddit_data['data']['children']
            comments = [p['data'].get('title', 'Sans titre') for p in posts]
            title = "Flux de posts"
            score = 0
            print(f"[DEBUG] Cas 2: title={title}, comments_count={len(comments)}")
        
        # Cas 3 : La réponse n'est pas dans un format standard Reddit
        else:
            print(f"[DEBUG] Cas 3: Format non reconnu, type={type(reddit_data)}")
            title = "Format non reconnu"
            score = 0
            comments = []

        return jsonify({
            "status": "success",
            "comments": comments[:50],
            "post_title": title,
            "post_score": score,
            "total_comments": len(comments)
        })
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)