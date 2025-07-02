from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import DatabaseManager
from facebook_api import FacebookAPI
from gemini_query import GeminiQueryEngine
import pandas as pd
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Facebook Ads Analytics FastAPI", description="API for Facebook Ads Analytics", version="1.0.0")

# Initialize core components once
db_manager = DatabaseManager()
facebook_api = FacebookAPI()
gemini_engine = GeminiQueryEngine(db_manager)

class FetchDataRequest(BaseModel):
    account_id: str

class AIQueryRequest(BaseModel):
    query: str

@app.get("/")
def index():
    """Health check endpoint."""
    return {"message": "Facebook Ads Analytics FastAPI is running."}

@app.get("/status")
def status():
    """Check DB and Facebook API connectivity."""
    try:
        campaigns = db_manager.get_campaigns()
        token = os.getenv('FACEBOOK_ACCESS_TOKEN', None)
        fb_ok = bool(token and len(token) > 0)
        return {"db_connected": True, "facebook_token_present": fb_ok, "campaigns_in_db": len(campaigns)}
    except Exception as e:
        return {"db_connected": False, "error": str(e)}

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
    """
    Automatically fetches data from Facebook, stores it in DB,
    and then runs the AI query using Gemini.
    """
    try:
        account_id = os.getenv("DEFAULT_ACCOUNT_ID", "")
        if not account_id:
            raise HTTPException(status_code=400, detail="Missing DEFAULT_ACCOUNT_ID in .env")

        # Step 1: Fetch and Store Fresh Data
        campaigns = facebook_api.fetch_campaigns(account_id)
        adsets = facebook_api.fetch_adsets(account_id)
        ads = facebook_api.fetch_ads(account_id)
        ad_insights = facebook_api.fetch_ad_insights(account_id)

        db_manager.store_campaigns(campaigns)
        db_manager.store_adsets(adsets)
        db_manager.store_ads(ads)
        db_manager.store_ad_insights(ad_insights)

        # Step 2: AI Query on Fresh Data
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
from fastapi.responses import FileResponse
from typing import Dict, Any

#Serve plugin files (.well-known and static/logo)
@app.get("/.well-known/{filename}")
async def serve_plugin_manifest(filename: str):
        return FileResponse(os.path.join(".well-known", filename))

@app.get("/static/{filename}")
async def serve_static_file(filename: str):
        return FileResponse(os.path.join("static", filename))

#Tool call request format
class MCPToolRequest(BaseModel):
        endpoint: str
        params: Dict[str, Any]

#Main tool endpoint for Open WebUI + Ollama
from fastapi.responses import FileResponse
from typing import Dict, Any

#Serve plugin files (.well-known and static/logo)
@app.get("/.well-known/{filename}")
async def serve_plugin_manifest(filename: str):
        return FileResponse(os.path.join(".well-known", filename))

@app.get("/static/{filename}")
async def serve_static_file(filename: str):
        return FileResponse(os.path.join("static", filename))

#Tool call request format
class MCPToolRequest(BaseModel):
        endpoint: str
        params: Dict[str, Any]

#Main tool endpoint for Open WebUI + Ollama
@app.post("/mcp_tool")
async def mcp_tool_handler(payload: MCPToolRequest):
        try:
                endpoint = payload.endpoint
                params = payload.params
                account_id = params.get("account_id", "")
                date_range = params.get("date_range", "LAST_7_DAYS")
                dummy_data = [
        {
            "ad_name": "Sample Ad",
            "ad_id": "123",
            "clicks": 100,
            "spend": 25.50
        }
    ]

    insights = "Sample Ad is performing well. Consider increasing the budget."

    return {
        "data": dummy_data,
        "metadata": {
            "account_id": account_id,
            "date_range": date_range,
            "intent": endpoint
        },
        "insights": insights
    }
except Exception as e:
    return JSONResponse(status_code=500, content={"error": str(e)})

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
