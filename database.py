
# import os
# from dotenv import load_dotenv
# load_dotenv()
# import pandas as pd
# import json
# from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Float, DateTime, Text
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import SQLAlchemyError
# import uuid
# from datetime import datetime
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class DatabaseManager:
#     def __init__(self):
#         self.engine = self._create_engine()
#         self.metadata = MetaData()
#         self._define_tables()
#         self._create_tables()
#         Session = sessionmaker(bind=self.engine)
#         self.session = Session()

#     def _create_engine(self):
#         try:
#             database_url = os.getenv('DATABASE_URL')
#             if database_url and database_url.startswith('postgres://'):
#                 database_url = database_url.replace('postgres://', 'postgresql://', 1)
#             if not database_url:
#                 host = os.getenv('PGHOST', 'localhost')
#                 port = os.getenv('PGPORT', '5432')
#                 database = os.getenv('PGDATABASE', 'facebookdb')
#                 username = os.getenv('PGUSER', 'postgres')
#                 password = os.getenv('PGPASSWORD', '')
#                 database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
#             return create_engine(database_url)
#         except Exception as e:
#             logger.error(f"Error creating engine: {e}")
#             raise

#     def _define_tables(self):
#         self.ads_table = Table('ads', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('campaign_id', String),
#             Column('adset_id', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('account_id', String),
#             Column('impressions', Integer),
#             Column('clicks', Integer),
#             Column('spend', Float),
#             Column('reach', Integer),
#             Column('frequency', Float),
#             Column('cpm', Float),
#             Column('cpc', Float),
#             Column('ctr', Float),
#             Column('cpp', Float),
#             Column('actions', JSONB),
#             Column('cost_per_action_type', JSONB),
#             Column('date_start', String),
#             Column('date_stop', String),
#             Column('ad_creative_id', String),
#             Column('creative', JSONB),
#             Column('objective', String),
#             Column('buying_type', String),
#             Column('optimization_goal', String),
#             Column('bid_strategy', String),
#             Column('attribution_setting', String),
#             Column('conversion_values', JSONB),
#             Column('website_purchase_roas', JSONB),
#             Column('action_values', JSONB),
#             Column('inline_link_clicks', Integer),
            
#         )

#         self.campaigns_table = Table('campaigns', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('objective', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('start_time', String),
#             Column('stop_time', String),
#             Column('budget_remaining', String),
#             Column('daily_budget', String),
#             Column('lifetime_budget', String),
#             Column('account_id', String),
#             Column('buying_type', String),
#             Column('spend_cap', String),
#             Column('special_ad_categories', JSONB),
#             Column('bid_strategy', String)
#         )

#         self.adsets_table = Table('adsets', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('campaign_id', String),
#             Column('optimization_goal', String),
#             Column('billing_event', String),
#             Column('bid_amount', String),
#             Column('daily_budget', String),
#             Column('lifetime_budget', String),
#             Column('start_time', String),
#             Column('end_time', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('account_id', String),
#             Column('targeting', JSONB),
#             Column('pacing_type', JSONB),
#             Column('attribution_spec', JSONB),
#             Column('bid_strategy', String),
#             Column('promoted_object', JSONB),
#             Column('frequency_cap', String),
#             Column('frequency_control_specs', JSONB)
#         )

#     def _create_tables(self):
#         self.metadata.create_all(self.engine)

#     def store_campaigns(self, campaigns: list):
#         self._bulk_insert(self.campaigns_table, campaigns)

#     def store_adsets(self, adsets: list):
#         self._bulk_insert(self.adsets_table, adsets)

#     def store_ads(self, ads: list):
#         self._bulk_insert(self.ads_table, ads)

#     def _bulk_insert(self, table, records: list):
#         try:
#             with self.engine.begin() as conn:
#                 conn.execute(table.delete())
#                 conn.execute(table.insert(), records)
#                 logger.info(f"Inserted {len(records)} records into {table.name}")
#         except SQLAlchemyError as e:
#             logger.error(f"Error inserting into {table.name}: {str(e)}")

#     def get_campaigns(self):
#         return self._fetch_all(self.campaigns_table)

#     def get_adsets(self):
#         return self._fetch_all(self.adsets_table)

#     def get_ads(self):
#         return self._fetch_all(self.ads_table)

