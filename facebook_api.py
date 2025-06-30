
# import os
# import requests
# import time
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import logging
# from typing import List, Dict, Any

# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class FacebookAPI:
#     def __init__(self):
#         self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
#         self.api_version = 'v18.0'
#         self.base_url = f'https://graph.facebook.com/{self.api_version}'
#         self.limit = 500

#         if not self.access_token:
#             logger.warning("Facebook access token not found in environment variables")

#     def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
#         url = f"{self.base_url}/{endpoint}"
#         default_params = {
#             'access_token': self.access_token,
#             'limit': self.limit
#         }
#         if params:
#             default_params.update(params)

#         try:
#             response = requests.get(url, params=default_params)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logger.error(f"API request failed: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 logger.error(f"Response content: {e.response.text}")
#             raise

#     def _paginate_request(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
#         all_data = []
#         response = self._make_request(endpoint, params)
#         if 'data' in response:
#             all_data.extend(response['data'])

#         while 'paging' in response and 'next' in response['paging']:
#             logger.info(f"Fetching next page, current count: {len(all_data)}")
#             next_url = response['paging']['next']
#             after_param = next_url.split('after=')[1].split('&')[0] if 'after=' in next_url else None
#             if after_param:
#                 paginated_params = params.copy() if params else {}
#                 paginated_params['after'] = after_param
#                 response = self._make_request(endpoint, paginated_params)
#                 if 'data' in response:
#                     all_data.extend(response['data'])
#                 else:
#                     break
#                 time.sleep(0.1)
#             else:
#                 break
#         logger.info(f"Fetched total {len(all_data)} items")
#         return all_data

#     def fetch_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = "id,name,status,objective,created_time,updated_time,start_time,stop_time,budget_remaining,daily_budget,lifetime_budget,account_id,buying_type,spend_cap,special_ad_categories,bid_strategy"
#         endpoint = f"{account_id}/campaigns"
#         return self._paginate_request(endpoint, {"fields": fields})

#     def fetch_adsets(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = "id,name,status,campaign_id,optimization_goal,billing_event,bid_amount,daily_budget,lifetime_budget,start_time,end_time,created_time,updated_time,account_id,targeting,pacing_type,attribution_spec,bid_strategy,promoted_object,frequency_cap,frequency_control_specs"
#         endpoint = f"{account_id}/adsets"
#         return self._paginate_request(endpoint, {"fields": fields})

#     def fetch_ads(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = "id,name,status,campaign_id,adset_id,created_time,updated_time,account_id,adcreatives{id,name},objective,buying_type,optimization_goal,bid_strategy,attribution_setting"
#         endpoint = f"{account_id}/ads"
#         ads = self._paginate_request(endpoint, {"fields": fields})
#         logger.info(f"Fetched total {len(ads)} ads")

#         # Fetch insights in bulk (not one-by-one)
#         insights = self.fetch_insights_bulk(account_id)
#         insights_by_id = {insight.get("ad_id"): insight for insight in insights if "ad_id" in insight}

#         # Merge into ads
#         enriched_ads = []
#         for ad in ads:
#             ad_insight = insights_by_id.get(ad["id"], {})
#             ad.update(ad_insight)
#             enriched_ads.append(ad)

#         return enriched_ads

#     def fetch_insights_bulk(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = ",".join([
#             "ad_id", "impressions", "clicks", "spend", "reach", "frequency",
#             "cpm", "cpc", "ctr", "cpp",
#             "date_start", "date_stop", "conversion_values"
#         ])
#         endpoint = f"{account_id}/insights"
#         params = {
#             "fields": fields,
#             "level": "ad",
#             "date_preset": "last_30d"
#         }
#         return self._paginate_request(endpoint, params)

# facebook_api.py

# import os
# import requests
# import time
# from dotenv import load_dotenv
# from datetime import datetime
# import logging
# from typing import List, Dict, Any

# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class FacebookAPI:
#     def __init__(self):
#         self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
#         self.api_version = 'v18.0'
#         self.base_url = f'https://graph.facebook.com/{self.api_version}'
#         self.limit = 500

#         if not self.access_token:
#             logger.warning("Facebook access token not found in environment variables")

#     def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
#         url = f"{self.base_url}/{endpoint}"
#         default_params = {
#             'access_token': self.access_token,
#             'limit': self.limit
#         }
#         if params:
#             default_params.update(params)

#         try:
#             response = requests.get(url, params=default_params)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logger.error(f"API request failed: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 logger.error(f"Response content: {e.response.text}")
#             raise

#     def _paginate_request(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
#         all_data = []
#         response = self._make_request(endpoint, params)
#         if 'data' in response:
#             all_data.extend(response['data'])

#         while 'paging' in response and 'next' in response['paging']:
#             logger.info(f"Fetching next page, current count: {len(all_data)}")
#             next_url = response['paging']['next']
#             after_param = next_url.split('after=')[1].split('&')[0] if 'after=' in next_url else None
#             if after_param:
#                 paginated_params = params.copy() if params else {}
#                 paginated_params['after'] = after_param
#                 response = self._make_request(endpoint, paginated_params)
#                 if 'data' in response:
#                     all_data.extend(response['data'])
#                 else:
#                     break
#                 time.sleep(0.1)
#             else:
#                 break
#         logger.info(f"Fetched total {len(all_data)} items")
#         return all_data

#     def fetch_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = (
#             "id,name,status,objective,created_time,updated_time,"
#             "start_time,stop_time,budget_remaining,daily_budget,"
#             "lifetime_budget,account_id,buying_type,spend_cap,"
#             "special_ad_categories,bid_strategy"
#         )
#         endpoint = f"{account_id}/campaigns"
#         return self._paginate_request(endpoint, {"fields": fields})

