#!/usr/bin/env python3
"""
Test Google Analytics API access
This script verifies that your GA4 configuration is working correctly
"""

import json
import sys
import os
from pathlib import Path
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

# Add parent directory to path to import from config
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import Settings

print("🔍 Google Analytics Access Test")
print("=" * 50)

# Load settings from environment
try:
    settings = Settings()
    if not settings.ENABLE_GOOGLE_ANALYTICS:
        print("❌ Google Analytics is disabled in settings")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    print("   Make sure you have a .env file with proper configuration")
    sys.exit(1)

# Test each configured GA account
accounts_tested = 0
accounts_successful = 0

for account in settings.GA_ACCOUNTS:
    if not account.get('enabled', True):
        continue
    
    accounts_tested += 1
    account_name = account['name']
    property_id = account['property_id']
    credentials_path = account['credentials_path']
    
    print(f"\n📊 Testing Account: {account_name}")
    print("-" * 40)
    print(f"Property ID: {property_id}")
    print(f"Credentials: {credentials_path}")
    
    # Load credentials
    try:
        with open(credentials_path, 'r') as f:
            sa_info = json.load(f)
        
        print(f"✅ Service Account File: Found")
        print(f"📧 Service Account Email: {sa_info['client_email']}")
        print(f"🏗️  Project ID: {sa_info['project_id']}")
    except FileNotFoundError:
        print(f"❌ Service account file not found: {credentials_path}")
        continue
    except Exception as e:
        print(f"❌ Error loading service account file: {e}")
        continue

    # Create credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        print(f"✅ Credentials: Created successfully")
    except Exception as e:
        print(f"❌ Error creating credentials: {e}")
        continue

    # Create client and test API access
    try:
        client = BetaAnalyticsDataClient(credentials=credentials)
        print(f"✅ Analytics Client: Created successfully")
        
        # Test API access with a simple query
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            metrics=[Metric(name="activeUsers")]
        )
        
        response = client.run_report(request)
        
        print(f"✅ API Access: SUCCESS!")
        print(f"📊 Test Query Results:")
        
        if response.rows:
            for row in response.rows:
                print(f"   Active Users (Last 7 days): {row.metric_values[0].value}")
        else:
            print(f"   No data available (this is normal for new properties)")
        
        accounts_successful += 1
        
    except Exception as e:
        print(f"❌ API Access FAILED: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Ensure the service account has 'Viewer' access to GA4 property {property_id}")
        print(f"2. Verify the property ID is correct (just numbers, no 'properties/' prefix)")
        print(f"3. Check that Google Analytics Data API is enabled in your Google Cloud project")
        print(f"4. Wait 2-5 minutes after adding service account for permissions to propagate")

print("\n" + "=" * 50)
print(f"📊 Summary: {accounts_successful}/{accounts_tested} accounts tested successfully")

if accounts_tested == 0:
    print("❌ No Google Analytics accounts configured!")
    print("   Please check your .env file")
elif accounts_successful == accounts_tested:
    print("✅ All accounts configured correctly!")
else:
    print("⚠️  Some accounts have issues - check the errors above")