#     def _fetch_all(self, table):
#         with self.engine.connect() as conn:
#             result = conn.execute(table.select())
#             return [dict(row._mapping) for row in result]

#     def close(self):
#         try:
#             self.session.close()
#             self.engine.dispose()
#         except Exception as e:
#             logger.error(f"Error closing database connection: {e}")

#     def execute_query(self, query):
#         """Execute a SQL SELECT query and return a pandas DataFrame."""
#         try:
#             with self.engine.connect() as conn:
#                 result = pd.read_sql(text(query), conn)
#                 return result
#         except Exception as e:
#             logger.error(f"Error executing query: {e}")
#             raise


#     def get_schema_info(self):
#         """Return basic schema info used for Gemini query generation"""
#         return {
#             'ads': {
#                 'table': 'ads',
#                 'columns': [col.name for col in self.ads_table.columns],
#                 'description': 'Facebook Ads with performance metrics and creative data'
#             },
#             'campaigns': {
#                 'table': 'campaigns',
#                 'columns': [col.name for col in self.campaigns_table.columns],
#                 'description': 'Campaign metadata and configuration'
#             },
#             'adsets': {
#                 'table': 'adsets',
#                 'columns': [col.name for col in self.adsets_table.columns],
#                 'description': 'Ad Set configurations including targeting and pacing'
#             }
#         }

# database.py


