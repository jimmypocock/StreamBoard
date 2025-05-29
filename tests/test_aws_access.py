#!/usr/bin/env python3
"""
Test AWS API access
This script verifies that your AWS configuration is working correctly
"""

import os
import sys
from pathlib import Path
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

# Add parent directory to path to import from config
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import Settings

print("🔍 AWS Access Test")
print("=" * 50)

# Load settings from environment
try:
    settings = Settings()
    if not settings.ENABLE_AWS_METRICS:
        print("❌ AWS metrics are disabled in settings")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    print("   Make sure you have a .env file with proper configuration")
    sys.exit(1)

# Test each configured AWS account
accounts_tested = 0
accounts_successful = 0

for account in settings.AWS_ACCOUNTS:
    if not account.get('enabled', True):
        continue
    
    accounts_tested += 1
    account_name = account['name']
    access_key = account['access_key_id']
    region = account.get('region', 'us-east-1')
    
    print(f"\n☁️  Testing Account: {account_name}")
    print("-" * 40)
    print(f"🔑 Access Key: {access_key[:10]}...")
    print(f"🌍 Region: {region}")
    
    # Create AWS session
    try:
        session = boto3.Session(
            aws_access_key_id=account['access_key_id'],
            aws_secret_access_key=account['secret_access_key'],
            region_name=region
        )
    except Exception as e:
        print(f"❌ Error creating AWS session: {e}")
        continue
    
    # Test different AWS services
    results = {}
    
    # 1. Test Cost Explorer
    print("\n📊 Testing Cost Explorer API...")
    try:
        ce_client = session.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
        
        # Get cost for last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        total_cost = sum(float(day['Total']['UnblendedCost']['Amount']) for day in response['ResultsByTime'])
        print(f"✅ Cost Explorer: SUCCESS")
        print(f"   Last 7 days total cost: ${total_cost:.2f}")
        results['cost_explorer'] = True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Cost Explorer: FAILED ({error_code})")
        if error_code == 'AccessDeniedException':
            print(f"   Required permission: ce:GetCostAndUsage")
        results['cost_explorer'] = False
    except Exception as e:
        print(f"❌ Cost Explorer: FAILED - {str(e)}")
        results['cost_explorer'] = False
    
    # 2. Test EC2
    print("\n💻 Testing EC2 API...")
    try:
        ec2_client = session.client('ec2', region_name=region)
        response = ec2_client.describe_instances()
        
        instance_count = sum(len(r['Instances']) for r in response['Reservations'])
        print(f"✅ EC2: SUCCESS")
        print(f"   Found {instance_count} instances")
        results['ec2'] = True
        
    except ClientError as e:
        print(f"❌ EC2: FAILED - {e}")
        print(f"   Required permission: ec2:DescribeInstances")
        results['ec2'] = False
    
    # 3. Test S3
    print("\n🪣 Testing S3 API...")
    try:
        s3_client = session.client('s3', region_name=region)
        response = s3_client.list_buckets()
        
        bucket_count = len(response['Buckets'])
        print(f"✅ S3: SUCCESS")
        print(f"   Found {bucket_count} buckets")
        results['s3'] = True
        
    except ClientError as e:
        print(f"❌ S3: FAILED - {e}")
        print(f"   Required permission: s3:ListAllMyBuckets")
        results['s3'] = False
    
    # 4. Test CloudWatch
    print("\n📈 Testing CloudWatch API...")
    try:
        cw_client = session.client('cloudwatch', region_name=region)
        response = cw_client.describe_alarms(MaxRecords=1)
        
        print(f"✅ CloudWatch: SUCCESS")
        print(f"   API is accessible")
        results['cloudwatch'] = True
        
    except ClientError as e:
        print(f"❌ CloudWatch: FAILED - {e}")
        print(f"   Required permission: cloudwatch:DescribeAlarms")
        results['cloudwatch'] = False
    
    # 5. Test RDS
    print("\n🗄️  Testing RDS API...")
    try:
        rds_client = session.client('rds', region_name=region)
        response = rds_client.describe_db_instances()
        
        db_count = len(response['DBInstances'])
        print(f"✅ RDS: SUCCESS")
        print(f"   Found {db_count} database instances")
        results['rds'] = True
        
    except ClientError as e:
        print(f"❌ RDS: FAILED - {e}")
        print(f"   Required permission: rds:DescribeDBInstances")
        results['rds'] = False
    
    # Summary for this account
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Account Summary: {successful_tests}/{total_tests} services accessible")
    
    if successful_tests == total_tests:
        accounts_successful += 1
        print("✅ All AWS services configured correctly!")
    else:
        print("⚠️  Some services have permission issues")
        print("\n🔧 Recommended IAM policy additions:")
        if not results.get('cost_explorer'):
            print("   - ce:GetCostAndUsage")
        if not results.get('ec2'):
            print("   - ec2:DescribeInstances")
        if not results.get('s3'):
            print("   - s3:ListAllMyBuckets")
        if not results.get('cloudwatch'):
            print("   - cloudwatch:DescribeAlarms")
        if not results.get('rds'):
            print("   - rds:DescribeDBInstances")

print("\n" + "=" * 50)
print(f"☁️  Summary: {accounts_successful}/{accounts_tested} AWS accounts fully configured")

if accounts_tested == 0:
    print("❌ No AWS accounts configured!")
    print("   Please check your .env file")
elif accounts_successful == accounts_tested:
    print("✅ All accounts configured correctly!")
else:
    print("⚠️  Some accounts have issues - check the errors above")

print("\n💡 Cost Notes:")
print("- EC2, S3, CloudWatch, RDS: API calls are generally free within reasonable limits")
print("- Cost Explorer: $0.01 per request (after 1000 free requests/month)")
print("- For production use, implement caching to minimize API calls")