"""
Base service class for multi-account support
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import streamlit as st
import pandas as pd


class MultiAccountService(ABC):
    """Base class for services supporting multiple accounts"""
    
    def __init__(self, accounts_config: List[Dict[str, Any]]):
        """
        Initialize service with multiple account configurations
        
        Args:
            accounts_config: List of account configuration dictionaries
        """
        self.accounts = {}
        self.account_errors = {}
        
        # Initialize each account
        for config in accounts_config:
            account_name = config.get('name', f'Account_{len(self.accounts)}')
            try:
                if config.get('enabled', True):
                    account_client = self._init_account(config)
                    self.accounts[account_name] = {
                        'client': account_client,
                        'config': config,
                        'status': 'active'
                    }
            except Exception as e:
                # Store error but don't fail entire service
                self.account_errors[account_name] = str(e)
                self.accounts[account_name] = {
                    'client': None,
                    'config': config,
                    'status': 'error',
                    'error': str(e)
                }
    
    @abstractmethod
    def _init_account(self, config: Dict[str, Any]):
        """
        Initialize a single account client
        Must be implemented by subclasses
        
        Args:
            config: Account configuration dictionary
            
        Returns:
            Initialized client for the account
        """
        pass
    
    def get_account(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific account by name"""
        return self.accounts.get(name)
    
    def get_active_accounts(self) -> Dict[str, Dict[str, Any]]:
        """Get all active accounts"""
        return {
            name: account 
            for name, account in self.accounts.items() 
            if account['status'] == 'active'
        }
    
    def list_account_names(self) -> List[str]:
        """List all account names"""
        return list(self.accounts.keys())
    
    def list_active_account_names(self) -> List[str]:
        """List active account names"""
        return [
            name for name, account in self.accounts.items()
            if account['status'] == 'active'
        ]
    
    def has_active_accounts(self) -> bool:
        """Check if any accounts are active"""
        return len(self.list_active_account_names()) > 0
    
    def get_account_status(self, name: str) -> str:
        """Get status of a specific account"""
        account = self.accounts.get(name)
        if account:
            return account['status']
        return 'not_found'
    
    def get_account_error(self, name: str) -> Optional[str]:
        """Get error message for a specific account"""
        account = self.accounts.get(name)
        if account and account['status'] == 'error':
            return account.get('error')
        return None
    
    @abstractmethod
    def get_account_summary(self, account_name: str) -> Dict[str, Any]:
        """
        Get summary metrics for a specific account
        Must be implemented by subclasses
        
        Args:
            account_name: Name of the account
            
        Returns:
            Dictionary with summary metrics
        """
        pass
    
    def get_all_accounts_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary for all active accounts"""
        summaries = {}
        for name in self.list_active_account_names():
            try:
                summaries[name] = self.get_account_summary(name)
            except Exception as e:
                summaries[name] = {'error': str(e)}
        return summaries
    
    @staticmethod
    def aggregate_metrics(accounts_data: Dict[str, Dict[str, Any]], 
                         metric_keys: List[str]) -> Dict[str, Any]:
        """
        Aggregate metrics across multiple accounts
        
        Args:
            accounts_data: Dictionary of account data
            metric_keys: List of metric keys to aggregate
            
        Returns:
            Aggregated metrics
        """
        aggregated = {}
        
        for key in metric_keys:
            total = 0
            count = 0
            
            for account_data in accounts_data.values():
                if key in account_data and not isinstance(account_data.get(key), str):
                    value = account_data[key]
                    if value is not None:
                        total += value
                        count += 1
            
            # For rates/percentages, calculate average instead of sum
            if any(rate_key in key.lower() for rate_key in ['rate', 'ctr', 'rpm']):
                aggregated[key] = total / count if count > 0 else 0
            else:
                aggregated[key] = total
        
        return aggregated
    
    @staticmethod
    def combine_dataframes(dfs: Dict[str, pd.DataFrame], 
                          add_account_column: bool = True) -> pd.DataFrame:
        """
        Combine multiple DataFrames with account labels
        
        Args:
            dfs: Dictionary mapping account names to DataFrames
            add_account_column: Whether to add an 'account' column
            
        Returns:
            Combined DataFrame
        """
        if not dfs:
            return pd.DataFrame()
        
        if add_account_column:
            # Add account name to each dataframe
            for account_name, df in dfs.items():
                df['account'] = account_name
        
        # Combine all dataframes
        combined = pd.concat(dfs.values(), ignore_index=True)
        return combined