import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import TIMESTAMP, DATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        try:
            self.engine = self._create_engine()
            self.metadata = MetaData()
            self._define_tables()
            self._create_tables()
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("DatabaseManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseManager: {e}")
            raise

    def _create_engine(self):
        try:
            url = os.getenv('DATABASE_URL')
            if url and url.startswith('postgres://'):
                url = url.replace('postgres://', 'postgresql://', 1)
            if not url:
                url = f"postgresql://{os.getenv('PGUSER', 'postgres')}:{os.getenv('PGPASSWORD', '')}@" \
                      f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/" \
                      f"{os.getenv('PGDATABASE', 'facebookdb')}"
            
            engine = create_engine(url, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
            return engine
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            raise

    def _define_tables(self):
        self.campaigns_table = Table('campaigns', self.metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('status', String),
            Column('objective', String),
            Column('created_time', TIMESTAMP),     # ⬅️ Changed
            Column('updated_time', TIMESTAMP),     # ⬅️ Changed
            Column('start_time', TIMESTAMP),       # ⬅️ Changed
            Column('stop_time', TIMESTAMP),        # ⬅️ Changed
            Column('budget_remaining', Float),
            Column('daily_budget', Float),
            Column('lifetime_budget', Float),
            Column('account_id', String),
            Column('buying_type', String),
            Column('spend_cap', String),
            Column('special_ad_categories', JSONB),
            Column('bid_strategy', String)
        )

        self.adsets_table = Table('adsets', self.metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('status', String),
            Column('campaign_id', String),
            Column('optimization_goal', String),
            Column('billing_event', String),
            Column('bid_amount', Float),
            Column('daily_budget', Float),
            Column('lifetime_budget', Float),
            Column('start_time', TIMESTAMP),       # ⬅️ Changed
            Column('end_time', TIMESTAMP),         # ⬅️ Changed
            Column('created_time', TIMESTAMP),     # ⬅️ Changed
            Column('updated_time', TIMESTAMP),     # ⬅️ Changed
            Column('account_id', String),
            Column('targeting', JSONB),
            Column('pacing_type', JSONB),
            Column('attribution_spec', JSONB),
            Column('bid_strategy', String),
            Column('promoted_object', JSONB),
            Column('frequency_cap', String),
            Column('frequency_control_specs', JSONB)
        )

        self.ads_table = Table('ads', self.metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('status', String),
            Column('campaign_id', String),
            Column('adset_id', String),
            Column('created_time', TIMESTAMP),     # ⬅️ Changed
            Column('updated_time', TIMESTAMP),     # ⬅️ Changed
            Column('account_id', String),
            Column('objective', String),
            Column('buying_type', String),
            Column('optimization_goal', String),
            Column('bid_strategy', String),
            Column('attribution_setting', String),
            Column('ad_creative_id', String),
            Column('creative', JSONB)
        )

        self.ad_insights_table = Table('ad_insights', self.metadata,
            Column('ad_id', String),
            Column('campaign_id', String),
            Column('date_start', DATE),            # ⬅️ Changed
            Column('date_stop', DATE),             # ⬅️ Changed
            Column('spend', Float),
            Column('impressions', Integer),
            Column('clicks', Integer),
            Column('reach', Integer),
            Column('frequency', Float),
            Column('cpm', Float),
            Column('cpc', Float),
            Column('ctr', Float),
            Column('cpp', Float),
            Column('conversion_values', JSONB)
        )

        self.campaign_insights_table = Table('campaign_insights', self.metadata,
            Column('campaign_id', String),
            Column('date_start', DATE),            # ⬅️ Changed
            Column('date_stop', DATE),             # ⬅️ Changed
            Column('spend', Float),
            Column('impressions', Integer),
            Column('clicks', Integer),
            Column('reach', Integer),
            Column('conversions', Integer)
        )

    def _create_tables(self):
        try:
            self.metadata.create_all(self.engine)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def store_campaigns(self, campaigns):
        if not campaigns:
            logger.warning("No campaigns to store")
            return
        self._bulk_insert(self.campaigns_table, campaigns)

    def store_adsets(self, adsets):
        if not adsets:
            logger.warning("No adsets to store")
            return
        self._bulk_insert(self.adsets_table, adsets)

    def store_ads(self, ads):
        if not ads:
            logger.warning("No ads to store")
            return
        self._bulk_insert(self.ads_table, ads)

    def store_ad_insights(self, insights):
        if not insights:
            logger.warning("No insights to store")
            return
        self._bulk_insert(self.ad_insights_table, insights)

    def store_campaign_insights(self, insights):
        if not insights:
            logger.warning("No campaign insights to store")
            return
        self._bulk_insert(self.campaign_insights_table, insights)

    def _bulk_insert(self, table, records):
        try:
            logger.info(f"Attempting to insert {len(records)} records into {table.name}")
            cleaned_records = []
            table_columns = [col.name for col in table.columns]

            for record in records:
                cleaned_record = {col: record.get(col, None) for col in table_columns}
                cleaned_records.append(cleaned_record)


            with self.engine.begin() as conn:
                conn.execute(table.delete())  # Remove old records
                if cleaned_records:
                    conn.execute(table.insert(), cleaned_records)
                    logger.info(f"Inserted {len(cleaned_records)} records into {table.name}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error inserting into {table.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error inserting into {table.name}: {e}")
            raise

    def get_campaigns(self):
        return self._fetch_all(self.campaigns_table)

    def get_adsets(self):
        return self._fetch_all(self.adsets_table)

    def get_ads(self):
        return self._fetch_all(self.ads_table)

    def get_ad_insights(self):
        return self._fetch_all(self.ad_insights_table)

    def get_campaign_insights(self):
        return self._fetch_all(self.campaign_insights_table)

    def _fetch_all(self, table):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(table.select())
                records = [dict(row._mapping) for row in result]
                logger.info(f"Fetched {len(records)} records from {table.name}")
                return records
        except Exception as e:
            logger.error(f"Error fetching from {table.name}: {e}")
            return []

    def execute_query(self, query):
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(text(query), conn)
                return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def get_schema_info(self):
        return {
            'campaigns': {
                'table': 'campaigns',
                'columns': [col.name for col in self.campaigns_table.columns],
                'description': 'Campaign metadata only'
            },
            'adsets': {
                'table': 'adsets',
                'columns': [col.name for col in self.adsets_table.columns],
                'description': 'Ad Set configurations'
            },
            'ads': {
                'table': 'ads',
                'columns': [col.name for col in self.ads_table.columns],
                'description': 'Ad metadata only'
            },
            'ad_insights': {
                'table': 'ad_insights',
                'columns': [col.name for col in self.ad_insights_table.columns],
                'description': 'Performance metrics by ad and date'
            },
            'campaign_insights': {
                'table': 'campaign_insights',
                'columns': [col.name for col in self.campaign_insights_table.columns],
                'description': 'Performance metrics aggregated at campaign level'
            }
        }

    def close(self):
        try:
            if hasattr(self, 'session'):
                self.session.close()
            if hasattr(self, 'engine'):
                self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)

