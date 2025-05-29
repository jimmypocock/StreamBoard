"""
Configuration management for StreamBoard with multi-account support
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Settings:
    """Application settings with multi-account support"""
    
    # App settings
    APP_NAME = "StreamBoard Analytics Dashboard"
    APP_VERSION = "2.0.0"  # Updated for multi-account support
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server settings
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8501'))
    
    # Cache settings
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '3600'))  # 1 hour default
    CACHE_TTL_SHORT = int(os.getenv('CACHE_TTL_SHORT', '300'))  # 5 minutes
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
    
    # Feature flags
    ENABLE_GOOGLE_ANALYTICS = os.getenv('ENABLE_GOOGLE_ANALYTICS', 'True').lower() == 'true'
    ENABLE_GOOGLE_ADSENSE = os.getenv('ENABLE_GOOGLE_ADSENSE', 'True').lower() == 'true'
    ENABLE_AWS_METRICS = os.getenv('ENABLE_AWS_METRICS', 'True').lower() == 'true'
    
    @classmethod
    def get_google_analytics_accounts(cls) -> List[Dict[str, Any]]:
        """Get Google Analytics account configurations"""
        # Try to load from JSON format first (multi-account)
        accounts_json = os.getenv('GA_ACCOUNTS', '')
        if accounts_json:
            try:
                return json.loads(accounts_json)
            except json.JSONDecodeError:
                pass
        
        # Fall back to legacy single account format
        legacy_property_id = os.getenv('GA4_PROPERTY_ID', '')
        legacy_credentials_path = os.getenv('GA4_CREDENTIALS_PATH', '')
        legacy_credentials_json = os.getenv('GA4_CREDENTIALS_JSON', '')
        
        if legacy_property_id and (legacy_credentials_path or legacy_credentials_json):
            return [{
                'name': 'Default',
                'property_id': legacy_property_id,
                'credentials_path': legacy_credentials_path,
                'credentials_json': legacy_credentials_json,
                'enabled': True
            }]
        
        return []
    
    @classmethod
    def get_google_adsense_accounts(cls) -> List[Dict[str, Any]]:
        """Get Google AdSense account configurations"""
        # Try to load from JSON format first (multi-account)
        accounts_json = os.getenv('ADSENSE_ACCOUNTS', '')
        if accounts_json:
            try:
                return json.loads(accounts_json)
            except json.JSONDecodeError:
                pass
        
        # Fall back to legacy single account format
        legacy_client_secrets = os.getenv('ADSENSE_CLIENT_SECRETS_PATH', '')
        legacy_account_id = os.getenv('ADSENSE_ACCOUNT_ID', '')
        legacy_token_path = os.getenv('ADSENSE_TOKEN_PATH', 'token.json')
        
        if legacy_client_secrets:
            return [{
                'name': 'Default',
                'client_secrets_path': legacy_client_secrets,
                'account_id': legacy_account_id,
                'token_path': legacy_token_path,
                'enabled': True
            }]
        
        return []
    
    @classmethod
    def get_aws_accounts(cls) -> List[Dict[str, Any]]:
        """Get AWS account configurations"""
        # Try to load from JSON format first (multi-account)
        accounts_json = os.getenv('AWS_ACCOUNTS', '')
        if accounts_json:
            try:
                return json.loads(accounts_json)
            except json.JSONDecodeError:
                pass
        
        # Fall back to legacy single account format
        legacy_access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        legacy_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        legacy_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if legacy_access_key and legacy_secret_key:
            return [{
                'name': 'Default',
                'access_key_id': legacy_access_key,
                'secret_access_key': legacy_secret_key,
                'region': legacy_region,
                'enabled': True
            }]
        
        return []
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        errors = []
        warnings = []
        
        # Debug: Print what services are enabled
        if cls.DEBUG:
            print(f"DEBUG: Services enabled - GA: {cls.ENABLE_GOOGLE_ANALYTICS}, AdSense: {cls.ENABLE_GOOGLE_ADSENSE}, AWS: {cls.ENABLE_AWS_METRICS}")
        
        # Check if at least one service is enabled
        if not any([cls.ENABLE_GOOGLE_ANALYTICS, cls.ENABLE_GOOGLE_ADSENSE, cls.ENABLE_AWS_METRICS]):
            warnings.append("No services are enabled. Enable at least one service in your .env file.")
        
        # Validate Google Analytics
        if cls.ENABLE_GOOGLE_ANALYTICS:
            ga_accounts = cls.get_google_analytics_accounts()
            if cls.DEBUG:
                print(f"DEBUG: GA accounts loaded: {len(ga_accounts) if ga_accounts else 0}")
                if ga_accounts:
                    print(f"DEBUG: GA accounts: {ga_accounts}")
            if not ga_accounts:
                errors.append("Google Analytics is enabled but no accounts are configured")
            else:
                for i, account in enumerate(ga_accounts):
                    if not account.get('property_id'):
                        errors.append(f"GA account {i+1}: property_id is required")
                    if not account.get('credentials_path') and not account.get('credentials_json'):
                        errors.append(f"GA account {i+1}: either credentials_path or credentials_json is required")
        
        # Validate Google AdSense
        if cls.ENABLE_GOOGLE_ADSENSE:
            adsense_accounts = cls.get_google_adsense_accounts()
            if not adsense_accounts:
                errors.append("Google AdSense is enabled but no accounts are configured")
            else:
                for i, account in enumerate(adsense_accounts):
                    if not account.get('client_secrets_path'):
                        errors.append(f"AdSense account {i+1}: client_secrets_path is required")
        
        # Validate AWS
        if cls.ENABLE_AWS_METRICS:
            aws_accounts = cls.get_aws_accounts()
            if not aws_accounts:
                errors.append("AWS Metrics is enabled but no accounts are configured")
            else:
                for i, account in enumerate(aws_accounts):
                    if not account.get('access_key_id') or not account.get('secret_access_key'):
                        errors.append(f"AWS account {i+1}: access_key_id and secret_access_key are required")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
        
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}")
        
        return True


# Create settings instance
settings = Settings()