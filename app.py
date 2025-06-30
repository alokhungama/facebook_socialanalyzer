# import os
# from dotenv import load_dotenv
# load_dotenv()
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import time
# import numpy as np

# from facebook_api import FacebookAPI
# from database import DatabaseManager
# from gemini_query import GeminiQueryEngine
# from utils import format_currency, format_percentage, validate_account_id

# # Page configuration
# st.set_page_config(
#     page_title="Facebook Ads Analytics",
#     page_icon="📊",
#     layout="wide"
# )

# # Initialize session state
# if 'data_fetched' not in st.session_state:
#     st.session_state.data_fetched = False
# if 'campaigns_df' not in st.session_state:
#     st.session_state.campaigns_df = None
# if 'adsets_df' not in st.session_state:
#     st.session_state.adsets_df = None
# if 'ads_df' not in st.session_state:
#     st.session_state.ads_df = None

# def safe_convert_to_numeric(value, default=0):
#     """Safely convert a value to numeric, handling strings and None values."""
#     try:
#         if pd.isna(value) or value is None or value == '':
#             return default
#         return float(value)
#     except (ValueError, TypeError):
#         return default

# def prepare_numeric_data(df, columns):
#     """Convert specified columns to numeric values safely."""
#     df_copy = df.copy()
#     for col in columns:
#         if col in df_copy.columns:
#             df_copy[col] = df_copy[col].apply(lambda x: safe_convert_to_numeric(x, 0))
#     return df_copy

# def main():
#     st.title("📊 Facebook Ads Analytics Platform")
#     st.markdown("### AI-Powered Facebook Ads Data Analysis")

#     try:
#         db_manager = DatabaseManager()
#         facebook_api = FacebookAPI()
#         gemini_engine = GeminiQueryEngine(db_manager)
#     except Exception as e:
#         st.error(f"Failed to initialize components: {str(e)}")
#         st.stop()

#     with st.sidebar:
#         st.header("🔧 Configuration")

#         account_id = st.text_input(
#             "Facebook Ads Account ID",
#             placeholder="act_1234567890",
#             help="Enter your Facebook Ads account ID (e.g., act_1234567890)"
#         )

#         if account_id and not validate_account_id(account_id):
#             st.error("Invalid account ID format. Should start with 'act_' followed by numbers.")

#         st.subheader("📅 Data Management")

#         fetch_button = st.button(
#             "🔄 Fetch Fresh Data",
#             disabled=not account_id or not validate_account_id(account_id),
#             help="Fetch latest data from Facebook Marketing API"
#         )

#         if fetch_button:
#             fetch_facebook_data(account_id, facebook_api, db_manager)

#         load_button = st.button(
#             "📂 Load Existing Data",
#             help="Load previously fetched data from database"
#         )

#         if load_button:
#             load_existing_data(db_manager)

#         if st.session_state.data_fetched:
#             st.success("✅ Data loaded successfully")
#             if st.session_state.campaigns_df is not None:
#                 st.metric("Campaigns", len(st.session_state.campaigns_df))
#             if st.session_state.adsets_df is not None:
#                 st.metric("Ad Sets", len(st.session_state.adsets_df))
#             if st.session_state.ads_df is not None:
#                 st.metric("Ads", len(st.session_state.ads_df))
#         else:
#             st.info("💡 Fetch or load data to begin analysis")

#     if not st.session_state.data_fetched:
#         show_welcome_screen()
#     else:
#         show_analytics_dashboard(gemini_engine)

# def fetch_facebook_data(account_id, facebook_api, db_manager):
#     with st.spinner("Fetching data from Facebook Marketing API..."):
#         progress_bar = st.progress(0)
#         status_text = st.empty()

#         try:
#             status_text.text("Fetching campaigns...")
#             campaigns = facebook_api.fetch_campaigns(account_id)
#             progress_bar.progress(25)

#             status_text.text("Fetching ad sets...")
#             adsets = facebook_api.fetch_adsets(account_id)
#             progress_bar.progress(50)

#             status_text.text("Fetching ads...")
#             ads = facebook_api.fetch_ads(account_id)
#             progress_bar.progress(75)

#             status_text.text("Storing data in database...")
#             db_manager.store_campaigns(campaigns)
#             db_manager.store_adsets(adsets)
#             db_manager.store_ads(ads)

