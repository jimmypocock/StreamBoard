"""
Google AdSense Management API v2 integration with multi-account support
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import settings
from utils.auth import OAuth2Manager
from services.base_service import MultiAccountService
import numpy as np


class GoogleAdSenseService(MultiAccountService):
    """Service for interacting with Google AdSense Management API v2 - Multiple Accounts"""
    
    def __init__(self):
        # Get account configurations
        accounts_config = settings.get_google_adsense_accounts()
        super().__init__(accounts_config)
    
    def _init_account(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a single AdSense account client"""
        oauth_manager = OAuth2Manager(
            client_secrets_file=config['client_secrets_path'],
            scopes=['https://www.googleapis.com/auth/adsense.readonly'],
            token_file=config.get('token_path', f"token_{config['name']}.json")
        )
        
        credentials = oauth_manager.get_credentials()
        service = build('adsense', 'v2', credentials=credentials)
        
        # Get account ID if not provided
        account_id = config.get('account_id')
        if not account_id:
            try:
                accounts = service.accounts().list().execute()
                if accounts.get('accounts'):
                    account_id = accounts['accounts'][0]['name']
                    # Extract just the ID part (format: accounts/pub-XXXXX)
                    account_id = account_id.split('/')[-1]
            except Exception:
                pass
        
        return {
            'service': service,
            'oauth_manager': oauth_manager,
            'account_id': account_id
        }
    
    def get_account_summary(self, account_name: str) -> Dict[str, Any]:
        """Get summary metrics for a specific account"""
        account = self.get_account(account_name)
        if not account or account['status'] != 'active':
            return {'error': f'Account {account_name} not active'}
        
        # Get basic metrics for summary
        earnings = self.get_earnings_overview(account_name, days_back=7)
        return {
            'name': account_name,
            'earnings': earnings.get('earnings', 0),
            'clicks': earnings.get('clicks', 0),
            'rpm': earnings.get('rpm', 0)
        }
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_earnings_overview(_self, account_name: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Get earnings overview metrics for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            Dictionary with earnings overview
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_earnings_overview()
        
        try:
            client_data = account['client']
            service = client_data['service']
            account_id = client_data['account_id']
            
            if not account_id:
                return _self._get_mock_earnings_overview()
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Generate report
            report_request = service.accounts().reports().generate(
                account=f'accounts/{account_id}',
                dateRange=f'{start_date.isoformat()}/{end_date.isoformat()}',
                dimensions=[],
                metrics=[
                    'ESTIMATED_EARNINGS',
                    'PAGE_VIEWS',
                    'CLICKS',
                    'PAGE_VIEWS_CTR',
                    'PAGE_VIEWS_RPM',
                    'IMPRESSIONS'
                ]
            )
            
            response = report_request.execute()
            
            # Extract totals
            if response.get('rows'):
                cells = response['rows'][0]['cells']
                return {
                    'earnings': float(cells[0].get('value', 0)),
                    'earnings_change': 0,  # TODO: Calculate actual change
                    'pageviews': int(cells[1].get('value', 0)),
                    'pageviews_change': 0,
                    'clicks': int(cells[2].get('value', 0)),
                    'clicks_change': 0,
                    'ctr': float(cells[3].get('value', 0)) * 100,
                    'ctr_change': 0,
                    'rpm': float(cells[4].get('value', 0)),
                    'rpm_change': 0,
                    'impressions': int(cells[5].get('value', 0))
                }
            
            return _self._get_mock_earnings_overview()
            
        except HttpError as e:
            if e.resp.status == 403:
                st.error(f"Access denied for {account_name}. Please ensure AdSense API is enabled and you have proper permissions.")
            else:
                st.error(f"Error fetching AdSense data for {account_name}: {str(e)}")
            return _self._get_mock_earnings_overview()
        except Exception as e:
            st.error(f"Error fetching AdSense data for {account_name}: {str(e)}")
            return _self._get_mock_earnings_overview()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_earnings(_self, days_back: int = 30) -> Dict[str, Any]:
        """Get earnings overview for all accounts combined"""
        all_earnings = {}
        
        for account_name in _self.list_active_account_names():
            all_earnings[account_name] = _self.get_earnings_overview(account_name, days_back)
        
        if not all_earnings:
            return _self._get_mock_earnings_overview()
        
        # Aggregate metrics
        metric_keys = ['earnings', 'pageviews', 'clicks', 'ctr', 'rpm', 'impressions']
        aggregated = _self.aggregate_metrics(all_earnings, metric_keys)
        
        # Add change percentages
        aggregated['earnings_change'] = 0
        aggregated['pageviews_change'] = 0
        aggregated['clicks_change'] = 0
        aggregated['ctr_change'] = 0
        aggregated['rpm_change'] = 0
        
        return aggregated
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_daily_earnings(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get daily earnings data for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with daily earnings
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_daily_earnings(days_back)
        
        try:
            client_data = account['client']
            service = client_data['service']
            account_id = client_data['account_id']
            
            if not account_id:
                return _self._get_mock_daily_earnings(days_back)
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Generate report with DATE dimension
            report_request = service.accounts().reports().generate(
                account=f'accounts/{account_id}',
                dateRange=f'{start_date.isoformat()}/{end_date.isoformat()}',
                dimensions=['DATE'],
                metrics=[
                    'ESTIMATED_EARNINGS',
                    'PAGE_VIEWS',
                    'CLICKS',
                    'PAGE_VIEWS_CTR',
                    'PAGE_VIEWS_RPM'
                ],
                orderBy=['DATE']
            )
            
            response = report_request.execute()
            
            # Convert to DataFrame
            data = []
            if response.get('rows'):
                for row in response['rows']:
                    cells = row['cells']
                    data.append({
                        'date': cells[0].get('value'),
                        'earnings': float(cells[1].get('value', 0)),
                        'pageviews': int(cells[2].get('value', 0)),
                        'clicks': int(cells[3].get('value', 0)),
                        'ctr': float(cells[4].get('value', 0)),
                        'rpm': float(cells[5].get('value', 0)),
                        'account': account_name
                    })
            
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                return df
            
            return _self._get_mock_daily_earnings(days_back)
            
        except Exception as e:
            st.error(f"Error fetching daily earnings for {account_name}: {str(e)}")
            return _self._get_mock_daily_earnings(days_back)
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_daily_earnings(_self, days_back: int = 30) -> pd.DataFrame:
        """Get daily earnings for all accounts"""
        all_earnings = {}
        
        for account_name in _self.list_active_account_names():
            all_earnings[account_name] = _self.get_daily_earnings(account_name, days_back)
        
        if not all_earnings:
            return _self._get_mock_daily_earnings(days_back)
        
        # Combine all dataframes
        combined = _self.combine_dataframes(all_earnings, add_account_column=False)
        
        # Aggregate by date
        if not combined.empty and 'date' in combined.columns:
            aggregated = combined.groupby('date').agg({
                'earnings': 'sum',
                'pageviews': 'sum',
                'clicks': 'sum',
                'ctr': 'mean',
                'rpm': 'mean'
            }).reset_index()
            return aggregated
        
        return combined
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_earnings_by_site(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get earnings breakdown by site for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with site earnings
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_site_earnings()
        
        try:
            client_data = account['client']
            service = client_data['service']
            account_id = client_data['account_id']
            
            if not account_id:
                return _self._get_mock_site_earnings()
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Generate report with DOMAIN_NAME dimension
            report_request = service.accounts().reports().generate(
                account=f'accounts/{account_id}',
                dateRange=f'{start_date.isoformat()}/{end_date.isoformat()}',
                dimensions=['DOMAIN_NAME'],
                metrics=[
                    'ESTIMATED_EARNINGS',
                    'PAGE_VIEWS',
                    'CLICKS',
                    'PAGE_VIEWS_RPM'
                ],
                orderBy=['-ESTIMATED_EARNINGS']
            )
            
            response = report_request.execute()
            
            # Convert to DataFrame
            data = []
            if response.get('rows'):
                for row in response['rows']:
                    cells = row['cells']
                    data.append({
                        'site': cells[0].get('value', 'Unknown'),
                        'earnings': float(cells[1].get('value', 0)),
                        'pageviews': int(cells[2].get('value', 0)),
                        'clicks': int(cells[3].get('value', 0)),
                        'rpm': float(cells[4].get('value', 0)),
                        'account': account_name
                    })
            
            if data:
                return pd.DataFrame(data)
            
            return _self._get_mock_site_earnings()
            
        except Exception as e:
            st.error(f"Error fetching site earnings for {account_name}: {str(e)}")
            return _self._get_mock_site_earnings()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_site_earnings(_self, days_back: int = 30) -> pd.DataFrame:
        """Get site earnings for all accounts"""
        all_sites = {}
        
        for account_name in _self.list_active_account_names():
            all_sites[account_name] = _self.get_earnings_by_site(account_name, days_back)
        
        if not all_sites:
            return _self._get_mock_site_earnings()
        
        # Combine all dataframes - keep account info for sites
        combined = _self.combine_dataframes(all_sites, add_account_column=False)
        
        return combined
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_top_performing_pages(_self, account_name: str, days_back: int = 30, limit: int = 10) -> pd.DataFrame:
        """
        Get top performing pages by earnings for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            limit: Number of pages to return
            
        Returns:
            DataFrame with top pages
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_top_pages()
        
        try:
            client_data = account['client']
            service = client_data['service']
            account_id = client_data['account_id']
            
            if not account_id:
                return _self._get_mock_top_pages()
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Generate report with PAGE_URL dimension
            report_request = service.accounts().reports().generate(
                account=f'accounts/{account_id}',
                dateRange=f'{start_date.isoformat()}/{end_date.isoformat()}',
                dimensions=['PAGE_URL'],
                metrics=[
                    'ESTIMATED_EARNINGS',
                    'PAGE_VIEWS',
                    'PAGE_VIEWS_RPM'
                ],
                orderBy=['-ESTIMATED_EARNINGS'],
                limit=limit
            )
            
            response = report_request.execute()
            
            # Convert to DataFrame
            data = []
            if response.get('rows'):
                for row in response['rows']:
                    cells = row['cells']
                    url = cells[0].get('value', 'Unknown')
                    # Truncate long URLs for display
                    display_url = url if len(url) <= 50 else url[:47] + '...'
                    data.append({
                        'page': display_url,
                        'full_url': url,
                        'earnings': float(cells[1].get('value', 0)),
                        'pageviews': int(cells[2].get('value', 0)),
                        'rpm': float(cells[3].get('value', 0)),
                        'account': account_name
                    })
            
            if data:
                return pd.DataFrame(data)
            
            return _self._get_mock_top_pages()
            
        except Exception as e:
            st.error(f"Error fetching top pages for {account_name}: {str(e)}")
            return _self._get_mock_top_pages()
    
    # Mock data methods for fallback
    def _get_mock_earnings_overview(self) -> Dict[str, Any]:
        """Return mock earnings overview"""
        return {
            'earnings': 543.21,
            'earnings_change': 12.5,
            'pageviews': 123456,
            'pageviews_change': 8.3,
            'clicks': 2345,
            'clicks_change': -3.2,
            'ctr': 1.9,
            'ctr_change': -0.2,
            'rpm': 4.40,
            'rpm_change': 5.2,
            'impressions': 145678
        }
    
    def _get_mock_daily_earnings(self, days_back: int) -> pd.DataFrame:
        """Generate mock daily earnings data"""
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        data = []
        
        for date in dates:
            data.append({
                'date': date,
                'earnings': np.random.uniform(10, 30),
                'pageviews': np.random.randint(3000, 6000),
                'clicks': np.random.randint(50, 150),
                'ctr': np.random.uniform(1.5, 2.5),
                'rpm': np.random.uniform(3.5, 5.5)
            })
        
        return pd.DataFrame(data)
    
    def _get_mock_site_earnings(self) -> pd.DataFrame:
        """Return mock site earnings data"""
        return pd.DataFrame([
            {'site': 'example.com', 'earnings': 345.67, 'pageviews': 78234, 'clicks': 1523, 'rpm': 4.42},
            {'site': 'blog.example.com', 'earnings': 123.45, 'pageviews': 34567, 'clicks': 567, 'rpm': 3.57},
            {'site': 'shop.example.com', 'earnings': 74.09, 'pageviews': 12345, 'clicks': 255, 'rpm': 6.00}
        ])
    
    def _get_mock_top_pages(self) -> pd.DataFrame:
        """Return mock top pages data"""
        return pd.DataFrame([
            {'page': '/best-products-2024', 'full_url': 'https://example.com/best-products-2024', 'earnings': 45.67, 'pageviews': 8234, 'rpm': 5.55},
            {'page': '/how-to-guide', 'full_url': 'https://example.com/how-to-guide', 'earnings': 34.23, 'pageviews': 7123, 'rpm': 4.81},
            {'page': '/reviews/product-x', 'full_url': 'https://example.com/reviews/product-x', 'earnings': 28.90, 'pageviews': 5432, 'rpm': 5.32},
            {'page': '/comparison', 'full_url': 'https://example.com/comparison', 'earnings': 23.45, 'pageviews': 4321, 'rpm': 5.43},
            {'page': '/tutorials', 'full_url': 'https://example.com/tutorials', 'earnings': 19.87, 'pageviews': 3987, 'rpm': 4.98}
        ])