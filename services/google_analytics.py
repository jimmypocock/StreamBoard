"""
Google Analytics GA4 Data API integration with multi-account support
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy,
    RunRealtimeReportRequest
)
from config.settings import settings
from utils.auth import CredentialsManager
from services.base_service import MultiAccountService
import numpy as np


class GoogleAnalyticsService(MultiAccountService):
    """Service for interacting with Google Analytics GA4 Data API - Multiple Properties"""
    
    def __init__(self):
        # Get account configurations
        accounts_config = settings.get_google_analytics_accounts()
        super().__init__(accounts_config)
    
    def _init_account(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a single GA4 property client"""
        credentials = CredentialsManager.get_service_account_credentials(
            credentials_path=config.get('credentials_path'),
            credentials_json=config.get('credentials_json'),
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        # Debug: Print service account email
        if hasattr(credentials, 'service_account_email'):
            print(f"DEBUG: Using service account: {credentials.service_account_email}")
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        property_id = config['property_id']
        print(f"DEBUG: Connecting to GA4 property: {property_id}")
        
        return {
            'client': client,
            'property_id': property_id
        }
    
    def get_account_summary(self, account_name: str) -> Dict[str, Any]:
        """Get summary metrics for a specific account"""
        account = self.get_account(account_name)
        if not account or account['status'] != 'active':
            return {'error': f'Account {account_name} not active'}
        
        # Get basic metrics for summary
        metrics = self.get_overview_metrics(account_name, days_back=7)
        return {
            'name': account_name,
            'users': metrics.get('users', 0),
            'sessions': metrics.get('sessions', 0),
            'pageviews': metrics.get('pageviews', 0)
        }
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_overview_metrics(_self, account_name: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Get overview metrics for a specific GA4 property
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            Dictionary with overview metrics
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_overview_metrics()
        
        try:
            client_data = account['client']
            client = client_data['client']
            property_id = client_data['property_id']
            
            request = RunReportRequest(
                property=f"properties/{property_id}",
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="engagementRate")
                ],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )]
            )
            
            response = client.run_report(request)
            
            # Extract metrics from response
            metrics = {}
            for i, metric_header in enumerate(response.metric_headers):
                value = response.rows[0].metric_values[i].value if response.rows else "0"
                metrics[metric_header.name] = float(value)
            
            return {
                'users': int(metrics.get('activeUsers', 0)),
                'users_change': 0,  # TODO: Calculate actual change
                'sessions': int(metrics.get('sessions', 0)),
                'sessions_change': 0,
                'pageviews': int(metrics.get('screenPageViews', 0)),
                'pageviews_change': 0,
                'bounce_rate': metrics.get('bounceRate', 0) * 100,
                'bounce_rate_change': 0,
                'avg_session_duration': metrics.get('averageSessionDuration', 0),
                'engagement_rate': metrics.get('engagementRate', 0) * 100
            }
            
        except Exception as e:
            st.error(f"Error fetching Google Analytics data for {account_name}: {str(e)}")
            return _self._get_mock_overview_metrics()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_overview(_self, days_back: int = 30) -> Dict[str, Any]:
        """Get overview metrics for all accounts combined"""
        all_metrics = {}
        
        for account_name in _self.list_active_account_names():
            all_metrics[account_name] = _self.get_overview_metrics(account_name, days_back)
        
        if not all_metrics:
            return _self._get_mock_overview_metrics()
        
        # Aggregate metrics
        metric_keys = ['users', 'sessions', 'pageviews', 'bounce_rate', 'avg_session_duration', 'engagement_rate']
        aggregated = _self.aggregate_metrics(all_metrics, metric_keys)
        
        # Add change percentages (would need previous period data)
        aggregated['users_change'] = 0
        aggregated['sessions_change'] = 0
        aggregated['pageviews_change'] = 0
        aggregated['bounce_rate_change'] = 0
        
        return aggregated
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_traffic_data(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get daily traffic data for a specific property
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with daily traffic metrics
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_traffic_data(days_back)
        
        try:
            client_data = account['client']
            client = client_data['client']
            property_id = client_data['property_id']
            
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate")
                ],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )],
                order_bys=[OrderBy(
                    dimension=OrderBy.DimensionOrderBy(dimension_name="date")
                )]
            )
            
            response = client.run_report(request)
            df = _self._process_response(response)
            df['account'] = account_name
            return df
            
        except Exception as e:
            st.error(f"Error fetching traffic data for {account_name}: {str(e)}")
            return _self._get_mock_traffic_data(days_back)
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_traffic(_self, days_back: int = 30) -> pd.DataFrame:
        """Get traffic data for all accounts"""
        all_traffic = {}
        
        for account_name in _self.list_active_account_names():
            all_traffic[account_name] = _self.get_traffic_data(account_name, days_back)
        
        if not all_traffic:
            return _self._get_mock_traffic_data(days_back)
        
        # Combine all dataframes
        combined = _self.combine_dataframes(all_traffic, add_account_column=False)
        
        # Aggregate by date
        if not combined.empty and 'date' in combined.columns:
            # Ensure numeric types for aggregation
            numeric_columns = ['activeUsers', 'sessions', 'screenPageViews', 'bounceRate']
            for col in numeric_columns:
                if col in combined.columns:
                    combined[col] = pd.to_numeric(combined[col], errors='coerce')
            
            aggregated = combined.groupby('date').agg({
                'activeUsers': 'sum',
                'sessions': 'sum',
                'screenPageViews': 'sum',
                'bounceRate': 'mean'
            }).reset_index()
            return aggregated
        
        return combined
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_device_data(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get device category breakdown for a specific property
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with device metrics
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_device_data()
        
        try:
            client_data = account['client']
            client = client_data['client']
            property_id = client_data['property_id']
            
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="deviceCategory")],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="bounceRate")
                ],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )]
            )
            
            response = client.run_report(request)
            df = _self._process_response(response)
            df['account'] = account_name
            return df
            
        except Exception as e:
            st.error(f"Error fetching device data for {account_name}: {str(e)}")
            return _self._get_mock_device_data()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_devices(_self, days_back: int = 30) -> pd.DataFrame:
        """Get device data for all accounts combined"""
        all_devices = {}
        
        for account_name in _self.list_active_account_names():
            all_devices[account_name] = _self.get_device_data(account_name, days_back)
        
        if not all_devices:
            return _self._get_mock_device_data()
        
        # Combine all dataframes
        combined = _self.combine_dataframes(all_devices, add_account_column=False)
        
        # Aggregate by device category
        if not combined.empty and 'deviceCategory' in combined.columns:
            # Ensure numeric types for aggregation
            numeric_columns = ['activeUsers', 'sessions', 'bounceRate']
            for col in numeric_columns:
                if col in combined.columns:
                    combined[col] = pd.to_numeric(combined[col], errors='coerce')
            
            aggregated = combined.groupby('deviceCategory').agg({
                'activeUsers': 'sum',
                'sessions': 'sum',
                'bounceRate': 'mean'
            }).reset_index()
            return aggregated
        
        return combined
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_top_pages(_self, account_name: str, days_back: int = 30, limit: int = 10) -> pd.DataFrame:
        """
        Get top pages by pageviews for a specific property
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            limit: Number of top pages to return
            
        Returns:
            DataFrame with top pages
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_top_pages()
        
        try:
            client_data = account['client']
            client = client_data['client']
            property_id = client_data['property_id']
            
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="pagePath")],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="activeUsers"),
                    Metric(name="averageSessionDuration")
                ],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )],
                order_bys=[OrderBy(
                    metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                    desc=True
                )],
                limit=limit
            )
            
            response = client.run_report(request)
            df = _self._process_response(response)
            df['account'] = account_name
            return df
            
        except Exception as e:
            st.error(f"Error fetching top pages for {account_name}: {str(e)}")
            return _self._get_mock_top_pages()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SHORT)
    def get_realtime_users(_self, account_name: str) -> int:
        """
        Get realtime active users for a specific property
        
        Args:
            account_name: Name of the account
            
        Returns:
            Number of realtime active users
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return 42  # Mock value
        
        try:
            client_data = account['client']
            client = client_data['client']
            property_id = client_data['property_id']
            
            request = RunRealtimeReportRequest(
                property=f"properties/{property_id}",
                metrics=[Metric(name="activeUsers")]
            )
            
            response = client.run_realtime_report(request)
            
            if response.rows:
                return int(response.rows[0].metric_values[0].value)
            return 0
            
        except Exception as e:
            st.error(f"Error fetching realtime data for {account_name}: {str(e)}")
            return 0
    
    def get_total_realtime_users(self) -> int:
        """Get total realtime users across all properties"""
        total = 0
        for account_name in self.list_active_account_names():
            total += self.get_realtime_users(account_name)
        return total
    
    def _process_response(self, response) -> pd.DataFrame:
        """Convert GA4 API response to pandas DataFrame"""
        data = []
        
        for row in response.rows:
            row_data = {}
            
            # Add dimensions
            for i, dim_header in enumerate(response.dimension_headers):
                row_data[dim_header.name] = row.dimension_values[i].value
            
            # Add metrics
            for i, metric_header in enumerate(response.metric_headers):
                value = row.metric_values[i].value
                # Convert to appropriate type
                if metric_header.type_ in ['TYPE_INTEGER', 'TYPE_CURRENCY']:
                    row_data[metric_header.name] = int(value)
                elif metric_header.type_ == 'TYPE_FLOAT':
                    row_data[metric_header.name] = float(value)
                else:
                    row_data[metric_header.name] = value
            
            data.append(row_data)
        
        return pd.DataFrame(data)
    
    # Mock data methods for fallback
    def _get_mock_overview_metrics(self) -> Dict[str, Any]:
        """Return mock overview metrics"""
        return {
            'users': 12543,
            'users_change': 15.3,
            'sessions': 18234,
            'sessions_change': 8.7,
            'pageviews': 45123,
            'pageviews_change': -2.1,
            'bounce_rate': 42.3,
            'bounce_rate_change': -5.2,
            'avg_session_duration': 156,
            'engagement_rate': 68.5
        }
    
    def _get_mock_traffic_data(self, days_back: int) -> pd.DataFrame:
        """Generate mock traffic data"""
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        data = []
        
        for date in dates:
            data.append({
                'date': date.strftime('%Y%m%d'),
                'activeUsers': np.random.randint(300, 600),
                'sessions': np.random.randint(400, 800),
                'screenPageViews': np.random.randint(1000, 2000),
                'bounceRate': np.random.uniform(0.35, 0.55)
            })
        
        return pd.DataFrame(data)
    
    def _get_mock_device_data(self) -> pd.DataFrame:
        """Return mock device data"""
        return pd.DataFrame([
            {'deviceCategory': 'desktop', 'activeUsers': 5234, 'sessions': 7123, 'bounceRate': 0.38},
            {'deviceCategory': 'mobile', 'activeUsers': 6543, 'sessions': 9234, 'bounceRate': 0.48},
            {'deviceCategory': 'tablet', 'activeUsers': 766, 'sessions': 877, 'bounceRate': 0.42}
        ])
    
    def _get_mock_top_pages(self) -> pd.DataFrame:
        """Return mock top pages data"""
        return pd.DataFrame([
            {'pagePath': '/', 'screenPageViews': 12543, 'activeUsers': 8234, 'averageSessionDuration': 143},
            {'pagePath': '/products', 'screenPageViews': 8234, 'activeUsers': 5123, 'averageSessionDuration': 234},
            {'pagePath': '/about', 'screenPageViews': 4532, 'activeUsers': 3234, 'averageSessionDuration': 98},
            {'pagePath': '/contact', 'screenPageViews': 2345, 'activeUsers': 1876, 'averageSessionDuration': 67},
            {'pagePath': '/blog', 'screenPageViews': 1987, 'activeUsers': 1234, 'averageSessionDuration': 189}
        ])