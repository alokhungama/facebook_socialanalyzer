from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import DatabaseManager
from facebook_api import FacebookAPI
from gemini_query import GeminiQueryEngine
import pandas as pd
import os
from dotenv import load_dotenv
import uvicorn
from fastapi import Query

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
        # Test DB connection
        campaigns = db_manager.get_campaigns()
        # Test Facebook API (will not fetch real data, just check token)
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
def load_data(
    table: str = Query("all", enum=["all", "campaigns", "adsets", "ads", "ad_insights"]),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Load limited data from a specific table.
    Supported tables: campaigns, adsets, ads, ad_insights
    Use 'all' to get a preview of each (limited).
    """
    try:
        if table == "campaigns":
            return {"campaigns": db_manager.get_campaigns()[:limit]}

        elif table == "adsets":
            return {"adsets": db_manager.get_adsets()[:limit]}

        elif table == "ads":
            return {"ads": db_manager.get_ads()[:limit]}

        elif table == "ad_insights":
            return {"ad_insights": db_manager.get_ad_insights()[:limit]}

        elif table == "all":
            return {
                "campaigns": db_manager.get_campaigns()[:limit],
                "adsets": db_manager.get_adsets()[:limit],
                "ads": db_manager.get_ads()[:limit],
                "ad_insights": db_manager.get_ad_insights()[:limit]
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid table name.")

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

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)