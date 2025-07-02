from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import os
import uvicorn
from dotenv import load_dotenv

from database import DatabaseManager
from facebook_api import FacebookAPI
from gemini_query import GeminiQueryEngine

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Facebook Ads Analytics FastAPI",
    description="API for Facebook Ads Analytics",
    version="1.0.0"
)

# Initialize core components
db_manager = DatabaseManager()
facebook_api = FacebookAPI()
gemini_engine = GeminiQueryEngine(db_manager)

# === Request Models ===
class FetchDataRequest(BaseModel):
    account_id: str

class AIQueryRequest(BaseModel):
    query: str

class MCPToolRequest(BaseModel):
    endpoint: str
    params: Dict[str, Any]

# === Basic Routes ===
@app.get("/")
def index():
    return {"message": "Facebook Ads Analytics FastAPI is running."}

@app.get("/status")
def status():
    try:
        campaigns = db_manager.get_campaigns()
        token = os.getenv('FACEBOOK_ACCESS_TOKEN', None)
        fb_ok = bool(token and len(token) > 0)
        return {
            "db_connected": True,
            "facebook_token_present": fb_ok,
            "campaigns_in_db": len(campaigns)
        }
    except Exception as e:
        return {"db_connected": False, "error": str(e)}

# === Data Fetching ===
@app.post("/fetch_data")
def fetch_data(request: FetchDataRequest):
    account_id = request.account_id
    if not account_id:
        raise HTTPException(status_code=400, detail="Missing account_id")
    try:
        campaigns = facebook_api.fetch_campaigns(account_id)
        adsets = facebook_api.fetch_adsets(account_id)
        ads = facebook_api.fetch_ads(account_id)
        ad_insights = facebook_api.fetch_ad_insights(account_id)

        db_manager.store_campaigns(campaigns)
        db_manager.store_adsets(adsets)
        db_manager.store_ads(ads)
        db_manager.store_ad_insights(ad_insights)

        return {
            "status": "success",
            "campaigns_count": len(campaigns),
            "adsets_count": len(adsets),
            "ads_count": len(ads),
            "ad_insights_count": len(ad_insights)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load_data")
def load_data():
    try:
        campaigns = db_manager.get_campaigns()
        adsets = db_manager.get_adsets()
        ads = db_manager.get_ads()
        ad_insights = db_manager.get_ad_insights()
        return {
            "campaigns": campaigns,
            "adsets": adsets,
            "ads": ads,
            "ad_insights": ad_insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === AI Query Interface ===
@app.post("/ai_query")
def ai_query(request: AIQueryRequest):
    query = request.query
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    try:
        result = gemini_engine.process_query(query)
        response = {}
        if result.get('data') is not None:
            response['data'] = result['data'].to_dict(orient='records')
        if result.get('insights'):
            response['insights'] = result['insights']
        if result.get('sql_query'):
            response['sql_query'] = result['sql_query']
        if result.get('error'):
            response['error'] = result['error']
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auto_query")
def auto_query(request: AIQueryRequest):
    try:
        account_id = os.getenv("DEFAULT_ACCOUNT_ID", "")
        if not account_id:
            raise HTTPException(status_code=400, detail="Missing DEFAULT_ACCOUNT_ID in .env")

        campaigns = facebook_api.fetch_campaigns(account_id)
        adsets = facebook_api.fetch_adsets(account_id)
        ads = facebook_api.fetch_ads(account_id)
        ad_insights = facebook_api.fetch_ad_insights(account_id)

        db_manager.store_campaigns(campaigns)
        db_manager.store_adsets(adsets)
        db_manager.store_ads(ads)
        db_manager.store_ad_insights(ad_insights)

        result = gemini_engine.process_query(request.query)

        return {
            "fetch_status": "success",
            "fetched_counts": {
                "campaigns": len(campaigns),
                "adsets": len(adsets),
                "ads": len(ads),
                "ad_insights": len(ad_insights)
            },
            "insights": result.get("insights"),
            "sql_query": result.get("sql_query"),
            "data": result["data"].to_dict(orient='records') if result.get("data") is not None else [],
            "error": result.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Plugin Support ===
@app.get("/.well-known/{filename}")
async def serve_plugin_manifest(filename: str):
    return FileResponse(os.path.join(".well-known", filename))

@app.get("/static/{filename}")
async def serve_static_file(filename: str):
    return FileResponse(os.path.join("static", filename))

# === Open WebUI Tool Endpoint ===
@app.post("/mcp_tool")
async def mcp_tool_handler(payload: MCPToolRequest):
    try:
        endpoint = payload.endpoint
        params = payload.params
        account_id = params.get("account_id", "")
        date_range = params.get("date_range", "LAST_7_DAYS")

        # Compose a natural language query dynamically
        if endpoint == "summary":
            query = f"Show me a summary of Facebook ad performance for account {account_id} in the {date_range}."
        else:
            query = endpoint  # assume endpoint is already a natural language query

        # Run through GeminiQueryEngine
        result = gemini_engine.process_query(query)

        response = {
            "data": result["data"].to_dict(orient="records") if result.get("data") is not None else [],
            "metadata": {
                "account_id": account_id,
                "date_range": date_range,
                "query": query,
                "sql_query": result.get("sql_query")
            },
            "insights": result.get("insights", ""),
            "error": result.get("error", None)
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Uvicorn Entry Point ===
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

