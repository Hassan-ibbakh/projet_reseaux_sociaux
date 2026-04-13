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
def get_reddit_comments():
    try:
        data = request.get_json()
        url = data.get('url', 'https://www.reddit.com/r/marketing/top/.json?limit=25&t=week')
        
        # Nettoyage URL — supprimer paramètres utm si présents
        if '?' in url and 'utm' in url:
            url = url.split('?')[0]
        if not url.endswith('.json'):
            url = url.rstrip('/') + '.json'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        
        response = req.get(url, headers=headers, timeout=15)
        
        # Vérifier si Reddit a bloqué
        if 'html' in response.headers.get('Content-Type', ''):
            return jsonify({"status": "error", "message": "Reddit a bloque la requete"}), 429
            
        reddit_data = response.json()

        if isinstance(reddit_data, list):
            comments = [
                c['data']['body']
                for c in reddit_data[1]['data']['children']
                if c['data'].get('body') not in [None, '[deleted]', '[removed]']
            ]
            title = reddit_data[0]['data']['children'][0]['data']['title']
            score = reddit_data[0]['data']['children'][0]['data']['score']
        else:
            posts = reddit_data['data']['children']
            comments = [p['data']['title'] for p in posts]
            title = "Top posts"
            score = 0

        return jsonify({
            "status": "success",
            "comments": comments[:50],
            "post_title": title,
            "post_score": score,
            "total_comments": len(comments)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    try:
        data = request.get_json()
        url = data.get('url', 'https://www.reddit.com/r/Entrepreneur/comments/1sfen8x/are_successful_entrepreneurs_just_people_with/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button')

        headers = {"User-Agent": "Mozilla/5.0 AgenceX/1.0"}
        response = req.get(url, headers=headers, timeout=10)
        reddit_data = response.json()

        if isinstance(reddit_data, list):
            comments = [
                c['data']['body']
                for c in reddit_data[1]['data']['children']
                if c['data'].get('body') not in [None, '[deleted]', '[removed]']
            ]
            title = reddit_data[0]['data']['children'][0]['data']['title']
            score = reddit_data[0]['data']['children'][0]['data']['score']
        else:
            posts = reddit_data['data']['children']
            comments = [p['data']['title'] for p in posts]
            title = "Top posts"
            score = 0

        return jsonify({
            "status": "success",
            "comments": comments[:50],
            "post_title": title,
            "post_score": score,
            "total_comments": len(comments)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)