#             st.session_state.campaigns_df = pd.DataFrame(campaigns)
#             st.session_state.adsets_df = pd.DataFrame(adsets)
#             st.session_state.ads_df = pd.DataFrame(ads)
#             st.session_state.data_fetched = True

#             progress_bar.progress(100)
#             status_text.text("✅ Data fetched and stored successfully!")

#             time.sleep(1)
#             st.rerun()

#         except Exception as e:
#             st.error(f"Error fetching data: {str(e)}")
#             progress_bar.empty()
#             status_text.empty()

# def load_existing_data(db_manager):
#     try:
#         with st.spinner("Loading data from database..."):
#             campaigns = db_manager.get_campaigns()
#             adsets = db_manager.get_adsets()
#             ads = db_manager.get_ads()

#             if campaigns:
#                 st.session_state.campaigns_df = pd.DataFrame(campaigns)
#                 st.session_state.adsets_df = pd.DataFrame(adsets)
#                 st.session_state.ads_df = pd.DataFrame(ads)
#                 st.session_state.data_fetched = True
#                 st.success("Data loaded successfully from database!")
#                 st.rerun()
#             else:
#                 st.warning("No data found in database. Please fetch fresh data first.")

#     except Exception as e:
#         st.error(f"Error loading data: {str(e)}")

# def show_welcome_screen():
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         st.markdown("""
#         ## 🚀 Welcome to Facebook Ads Analytics

#         Get started by:
#         1. **Enter your Facebook Ads Account ID** in the sidebar
#         2. **Fetch fresh data** from Facebook Marketing API, or
#         3. **Load existing data** from the database

#         Once data is loaded, you can:
#         - 📊 View comprehensive analytics dashboards
#         - 🧠 Ask natural language questions about your data
#         - 📈 Explore interactive charts and visualizations

#         ### Features:
#         - 🔄 Real-time data fetching with pagination
#         - 📀 PostgreSQL database storage
#         - 🧠 AI-powered querying with Google Gemini
#         - 📱 Interactive dashboards and charts
#         """)

# def show_overview_tab():
#     st.header("📊 Campaign Overview")

#     if st.session_state.ads_df is not None and not st.session_state.ads_df.empty:
#         # Prepare data with proper numeric conversion
#         insights_df = prepare_numeric_data(st.session_state.ads_df, 
#                                          ['spend', 'impressions', 'clicks'])

#         col1, col2, col3, col4 = st.columns(4)

#         total_spend = insights_df['spend'].sum()
#         total_impressions = insights_df['impressions'].sum()
#         total_clicks = insights_df['clicks'].sum()
#         avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

#         with col1:
#             st.metric("Total Spend", format_currency(total_spend))
#         with col2:
#             st.metric("Total Impressions", f"{int(total_impressions):,}")
#         with col3:
#             st.metric("Total Clicks", f"{int(total_clicks):,}")
#         with col4:
#             st.metric("Average CTR", format_percentage(avg_ctr))

#         col1, col2 = st.columns(2)

#         with col1:
#             if st.session_state.campaigns_df is not None:
#                 try:
#                     campaign_spend = insights_df.groupby('campaign_id')['spend'].sum().reset_index()
#                     campaign_spend = campaign_spend.merge(
#                         st.session_state.campaigns_df[['id', 'name']], 
#                         left_on='campaign_id', 
#                         right_on='id', 
#                         how='left'
#                     )
#                     # Filter out campaigns with zero spend
#                     campaign_spend = campaign_spend[campaign_spend['spend'] > 0]
                    
#                     if not campaign_spend.empty:
#                         fig = px.bar(
#                             campaign_spend.head(10),
#                             x='name',
#                             y='spend',
#                             title="Top 10 Campaigns by Spend",
#                             labels={'spend': 'Spend (₹)', 'name': 'Campaign Name'}
#                         )
#                         fig.update_layout(xaxis_tickangle=45)
#                         st.plotly_chart(fig, use_container_width=True)
#                     else:
#                         st.info("No campaign spending data available")
#                 except Exception as e:
#                     st.error(f"Error creating campaign spend chart: {str(e)}")

