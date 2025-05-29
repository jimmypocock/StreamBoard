"""
AWS Cost Explorer and CloudWatch integration with multi-account support
"""
import streamlit as st
import pandas as pd
import boto3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from botocore.exceptions import ClientError, NoCredentialsError
from config.settings import settings
from services.base_service import MultiAccountService
import numpy as np


class AWSMetricsService(MultiAccountService):
    """Service for interacting with AWS Cost Explorer and CloudWatch - Multiple Accounts"""
    
    def __init__(self):
        # Get account configurations
        accounts_config = settings.get_aws_accounts()
        super().__init__(accounts_config)
    
    def _init_account(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize AWS clients for a single account"""
        # Create session with explicit credentials
        session = boto3.Session(
            aws_access_key_id=config['access_key_id'],
            aws_secret_access_key=config['secret_access_key'],
            region_name=config.get('region', 'us-east-1')
        )
        
        # Initialize clients
        return {
            'ce_client': session.client('ce', region_name='us-east-1'),  # Cost Explorer only in us-east-1
            'cloudwatch_client': session.client('cloudwatch'),
            'ec2_client': session.client('ec2'),
            's3_client': session.client('s3'),
            'rds_client': session.client('rds'),
            'region': config.get('region', 'us-east-1')
        }
    
    def get_account_summary(self, account_name: str) -> Dict[str, Any]:
        """Get summary metrics for a specific account"""
        account = self.get_account(account_name)
        if not account or account['status'] != 'active':
            return {'error': f'Account {account_name} not active'}
        
        # Get basic cost metrics for summary
        cost_overview = self.get_cost_overview(account_name, days_back=7)
        return {
            'name': account_name,
            'total_cost': cost_overview.get('total_cost', 0),
            'service_count': cost_overview.get('service_count', 0),
            'region': account['client'].get('region', 'us-east-1')
        }
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_cost_overview(_self, account_name: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Get AWS cost overview for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            Dictionary with cost overview
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_cost_overview()
        
        try:
            client_data = account['client']
            ce_client = client_data['ce_client']
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Get current period costs
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost', 'UnblendedCost'],
                GroupBy=[{
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }]
            )
            
            # Calculate total costs
            total_cost = 0
            service_costs = {}
            
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    if service in service_costs:
                        service_costs[service] += cost
                    else:
                        service_costs[service] = cost
            
            # Get forecast
            try:
                forecast_response = ce_client.get_cost_forecast(
                    TimePeriod={
                        'Start': end_date.strftime('%Y-%m-%d'),
                        'End': (end_date + timedelta(days=30)).strftime('%Y-%m-%d')
                    },
                    Metric='BLENDED_COST',
                    Granularity='MONTHLY'
                )
                forecast_total = float(forecast_response['Total']['Amount'])
            except:
                forecast_total = total_cost  # Use current as forecast if unavailable
            
            return {
                'total_cost': total_cost,
                'cost_change': 0,  # TODO: Calculate actual change
                'forecast_cost': forecast_total,
                'top_services': sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5],
                'service_count': len(service_costs),
                'account': account_name
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                st.error(f"Access denied to AWS Cost Explorer for {account_name}. Please ensure you have the necessary permissions.")
            else:
                st.error(f"AWS API error for {account_name}: {str(e)}")
            return _self._get_mock_cost_overview()
        except Exception as e:
            st.error(f"Error fetching AWS costs for {account_name}: {str(e)}")
            return _self._get_mock_cost_overview()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_cost_overview(_self, days_back: int = 30) -> Dict[str, Any]:
        """Get cost overview for all accounts combined"""
        all_costs = {}
        
        for account_name in _self.list_active_account_names():
            all_costs[account_name] = _self.get_cost_overview(account_name, days_back)
        
        if not all_costs:
            return _self._get_mock_cost_overview()
        
        # Aggregate total costs
        total_cost = sum(cost.get('total_cost', 0) for cost in all_costs.values())
        forecast_cost = sum(cost.get('forecast_cost', 0) for cost in all_costs.values())
        
        # Combine top services from all accounts
        all_services = {}
        for cost_data in all_costs.values():
            for service, cost in cost_data.get('top_services', []):
                all_services[service] = all_services.get(service, 0) + cost
        
        top_services = sorted(all_services.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_cost': total_cost,
            'cost_change': 0,
            'forecast_cost': forecast_cost,
            'top_services': top_services,
            'service_count': len(all_services),
            'account_breakdown': {name: cost.get('total_cost', 0) for name, cost in all_costs.items()}
        }
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_daily_costs(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get daily cost breakdown for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with daily costs
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_daily_costs(days_back)
        
        try:
            client_data = account['client']
            ce_client = client_data['ce_client']
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            
            data = []
            for result in response['ResultsByTime']:
                data.append({
                    'date': result['TimePeriod']['Start'],
                    'cost': float(result['Total']['BlendedCost']['Amount']),
                    'account': account_name
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df
            
        except Exception as e:
            st.error(f"Error fetching daily costs for {account_name}: {str(e)}")
            return _self._get_mock_daily_costs(days_back)
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_all_accounts_daily_costs(_self, days_back: int = 30) -> pd.DataFrame:
        """Get daily costs for all accounts"""
        all_costs = {}
        
        for account_name in _self.list_active_account_names():
            all_costs[account_name] = _self.get_daily_costs(account_name, days_back)
        
        if not all_costs:
            return _self._get_mock_daily_costs(days_back)
        
        # Combine all dataframes
        combined = _self.combine_dataframes(all_costs, add_account_column=False)
        
        # Aggregate by date
        if not combined.empty and 'date' in combined.columns:
            aggregated = combined.groupby('date').agg({
                'cost': 'sum'
            }).reset_index()
            return aggregated
        
        return combined
    
    @st.cache_data(ttl=settings.CACHE_TTL_SECONDS)
    def get_service_costs(_self, account_name: str, days_back: int = 30) -> pd.DataFrame:
        """
        Get costs by AWS service for a specific account
        
        Args:
            account_name: Name of the account
            days_back: Number of days to look back
            
        Returns:
            DataFrame with service costs
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_service_costs()
        
        try:
            client_data = account['client']
            ce_client = client_data['ce_client']
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[{
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }]
            )
            
            data = []
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    if cost > 0.01:  # Filter out negligible costs
                        data.append({
                            'service': service,
                            'cost': cost,
                            'usage': float(group['Metrics'].get('UsageQuantity', {}).get('Amount', 0)),
                            'account': account_name
                        })
            
            if data:
                df = pd.DataFrame(data)
                # Aggregate by service
                df = df.groupby(['service', 'account']).agg({
                    'cost': 'sum',
                    'usage': 'sum'
                }).reset_index()
                df = df.sort_values('cost', ascending=False)
                return df
            
            return _self._get_mock_service_costs()
            
        except Exception as e:
            st.error(f"Error fetching service costs for {account_name}: {str(e)}")
            return _self._get_mock_service_costs()
    
    @st.cache_data(ttl=settings.CACHE_TTL_SHORT)
    def get_resource_summary(_self, account_name: str) -> Dict[str, Any]:
        """
        Get summary of AWS resources for a specific account
        
        Args:
            account_name: Name of the account
            
        Returns:
            Dictionary with resource counts and status
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_resource_summary()
        
        client_data = account['client']
        summary = {
            'account': account_name,
            'region': client_data.get('region', 'us-east-1'),
            'ec2_instances': {'running': 0, 'stopped': 0, 'total': 0},
            's3_buckets': {'count': 0, 'total_size': 0},
            'rds_instances': {'count': 0, 'status': {}},
            'errors': []
        }
        
        # Get EC2 instances
        try:
            ec2_client = client_data['ec2_client']
            ec2_response = ec2_client.describe_instances()
            for reservation in ec2_response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    summary['ec2_instances']['total'] += 1
                    state = instance['State']['Name']
                    if state == 'running':
                        summary['ec2_instances']['running'] += 1
                    elif state == 'stopped':
                        summary['ec2_instances']['stopped'] += 1
        except Exception as e:
            summary['errors'].append(f"EC2: {str(e)}")
        
        # Get S3 buckets
        try:
            s3_client = client_data['s3_client']
            s3_response = s3_client.list_buckets()
            summary['s3_buckets']['count'] = len(s3_response.get('Buckets', []))
        except Exception as e:
            summary['errors'].append(f"S3: {str(e)}")
        
        # Get RDS instances
        try:
            rds_client = client_data['rds_client']
            rds_response = rds_client.describe_db_instances()
            summary['rds_instances']['count'] = len(rds_response.get('DBInstances', []))
            for db in rds_response.get('DBInstances', []):
                status = db['DBInstanceStatus']
                if status in summary['rds_instances']['status']:
                    summary['rds_instances']['status'][status] += 1
                else:
                    summary['rds_instances']['status'][status] = 1
        except Exception as e:
            summary['errors'].append(f"RDS: {str(e)}")
        
        return summary
    
    def get_all_accounts_resource_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get resource summary for all accounts"""
        all_resources = {}
        
        for account_name in self.list_active_account_names():
            all_resources[account_name] = self.get_resource_summary(account_name)
        
        return all_resources
    
    @st.cache_data(ttl=settings.CACHE_TTL_SHORT)
    def get_cloudwatch_alarms(_self, account_name: str) -> pd.DataFrame:
        """
        Get active CloudWatch alarms for a specific account
        
        Args:
            account_name: Name of the account
            
        Returns:
            DataFrame with alarm information
        """
        account = _self.get_account(account_name)
        if not account or account['status'] != 'active':
            return _self._get_mock_alarms()
        
        try:
            client_data = account['client']
            cloudwatch_client = client_data['cloudwatch_client']
            
            response = cloudwatch_client.describe_alarms(
                StateValue='ALARM',
                MaxRecords=100
            )
            
            data = []
            for alarm in response.get('MetricAlarms', []):
                data.append({
                    'name': alarm['AlarmName'],
                    'metric': alarm['MetricName'],
                    'state': alarm['StateValue'],
                    'reason': alarm.get('StateReason', ''),
                    'updated': alarm.get('StateUpdatedTimestamp', datetime.now()),
                    'account': account_name
                })
            
            if data:
                return pd.DataFrame(data)
            
            # Return empty DataFrame with correct columns if no alarms
            return pd.DataFrame(columns=['name', 'metric', 'state', 'reason', 'updated', 'account'])
            
        except Exception as e:
            st.error(f"Error fetching CloudWatch alarms for {account_name}: {str(e)}")
            return _self._get_mock_alarms()
    
    def get_all_accounts_alarms(self) -> pd.DataFrame:
        """Get CloudWatch alarms for all accounts"""
        all_alarms = {}
        
        for account_name in self.list_active_account_names():
            all_alarms[account_name] = self.get_cloudwatch_alarms(account_name)
        
        if not all_alarms:
            return self._get_mock_alarms()
        
        # Combine all alarms
        combined = self.combine_dataframes(all_alarms, add_account_column=False)
        return combined
    
    # Mock data methods
    def _get_mock_cost_overview(self) -> Dict[str, Any]:
        """Return mock cost overview"""
        return {
            'total_cost': 2345.67,
            'cost_change': 12.5,
            'forecast_cost': 2567.89,
            'top_services': [
                ('Amazon EC2', 890.12),
                ('Amazon S3', 345.67),
                ('Amazon RDS', 234.56),
                ('AWS Lambda', 123.45),
                ('Amazon CloudFront', 98.76)
            ],
            'service_count': 12
        }
    
    def _get_mock_daily_costs(self, days_back: int) -> pd.DataFrame:
        """Generate mock daily cost data"""
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        data = []
        
        base_cost = 70
        for i, date in enumerate(dates):
            # Add some variation
            daily_cost = base_cost + np.random.uniform(-10, 15) + (i * 0.5)
            data.append({
                'date': date,
                'cost': max(0, daily_cost)
            })
        
        return pd.DataFrame(data)
    
    def _get_mock_service_costs(self) -> pd.DataFrame:
        """Return mock service cost data"""
        return pd.DataFrame([
            {'service': 'Amazon EC2', 'cost': 890.12, 'usage': 24567, 'account': 'Mock'},
            {'service': 'Amazon S3', 'cost': 345.67, 'usage': 1234567, 'account': 'Mock'},
            {'service': 'Amazon RDS', 'cost': 234.56, 'usage': 720, 'account': 'Mock'},
            {'service': 'AWS Lambda', 'cost': 123.45, 'usage': 5678900, 'account': 'Mock'},
            {'service': 'Amazon CloudFront', 'cost': 98.76, 'usage': 456789, 'account': 'Mock'}
        ])
    
    def _get_mock_resource_summary(self) -> Dict[str, Any]:
        """Return mock resource summary"""
        return {
            'account': 'Mock',
            'region': 'us-east-1',
            'ec2_instances': {'running': 5, 'stopped': 2, 'total': 7},
            's3_buckets': {'count': 12, 'total_size': 0},
            'rds_instances': {'count': 3, 'status': {'available': 3}},
            'errors': []
        }
    
    def _get_mock_alarms(self) -> pd.DataFrame:
        """Return mock CloudWatch alarms"""
        return pd.DataFrame([
            {
                'name': 'High CPU Utilization',
                'metric': 'CPUUtilization',
                'state': 'ALARM',
                'reason': 'Threshold Crossed: 1 datapoint [89.5] was greater than the threshold (80.0)',
                'updated': datetime.now() - timedelta(minutes=15),
                'account': 'Mock'
            },
            {
                'name': 'Low Disk Space',
                'metric': 'DiskSpaceUtilization',
                'state': 'ALARM',
                'reason': 'Threshold Crossed: 1 datapoint [92.3] was greater than the threshold (90.0)',
                'updated': datetime.now() - timedelta(hours=2),
                'account': 'Mock'
            }
        ])