# import os
# from dotenv import load_dotenv
# load_dotenv()
# import pandas as pd
# from datetime import datetime
# from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, text, Date
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import SQLAlchemyError
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class DatabaseManager:
#     def __init__(self):
#         try:
#             self.engine = self._create_engine()
#             self.metadata = MetaData()
#             self._define_tables()
#             self._create_tables()
#             Session = sessionmaker(bind=self.engine)
#             self.session = Session()
#             logger.info("DatabaseManager initialized successfully")
#         except Exception as e:
#             logger.error(f"Failed to initialize DatabaseManager: {e}")
#             raise

#     def _create_engine(self):
#         try:
#             url = os.getenv('DATABASE_URL')
#             if url and url.startswith('postgres://'):
#                 url = url.replace('postgres://', 'postgresql://', 1)
#             if not url:
#                 url = f"postgresql://{os.getenv('PGUSER', 'postgres')}:{os.getenv('PGPASSWORD', '')}@" \
#                       f"{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/" \
#                       f"{os.getenv('PGDATABASE', 'facebookdb')}"
            
#             engine = create_engine(url, echo=False)
#             with engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#                 logger.info("Database connection successful")
#             return engine
#         except Exception as e:
#             logger.error(f"Error creating database engine: {e}")
#             raise

#     def _define_tables(self):
#         self.campaigns_table = Table('campaigns', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('objective', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('start_time', String),
#             Column('stop_time', String),
#             Column('budget_remaining', Float),
#             Column('daily_budget', Float),
#             Column('lifetime_budget', Float),
#             Column('account_id', String),
#             Column('buying_type', String),
#             Column('spend_cap', String),
#             Column('special_ad_categories', JSONB),
#             Column('bid_strategy', String)
#         )

#         self.adsets_table = Table('adsets', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('campaign_id', String),
#             Column('optimization_goal', String),
#             Column('billing_event', String),
#             Column('bid_amount', Float),
#             Column('daily_budget', Float),
#             Column('lifetime_budget', Float),
#             Column('start_time', String),
#             Column('end_time', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('account_id', String),
#             Column('targeting', JSONB),
#             Column('pacing_type', JSONB),
#             Column('attribution_spec', JSONB),
#             Column('bid_strategy', String),
#             Column('promoted_object', JSONB),
#             Column('frequency_cap', String),
#             Column('frequency_control_specs', JSONB)
#         )

#         self.ads_table = Table('ads', self.metadata,
#             Column('id', String, primary_key=True),
#             Column('name', String),
#             Column('status', String),
#             Column('campaign_id', String),
#             Column('adset_id', String),
#             Column('created_time', String),
#             Column('updated_time', String),
#             Column('account_id', String),
#             Column('objective', String),
#             Column('buying_type', String),
#             Column('optimization_goal', String),
#             Column('bid_strategy', String),
#             Column('attribution_setting', String),
#             Column('ad_creative_id', String),
#             Column('creative', JSONB)
#         )

#         self.ad_insights_table = Table('ad_insights', self.metadata,
#             Column('ad_id', String),
#             Column('campaign_id', String),
#             Column('date_start', Date),
#             Column('date_stop', Date),
#             Column('spend', Float),
#             Column('impressions', Integer),
#             Column('clicks', Integer),
#             Column('reach', Integer),
#             Column('frequency', Float),
#             Column('cpm', Float),
#             Column('cpc', Float),
#             Column('ctr', Float),
#             Column('cpp', Float),
#             Column('conversion_values', JSONB)
#         )

#         self.campaign_insights_table = Table('campaign_insights', self.metadata,
#             Column('campaign_id', String),
#             Column('date_start', Date),
#             Column('date_stop', Date),
#             Column('spend', Float),
#             Column('impressions', Integer),
#             Column('clicks', Integer),
#             Column('reach', Integer),
#             Column('conversions', Integer)
#         )

#     def _create_tables(self):
#         try:
#             self.metadata.create_all(self.engine)
#             logger.info("Tables created successfully")
#         except Exception as e:
#             logger.error(f"Error creating tables: {e}")
#             raise

#     def _parse_dates(self, record, fields):
#         for field in fields:
#             if field in record and isinstance(record[field], str):
#                 try:
#                     record[field] = datetime.strptime(record[field], "%Y-%m-%d").date()
#                 except Exception as e:
#                     logger.warning(f"Failed to parse {field}: {e}")
#         return record

