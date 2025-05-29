"""
Authentication and credential management utilities
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

class CredentialsManager:
    """Manage Google service account credentials"""
    
    @staticmethod
    def get_service_account_credentials(
        credentials_path: Optional[str] = None,
        credentials_json: Optional[str] = None,
        scopes: list = None
    ) -> service_account.Credentials:
        """
        Get service account credentials from file or JSON string
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account JSON as string
            scopes: List of OAuth scopes
            
        Returns:
            Service account credentials
        """
        if credentials_json:
            # Load from JSON string (useful for deployment)
            info = json.loads(credentials_json)
        elif credentials_path and os.path.exists(credentials_path):
            # Load from file
            with open(credentials_path, 'r') as f:
                info = json.load(f)
        else:
            raise ValueError(
                "Either credentials_path or credentials_json must be provided"
            )
        
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=scopes
        )
        
        return credentials


class OAuth2Manager:
    """Manage OAuth2 flow for user authentication"""
    
    def __init__(self, client_secrets_file: str, scopes: list, token_file: str = 'token.json'):
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes
        self.token_file = token_file
    
    def get_credentials(self) -> Credentials:
        """
        Get valid OAuth2 credentials, refreshing or re-authenticating if needed
        
        Returns:
            Valid OAuth2 credentials
        """
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # Refresh or get new token if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes
                )
                # Use a fixed port for consistent redirect URI
                creds = flow.run_local_server(port=8080)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def clear_credentials(self):
        """Clear stored credentials"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)


class SessionManager:
    """Manage Streamlit session state for authentication"""
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def set_authenticated(email: str):
        """Set user as authenticated"""
        st.session_state.authenticated = True
        st.session_state.user_email = email
    
    @staticmethod
    def logout():
        """Clear authentication session"""
        st.session_state.authenticated = False
        st.session_state.user_email = None