#         with col2:
#             try:
#                 campaign_metrics = insights_df.groupby('campaign_id').agg({
#                     'clicks': 'sum',
#                     'impressions': 'sum',
#                     'spend': 'sum'
#                 }).reset_index()
                
#                 # Safely calculate metrics with proper division handling
#                 campaign_metrics['clicks'] = campaign_metrics['clicks'].replace(0, np.nan)
#                 campaign_metrics['impressions'] = campaign_metrics['impressions'].replace(0, np.nan)
#                 campaign_metrics['spend'] = campaign_metrics['spend'].replace(0, np.nan)
                
#                 # Calculate CTR (only where impressions > 0)
#                 campaign_metrics['ctr'] = np.where(
#                     campaign_metrics['impressions'] > 0,
#                     (campaign_metrics['clicks'] / campaign_metrics['impressions'] * 100),
#                     0
#                 )
                
#                 # Calculate CPC (only where clicks > 0)
#                 campaign_metrics['cpc'] = np.where(
#                     campaign_metrics['clicks'] > 0,
#                     campaign_metrics['spend'] / campaign_metrics['clicks'],
#                     0
#                 )
                
#                 # Calculate CPM (only where impressions > 0)
#                 campaign_metrics['cpm'] = np.where(
#                     campaign_metrics['impressions'] > 0,
#                     (campaign_metrics['spend'] / campaign_metrics['impressions']) * 1000,
#                     0
#                 )
                
#                 # Merge with campaign names
#                 campaign_metrics = campaign_metrics.merge(
#                     st.session_state.campaigns_df[['id', 'name']], 
#                     left_on='campaign_id', 
#                     right_on='id', 
#                     how='left'
#                 )
                
#                 # Filter out campaigns with zero CTR
#                 campaign_metrics_filtered = campaign_metrics[campaign_metrics['ctr'] > 0]
                
#                 if not campaign_metrics_filtered.empty:
#                     fig = px.bar(
#                         campaign_metrics_filtered.head(10),
#                         x='name',
#                         y='ctr',
#                         title="Top 10 Campaigns by CTR",
#                         labels={'ctr': 'CTR (%)', 'name': 'Campaign Name'}
#                     )
#                     fig.update_layout(xaxis_tickangle=45)
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.info("No CTR data available for campaigns")
                    
#             except Exception as e:
#                 st.error(f"Error creating CTR chart: {str(e)}")
#     else:
#         st.info("No ads data available. Please fetch or load data first.")

# def show_ai_query_tab(gemini_engine):
#     st.header("🤖 AI-Powered Analytics")
#     st.markdown("Ask questions about your Facebook Ads data in natural language!")

#     user_query = st.text_area(
#         "Enter your question:",
#         placeholder="e.g., Show me top 5 campaigns by spend",
#         height=100
#     )
#     if st.button("🔍 Analyze") and user_query.strip():
#         with st.spinner("Analyzing your query..."):
#             try:
#                 result = gemini_engine.process_query(user_query)
#                 if result:
#                     st.subheader("📋 Query Results")
#                     if result['data'] is not None and not result['data'].empty:
#                         st.dataframe(result['data'], use_container_width=True)
#                     if result.get('insights'):
#                         st.subheader("🧠 AI Insights")
#                         st.markdown(result['insights'])
#                 else:
#                     st.error("Failed to process query. Try rephrasing.")
#             except Exception as e:
#                 st.error(f"Error: {str(e)}")

# def show_raw_data_tab():
#     st.header("📋 Raw Data")
#     data_type = st.selectbox("Select data to view:", ["Campaigns", "Ad Sets", "Ads"])
    
#     try:
#         if data_type == "Campaigns" and st.session_state.campaigns_df is not None:
#             st.dataframe(st.session_state.campaigns_df, use_container_width=True)
#         elif data_type == "Ad Sets" and st.session_state.adsets_df is not None:
#             st.dataframe(st.session_state.adsets_df, use_container_width=True)
#         elif data_type == "Ads" and st.session_state.ads_df is not None:
#             st.dataframe(st.session_state.ads_df, use_container_width=True)
#         else:
#             st.info("No data available. Fetch or load data first.")
#     except Exception as e:
#         st.error(f"Error displaying data: {str(e)}")