#     def store_campaigns(self, campaigns):
#         if not campaigns:
#             logger.warning("No campaigns to store")
#             return
#         self._bulk_insert(self.campaigns_table, campaigns)

#     def store_adsets(self, adsets):
#         if not adsets:
#             logger.warning("No adsets to store")
#             return
#         self._bulk_insert(self.adsets_table, adsets)

#     def store_ads(self, ads):
#         if not ads:
#             logger.warning("No ads to store")
#             return
#         self._bulk_insert(self.ads_table, ads)

#     def store_ad_insights(self, insights):
#         if not insights:
#             logger.warning("No ad insights to store")
#             return
#         for record in insights:
#             self._parse_dates(record, ['date_start', 'date_stop'])
#         self._bulk_insert(self.ad_insights_table, insights)

#     def store_campaign_insights(self, insights):
#         if not insights:
#             logger.warning("No campaign insights to store")
#             return
#         for record in insights:
#             self._parse_dates(record, ['date_start', 'date_stop'])
#         self._bulk_insert(self.campaign_insights_table, insights)

#     def _bulk_insert(self, table, records):
#         try:
#             logger.info(f"Inserting {len(records)} records into {table.name}")
#             cleaned_records = []
#             table_columns = [col.name for col in table.columns]

#             for record in records:
#                 cleaned_record = {col: record.get(col, None) for col in table_columns}
#                 cleaned_records.append(cleaned_record)

#             with self.engine.begin() as conn:
#                 conn.execute(table.delete())  # Clean insert
#                 if cleaned_records:
#                     conn.execute(table.insert(), cleaned_records)
#                     logger.info(f"Inserted into {table.name}")
#         except SQLAlchemyError as e:
#             logger.error(f"SQLAlchemy error inserting into {table.name}: {e}")
#             raise
#         except Exception as e:
#             logger.error(f"Unexpected error inserting into {table.name}: {e}")
#             raise

#     def get_campaigns(self):
#         return self._fetch_all(self.campaigns_table)

#     def get_adsets(self):
#         return self._fetch_all(self.adsets_table)

#     def get_ads(self):
#         return self._fetch_all(self.ads_table)

#     def get_ad_insights(self):
#         return self._fetch_all(self.ad_insights_table)

#     def get_campaign_insights(self):
#         return self._fetch_all(self.campaign_insights_table)

#     def _fetch_all(self, table):
#         try:
#             with self.engine.connect() as conn:
#                 result = conn.execute(table.select())
#                 records = [dict(row._mapping) for row in result]
#                 logger.info(f"Fetched {len(records)} records from {table.name}")
#                 return records
#         except Exception as e:
#             logger.error(f"Error fetching from {table.name}: {e}")
#             return []

#     def execute_query(self, query):
#         try:
#             with self.engine.connect() as conn:
#                 result = pd.read_sql(text(query), conn)
#                 return result
#         except Exception as e:
#             logger.error(f"Error executing query: {e}")
#             raise

#     def get_schema_info(self):
#         return {
#             'campaigns': {
#                 'table': 'campaigns',
#                 'columns': [col.name for col in self.campaigns_table.columns],
#                 'description': 'Campaign metadata only'
#             },
#             'adsets': {
#                 'table': 'adsets',
#                 'columns': [col.name for col in self.adsets_table.columns],
#                 'description': 'Ad Set configurations'
#             },
#             'ads': {
#                 'table': 'ads',
#                 'columns': [col.name for col in self.ads_table.columns],
#                 'description': 'Ad metadata only'
#             },
#             'ad_insights': {
#                 'table': 'ad_insights',
#                 'columns': [col.name for col in self.ad_insights_table.columns],
#                 'description': 'Performance metrics by ad and date'
#             },
#             'campaign_insights': {
#                 'table': 'campaign_insights',
#                 'columns': [col.name for col in self.campaign_insights_table.columns],
#                 'description': 'Performance metrics aggregated at campaign level'
#             }
#         }

#     def close(self):
#         try:
#             if hasattr(self, 'session'):
#                 self.session.close()
#             if hasattr(self, 'engine'):
#                 self.engine.dispose()
#             logger.info("Database connections closed")
#         except Exception as e:
#             logger.error(f"Error closing database connections: {e}")

#     def test_connection(self):
#         try:
#             with self.engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))
#             return True, "Connection successful"
#         except Exception as e:
#             return False, str(e)
