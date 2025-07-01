from flask import Flask, request, jsonify
from database import DatabaseManager
from facebook_api import FacebookAPI
from gemini_query import GeminiQueryEngine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize core components once
db_manager = DatabaseManager()
facebook_api = FacebookAPI()
gemini_engine = GeminiQueryEngine(db_manager)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data = request.get_json()
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({"error": "Missing account_id"}), 400
    try:
        campaigns = facebook_api.fetch_campaigns(account_id)
        adsets = facebook_api.fetch_adsets(account_id)
        ads = facebook_api.fetch_ads(account_id)
        ad_insights = facebook_api.fetch_ad_insights(account_id)

        # Optionally store in DB
        db_manager.store_campaigns(campaigns)
        db_manager.store_adsets(adsets)
        db_manager.store_ads(ads)
        db_manager.store_ad_insights(ad_insights)

        return jsonify({
            "status": "success",
            "campaigns_count": len(campaigns),
            "adsets_count": len(adsets),
            "ads_count": len(ads),
            "ad_insights_count": len(ad_insights)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load_data', methods=['GET'])
def load_data():
    try:
        campaigns = db_manager.get_campaigns()
        adsets = db_manager.get_adsets()
        ads = db_manager.get_ads()
        ad_insights = db_manager.get_ad_insights()
        return jsonify({
            "campaigns": campaigns,
            "adsets": adsets,
            "ads": ads,
            "ad_insights": ad_insights
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ai_query', methods=['POST'])
def ai_query():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "Missing query"}), 400
    try:
        result = gemini_engine.process_query(query)
        # result is expected to be a dict with 'data' (DataFrame) and 'insights' (str)
        response = {}
        if result.get('data') is not None:
            # Convert DataFrame to JSON
            response['data'] = result['data'].to_dict(orient='records')
        if result.get('insights'):
            response['insights'] = result['insights']
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return jsonify({"message": "Facebook Ads Analytics Flask API is running."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)