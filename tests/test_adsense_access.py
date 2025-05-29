#!/usr/bin/env python3
"""
Test Google AdSense API access
This script verifies that your AdSense configuration is working correctly
"""

import json
import os
import sys
from pathlib import Path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Add parent directory to path to import from config
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import Settings

SCOPES = ['https://www.googleapis.com/auth/adsense.readonly']

print("🔍 Google AdSense Access Test")
print("=" * 50)

# Load settings from environment
try:
    settings = Settings()
    if not settings.ENABLE_GOOGLE_ADSENSE:
        print("❌ Google AdSense is disabled in settings")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    print("   Make sure you have a .env file with proper configuration")
    sys.exit(1)

# Test each configured AdSense account
accounts_tested = 0
accounts_successful = 0

for account in settings.ADSENSE_ACCOUNTS:
    if not account.get('enabled', True):
        continue
    
    accounts_tested += 1
    account_name = account['name']
    client_secrets_path = account['client_secrets_path']
    token_path = account.get('token_path', f'token_{account_name.lower().replace(" ", "_")}.json')
    
    print(f"\n💰 Testing Account: {account_name}")
    print("-" * 40)
    print(f"Client Secrets: {client_secrets_path}")
    print(f"Token File: {token_path}")
    
    # Check client secrets file
    try:
        with open(client_secrets_path, 'r') as f:
            client_config = json.load(f)
        
        if 'web' in client_config:
            client_id = client_config['web']['client_id']
            print(f"✅ Client Secrets File: Found (Web application)")
            print(f"🔑 Client ID: {client_id[:50]}...")
        else:
            print(f"❌ Error: OAuth client must be configured as 'Web application'")
            continue
            
    except FileNotFoundError:
        print(f"❌ Client secrets file not found: {client_secrets_path}")
        print(f"   Please download from Google Cloud Console")
        continue
    except Exception as e:
        print(f"❌ Error loading client secrets: {e}")
        continue

    # OAuth2 flow
    creds = None
    if os.path.exists(token_path):
        print(f"📄 Token file found, attempting to load...")
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"⚠️  Error loading token: {e}")
            print(f"   Will re-authenticate...")

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                print(f"🔐 Starting new OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, SCOPES
                )
                creds = flow.run_local_server(port=8080)
        else:
            print(f"🔐 Starting OAuth2 flow...")
            print(f"   A browser window will open for authorization")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f"💾 Token saved to {token_path}")

    # Build AdSense service and test API access
    try:
        service = build('adsense', 'v2', credentials=creds)
        print(f"✅ AdSense Service: Created successfully")
        
        # Test API access
        accounts_response = service.accounts().list().execute()
        
        if 'accounts' in accounts_response:
            adsense_accounts = accounts_response['accounts']
            print(f"✅ API Access: SUCCESS!")
            print(f"📊 Found {len(adsense_accounts)} AdSense account(s):")
            
            for adsense_account in adsense_accounts:
                account_id = adsense_account['name'].split('/')[-1]
                display_name = adsense_account.get('displayName', 'Unknown')
                print(f"   - {display_name} (ID: {account_id})")
                
                # Try to get a simple report
                try:
                    report = service.accounts().reports().generate(
                        account=adsense_account['name'],
                        dateRange='LAST_7_DAYS',
                        metrics=['ESTIMATED_EARNINGS', 'PAGE_VIEWS', 'CLICKS'],
                        dimensions=['DATE']
                    ).execute()
                    
                    if 'rows' in report and report['rows']:
                        total_earnings = sum(float(row['cells'][1]['value']) for row in report['rows'])
                        print(f"     └─ Last 7 days earnings: ${total_earnings:.2f}")
                    else:
                        print(f"     └─ No earnings data for last 7 days")
                        
                except Exception as e:
                    print(f"     └─ Error fetching report: {str(e)}")
            
            accounts_successful += 1
        else:
            print(f"⚠️  No AdSense accounts found")
            print(f"   Make sure you're logged in with an account that has AdSense enabled")
            
    except Exception as e:
        print(f"❌ API Access FAILED: {e}")
        print(f"\n🔧 Common issues:")
        print(f"1. AdSense API not enabled in Google Cloud Console")
        print(f"2. Account doesn't have AdSense access")
        print(f"3. OAuth consent screen not configured properly")

print("\n" + "=" * 50)
print(f"💰 Summary: {accounts_successful}/{accounts_tested} accounts tested successfully")

if accounts_tested == 0:
    print("❌ No AdSense accounts configured!")
    print("   Please check your .env file")
elif accounts_successful == accounts_tested:
    print("✅ All accounts configured correctly!")
else:
    print("⚠️  Some accounts have issues - check the errors above")