# def show_analytics_dashboard(gemini_engine):
#     tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧠 AI Query", "📋 Raw Data"])
#     with tab1:
#         show_overview_tab()
#     with tab2:
#         show_ai_query_tab(gemini_engine)
#     with tab3:
#         show_raw_data_tab()

# if __name__ == "__main__":
#     main()

# app.py

# import os
# from dotenv import load_dotenv
# load_dotenv()
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from datetime import datetime
# import time
# import numpy as np

# from facebook_api import FacebookAPI
# from database import DatabaseManager
# from gemini_query import GeminiQueryEngine
# from utils import format_currency, format_percentage, validate_account_id

# st.set_page_config(page_title="Facebook Ads Analytics", page_icon="📊", layout="wide")

# if 'data_fetched' not in st.session_state:
#     st.session_state.data_fetched = False
# if 'campaigns_df' not in st.session_state:
#     st.session_state.campaigns_df = None
# if 'adsets_df' not in st.session_state:
#     st.session_state.adsets_df = None
# if 'ads_df' not in st.session_state:
#     st.session_state.ads_df = None

# def safe_convert_to_numeric(value, default=0):
#     try:
#         if pd.isna(value) or value is None or value == '':
#             return default
#         return float(value)
#     except (ValueError, TypeError):
#         return default

# def prepare_numeric_data(df, columns):
#     df_copy = df.copy()
#     for col in columns:
#         if col in df_copy.columns:
#             df_copy[col] = df_copy[col].apply(lambda x: safe_convert_to_numeric(x, 0))
#     return df_copy

# def main():
#     st.title("📊 Facebook Ads Analytics Platform")
#     st.markdown("### AI-Powered Facebook Ads Data Analysis")

#     try:
#         db_manager = DatabaseManager()
#         facebook_api = FacebookAPI()
#         gemini_engine = GeminiQueryEngine(db_manager)
#     except Exception as e:
#         st.error(f"Failed to initialize components: {str(e)}")
#         st.stop()

#     with st.sidebar:
#         st.header("🔧 Configuration")

#         account_id = st.text_input("Facebook Ads Account ID", placeholder="act_1234567890")

#         if account_id and not validate_account_id(account_id):
#             st.error("Invalid account ID format. Should start with 'act_' followed by numbers.")

#         fetch_button = st.button("🔄 Fetch Fresh Data", disabled=not account_id or not validate_account_id(account_id))

#         if fetch_button:
#             fetch_facebook_data(account_id, facebook_api, db_manager)

#         load_button = st.button("📂 Load Existing Data")

#         if load_button:
#             load_existing_data(db_manager)

#         if st.session_state.data_fetched:
#             st.success("✅ Data loaded successfully")
#             if st.session_state.campaigns_df is not None:
#                 st.metric("Campaigns", len(st.session_state.campaigns_df))
#             if st.session_state.adsets_df is not None:
#                 st.metric("Ad Sets", len(st.session_state.adsets_df))
#             if st.session_state.ads_df is not None:
#                 st.metric("Ads", len(st.session_state.ads_df))
#         else:
#             st.info("💡 Fetch or load data to begin analysis")

#     if not st.session_state.data_fetched:
#         show_welcome_screen()
#     else:
#         show_analytics_dashboard(gemini_engine)

# def fetch_facebook_data(account_id, facebook_api, db_manager):
#     with st.spinner("Fetching data from Facebook..."):
#         progress_bar = st.progress(0)
#         status_text = st.empty()

#         try:
#             status_text.text("Fetching campaigns...")
#             campaigns = facebook_api.fetch_campaigns(account_id)
#             campaign_insights = facebook_api.fetch_campaign_insights(account_id)
#             insights_by_id = {insight['campaign_id']: insight for insight in campaign_insights}
#             for campaign in campaigns:
#                 insight = insights_by_id.get(campaign['id'], {})
#                 campaign.update(insight)
#             progress_bar.progress(25)

#             status_text.text("Fetching ad sets...")
#             adsets = facebook_api.fetch_adsets(account_id)
#             progress_bar.progress(50)

#             status_text.text("Fetching ads...")
#             ads = facebook_api.fetch_ads(account_id)
#             ad_insights = facebook_api.fetch_ad_insights(account_id)
#             ad_insights_by_id = {insight['ad_id']: insight for insight in ad_insights}
#             for ad in ads:
#                 insight = ad_insights_by_id.get(ad['id'], {})
#                 ad.update(insight)
#             progress_bar.progress(75)