#     def fetch_adsets(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = (
#             "id,name,status,campaign_id,optimization_goal,billing_event,"
#             "bid_amount,daily_budget,lifetime_budget,start_time,end_time,"
#             "created_time,updated_time,account_id,targeting,pacing_type,"
#             "attribution_spec,bid_strategy,promoted_object,frequency_cap,"
#             "frequency_control_specs"
#         )
#         endpoint = f"{account_id}/adsets"
#         return self._paginate_request(endpoint, {"fields": fields})

#     def fetch_ads(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = (
#             "id,name,status,campaign_id,adset_id,created_time,updated_time,"
#             "account_id,objective,buying_type,optimization_goal,bid_strategy,"
#             "attribution_setting,adcreatives{id,name}"
#         )
#         endpoint = f"{account_id}/ads"
#         return self._paginate_request(endpoint, {"fields": fields})
#         # logger.info(f"Fetched total {len(ads)} ads")

#         # insights = self.fetch_ad_insights(account_id)
#         # insights_by_id = {insight.get("ad_id"): insight for insight in insights if "ad_id" in insight}

#         # enriched_ads = []
#         # for ad in ads:
#         #     ad_insight = insights_by_id.get(ad["id"], {})
#         #     ad.update(ad_insight)
#         #     enriched_ads.append(ad)

#         # return enriched_ads

#     def fetch_ad_insights(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = ",".join([
#             "ad_id", "impressions", "clicks", "spend", "reach", "frequency",
#             "cpm", "cpc", "ctr", "cpp", "date_start", "date_stop", "conversion_values"
#         ])
#         endpoint = f"{account_id}/insights"
#         params = {
#             "fields": fields,
#             "level": "ad",
#             "date_preset": "last_30d"
#         }
#         return self._paginate_request(endpoint, params)

#     def fetch_campaign_insights(self, account_id: str) -> List[Dict[str, Any]]:
#         fields = ",".join([
#             "campaign_id", "impressions", "clicks", "spend", "reach", "frequency",
#             "cpm", "cpc", "ctr", "cpp", "date_start", "date_stop", "conversion_values"
#         ])
#         endpoint = f"{account_id}/insights"
#         params = {
#             "fields": fields,
#             "level": "campaign",
#             "date_preset": "last_30d"
#         }
#         return self._paginate_request(endpoint, params)

import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime
import logging
from typing import List, Dict, Any

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookAPI:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        self.limit = 500

        if not self.access_token:
            logger.warning("Facebook access token not found in environment variables")

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        default_params = {
            'access_token': self.access_token,
            'limit': self.limit
        }
        if params:
            default_params.update(params)

        try:
            response = requests.get(url, params=default_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise

    def _paginate_request(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        all_data = []
        response = self._make_request(endpoint, params)
        if 'data' in response:
            all_data.extend(response['data'])

        while 'paging' in response and 'next' in response['paging']:
            logger.info(f"Fetching next page, current count: {len(all_data)}")
            next_url = response['paging']['next']
            after_param = next_url.split('after=')[1].split('&')[0] if 'after=' in next_url else None
            if after_param:
                paginated_params = params.copy() if params else {}
                paginated_params['after'] = after_param
                response = self._make_request(endpoint, paginated_params)
                if 'data' in response:
                    all_data.extend(response['data'])
                else:
                    break
                time.sleep(0.1)
            else:
                break
        logger.info(f"Fetched total {len(all_data)} items")
        return all_data

    def fetch_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
        fields = (
            "id,name,status,objective,created_time,updated_time,"
            "start_time,stop_time,budget_remaining,daily_budget,"
            "lifetime_budget,account_id,buying_type,spend_cap,"
            "special_ad_categories,bid_strategy"
        )
        endpoint = f"{account_id}/campaigns"
        
        # Fetch data from the API
        campaigns = self._paginate_request(endpoint, {"fields": fields})
        
        # Convert paise to rupees for budget fields
        for campaign in campaigns:
            for field in ['budget_remaining', 'daily_budget', 'lifetime_budget']:
                if field in campaign and campaign[field] is not None:
                    try:
                        campaign[field] = float(campaign[field]) / 100
                    except (ValueError, TypeError):
                        campaign[field] = None  # fallback if conversion fails

        return campaigns


    def fetch_adsets(self, account_id: str) -> List[Dict[str, Any]]:
        fields = (
            "id,name,status,campaign_id,optimization_goal,billing_event,"
            "bid_amount,daily_budget,lifetime_budget,start_time,end_time,"
            "created_time,updated_time,account_id,targeting,pacing_type,"
            "attribution_spec,bid_strategy,promoted_object,frequency_cap,"
            "frequency_control_specs"
        )
        endpoint = f"{account_id}/adsets"
        return self._paginate_request(endpoint, {"fields": fields})

    def fetch_ads(self, account_id: str) -> List[Dict[str, Any]]:
        fields = (
            "id,name,status,campaign_id,adset_id,created_time,updated_time,"
            "account_id,objective,buying_type,optimization_goal,bid_strategy,"
            "attribution_setting,adcreatives{id,name}"
        )
        endpoint = f"{account_id}/ads"
        return self._paginate_request(endpoint, {"fields": fields})

    def fetch_ad_insights(self, account_id: str) -> List[Dict[str, Any]]:
        fields = ",".join([
            "ad_id", "campaign_id", "impressions", "clicks", "spend", "reach", "frequency",
            "cpm", "cpc", "ctr", "cpp", "date_start", "date_stop", "conversion_values"
        ])
        endpoint = f"{account_id}/insights"
        params = {
            "fields": fields,
            "level": "ad",
            "date_preset": "last_14d",
            "time_increment": 1
        }
        return self._paginate_request(endpoint, params)