#             status_text.text("Storing data...")
#             db_manager.store_campaigns(campaigns)
#             db_manager.store_campaigns(campaign_insights)
#             db_manager.store_adsets(adsets)
#             db_manager.store_ads(ads)
#             db_manager.store_ads(ad_insights)

#             st.session_state.campaigns_df = pd.DataFrame(campaigns)
#             st.session_state.adsets_df = pd.DataFrame(adsets)
#             st.session_state.ads_df = pd.DataFrame(ads)
#             st.session_state.data_fetched = True

#             progress_bar.progress(100)
#             status_text.text("✅ Data fetched successfully")
#             time.sleep(1)
#             st.rerun()
#         except Exception as e:
#             st.error(f"Error fetching data: {str(e)}")
#             progress_bar.empty()
#             status_text.empty()

# def load_existing_data(db_manager):
#     try:
#         with st.spinner("Loading data..."):
#             campaigns = db_manager.get_campaigns()
#             adsets = db_manager.get_adsets()
#             ads = db_manager.get_ads()

#             if campaigns:
#                 st.session_state.campaigns_df = pd.DataFrame(campaigns)
#                 st.session_state.adsets_df = pd.DataFrame(adsets)
#                 st.session_state.ads_df = pd.DataFrame(ads)
#                 st.session_state.data_fetched = True
#                 st.success("Data loaded from database!")
#                 st.rerun()
#             else:
#                 st.warning("No data found in database.")
#     except Exception as e:
#         st.error(f"Error loading data: {str(e)}")

# def show_welcome_screen():
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         st.markdown("""
#         ## 🚀 Welcome to Facebook Ads Analytics

#         Get started by:
#         1. **Enter your Facebook Ads Account ID**
#         2. **Fetch fresh data** from Facebook, or
#         3. **Load existing data**

#         ### Features:
#         - 📊 Interactive dashboards
#         - 🧠 AI-powered queries (Gemini)
#         - 💰 Campaign and Ad insights
#         """)

# def show_overview_tab():
#     st.header("📊 Campaign Overview")

#     if st.session_state.ads_df is not None and not st.session_state.ads_df.empty:
#         required_cols = ['spend', 'impressions', 'clicks']
#         missing_cols = [col for col in required_cols if col not in st.session_state.ads_df.columns]
#         if missing_cols:
#             st.error(f"Missing columns in ads data: {', '.join(missing_cols)}")
#             st.write("Available columns:", list(st.session_state.ads_df.columns))
#             return

#         insights_df = prepare_numeric_data(st.session_state.ads_df, required_cols)
#         total_spend = insights_df['spend'].sum()
#         total_impressions = insights_df['impressions'].sum()
#         total_clicks = insights_df['clicks'].sum()
#         avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Total Spend", format_currency(total_spend))
#         col2.metric("Total Impressions", f"{int(total_impressions):,}")
#         col3.metric("Total Clicks", f"{int(total_clicks):,}")
#         col4.metric("Average CTR", format_percentage(avg_ctr))
#     else:
#         st.info("No ads data available.")

# def show_ai_query_tab(gemini_engine):
#     st.header("🤖 AI-Powered Analytics")
#     user_query = st.text_area("Enter your question:", placeholder="e.g., Show top 5 campaigns by CPC")
#     if st.button("🔍 Analyze") and user_query.strip():
#         with st.spinner("Analyzing..."):
#             try:
#                 result = gemini_engine.process_query(user_query)
#                 if result['data'] is not None and not result['data'].empty:
#                     st.dataframe(result['data'], use_container_width=True)
#                 else:
#                     st.warning("No data returned.")
#                 if result.get('insights'):
#                     st.subheader("🧠 AI Insights")
#                     st.markdown(result['insights'])
#             except Exception as e:
#                 st.error(f"Error: {str(e)}")

# def show_raw_data_tab():
#     st.header("📋 Raw Data")
#     data_type = st.selectbox("Select data to view:", ["Campaigns", "Ad Sets", "Ads"])
#     try:
#         if data_type == "Campaigns":
#             st.dataframe(st.session_state.campaigns_df, use_container_width=True)
#         elif data_type == "Ad Sets":
#             st.dataframe(st.session_state.adsets_df, use_container_width=True)
#         elif data_type == "Ads":
#             st.dataframe(st.session_state.ads_df, use_container_width=True)
#     except Exception as e:
#         st.error(f"Error displaying data: {str(e)}")

# def show_analytics_dashboard(gemini_engine):
#     tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧠 AI Query", "📋 Raw Data"])
#     with tab1: show_overview_tab()
#     with tab2: show_ai_query_tab(gemini_engine)
#     with tab3: show_raw_data_tab()

# if __name__ == "__main__":
#     main()

# === UPDATED: app.py ===
# === UPDATED: app.py ===

import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import numpy as np
from facebook_api import FacebookAPI
from database import DatabaseManager
from gemini_query import GeminiQueryEngine
from utils import format_currency, format_percentage, validate_account_id

st.set_page_config(page_title="Facebook Ads Analytics", page_icon="📊", layout="wide")

if 'data_fetched' not in st.session_state:
    st.session_state.data_fetched = False
if 'campaigns_df' not in st.session_state:
    st.session_state.campaigns_df = None
if 'adsets_df' not in st.session_state:
    st.session_state.adsets_df = None
if 'ads_df' not in st.session_state:
    st.session_state.ads_df = None
if 'insights_df' not in st.session_state:
    st.session_state.insights_df = None

def safe_convert_to_numeric(value, default=0):
    try:
        if pd.isna(value) or value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def prepare_numeric_data(df, columns):
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: safe_convert_to_numeric(x, 0))
    return df_copy

def main():
    st.title("📊 Facebook Ads Analytics Platform")
    st.markdown("### AI-Powered Facebook Ads Data Analysis")

    try:
        db_manager = DatabaseManager()
        facebook_api = FacebookAPI()
        gemini_engine = GeminiQueryEngine(db_manager)
    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        st.stop()

    with st.sidebar:
        st.header("🔧 Configuration")

        account_id = st.text_input("Facebook Ads Account ID", placeholder="act_1234567890")

        if account_id and not validate_account_id(account_id):
            st.error("Invalid account ID format. Should start with 'act_' followed by numbers.")

        fetch_button = st.button("🔄 Fetch Fresh Data", disabled=not account_id or not validate_account_id(account_id))

        if fetch_button:
            fetch_facebook_data(account_id, facebook_api, db_manager)

        load_button = st.button("📂 Load Existing Data")

        if load_button:
            load_existing_data(db_manager)

        if st.session_state.data_fetched:
            st.success("✅ Data loaded successfully")
            if st.session_state.campaigns_df is not None:
                st.metric("Campaigns", len(st.session_state.campaigns_df))
            if st.session_state.adsets_df is not None:
                st.metric("Ad Sets", len(st.session_state.adsets_df))
            if st.session_state.ads_df is not None:
                st.metric("Ads", len(st.session_state.ads_df))
        else:
            st.info("💡 Fetch or load data to begin analysis")

    if not st.session_state.data_fetched:
        show_welcome_screen()
    else:
        show_analytics_dashboard(gemini_engine)

def fetch_facebook_data(account_id, facebook_api, db_manager):
    with st.spinner("Fetching data from Facebook..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("Fetching campaigns...")
            campaigns = facebook_api.fetch_campaigns(account_id)
            progress_bar.progress(20)

            status_text.text("Fetching ad sets...")
            adsets = facebook_api.fetch_adsets(account_id)
            progress_bar.progress(40)

            status_text.text("Fetching ads...")
            ads = facebook_api.fetch_ads(account_id)
            progress_bar.progress(60)

            status_text.text("Fetching ad insights...")
            ad_insights = facebook_api.fetch_ad_insights(account_id)
            progress_bar.progress(80)

            status_text.text("Storing data...")
            db_manager.store_campaigns(campaigns)
            db_manager.store_adsets(adsets)
            db_manager.store_ads(ads)
            db_manager.store_ad_insights(ad_insights)

            st.session_state.campaigns_df = pd.DataFrame(campaigns)
            st.session_state.adsets_df = pd.DataFrame(adsets)
            st.session_state.ads_df = pd.DataFrame(ads)
            st.session_state.insights_df = pd.DataFrame(ad_insights)
            st.session_state.data_fetched = True

            progress_bar.progress(100)
            status_text.text("✅ Data fetched successfully")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def load_existing_data(db_manager):
    try:
        with st.spinner("Loading data..."):
            campaigns = db_manager.get_campaigns()
            adsets = db_manager.get_adsets()
            ads = db_manager.get_ads()
            insights = db_manager.get_ad_insights()

            if campaigns:
                st.session_state.campaigns_df = pd.DataFrame(campaigns)
                st.session_state.adsets_df = pd.DataFrame(adsets)
                st.session_state.ads_df = pd.DataFrame(ads)
                st.session_state.insights_df = pd.DataFrame(insights)
                st.session_state.data_fetched = True
                st.success("Data loaded from database!")
                st.rerun()
            else:
                st.warning("No data found in database.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def show_analytics_dashboard(gemini_engine):
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧠 AI Query", "📋 Raw Data"])
    with tab1:
        show_overview_tab()
    with tab2:
        show_ai_query_tab(gemini_engine)
    with tab3:
        show_raw_data_tab()

def show_overview_tab():
    st.header("📊 Campaign Overview")
    if st.session_state.insights_df is not None and not st.session_state.insights_df.empty:
        df = prepare_numeric_data(st.session_state.insights_df, ['spend', 'impressions', 'clicks'])

        total_spend = df['spend'].sum()
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Spend", format_currency(total_spend))
        col2.metric("Total Impressions", f"{int(total_impressions):,}")
        col3.metric("Total Clicks", f"{int(total_clicks):,}")
        col4.metric("Average CTR", format_percentage(avg_ctr))

        st.markdown("### 📈 Spend Trend (Last 14 Days)")
        try:
            trend_df = df.groupby("date_start")["spend"].sum().reset_index()
            fig = px.line(trend_df, x="date_start", y="spend", markers=True, title="Daily Spend")
            fig.update_layout(xaxis_title="Date", yaxis_title="Spend")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {str(e)}")
    else:
        st.info("No insights data available.")

def show_ai_query_tab(gemini_engine):
    st.header("🤖 AI-Powered Analytics")
    user_query = st.text_area("Enter your question:", placeholder="e.g., Show top 5 campaigns by CPC")
    if st.button("🔍 Analyze") and user_query.strip():
        with st.spinner("Analyzing..."):
            try:
                result = gemini_engine.process_query(user_query)
                if result['data'] is not None and not result['data'].empty:
                    st.dataframe(result['data'], use_container_width=True)
                else:
                    st.warning("No data returned.")
                if result.get('insights'):
                    st.subheader("🧠 AI Insights")
                    st.markdown(result['insights'])
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_raw_data_tab():
    st.header("📋 Raw Data")
    data_type = st.selectbox("Select data to view:", ["Campaigns", "Ad Sets", "Ads", "Ad Insights"])
    try:
        if data_type == "Campaigns" and st.session_state.campaigns_df is not None:
            st.dataframe(st.session_state.campaigns_df, use_container_width=True)
        elif data_type == "Ad Sets" and st.session_state.adsets_df is not None:
            st.dataframe(st.session_state.adsets_df, use_container_width=True)
        elif data_type == "Ads" and st.session_state.ads_df is not None:
            st.dataframe(st.session_state.ads_df, use_container_width=True)
        elif data_type == "Ad Insights" and st.session_state.insights_df is not None:
            st.dataframe(st.session_state.insights_df, use_container_width=True)
        else:
            st.info("No data available. Fetch or load data first.")
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")

def show_welcome_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ## 🚀 Welcome to Facebook Ads Analytics

        Get started by:
        1. **Enter your Facebook Ads Account ID** in the sidebar
        2. **Fetch fresh data** from Facebook Marketing API, or
        3. **Load existing data** from the database

        Once data is loaded, you can:
        - 📊 View comprehensive analytics dashboards
        - 🧠 Ask natural language questions about your data
        - 📈 Explore interactive charts and visualizations

        ### Features:
        - 🔄 Real-time data fetching with pagination
        - 📀 PostgreSQL database storage
        - 🧠 AI-powered querying with Google Gemini
        - 📱 Interactive dashboards and charts
        """)

if __name__ == "__main__":
    main()
