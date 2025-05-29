# StreamBoard 📊

> All Your Metrics. One Dashboard. 10 Minutes.

StreamBoard is a self-hosted, open-source analytics dashboard that unifies all your business metrics in one beautiful interface. Now with **multi-account support** - track unlimited Google Analytics properties, AdSense accounts, and AWS accounts all in one place!

![StreamBoard Logo](https://img.shields.io/badge/StreamBoard-Analytics%20Made%20Simple-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTMgMTNoMnY3SDN6bTQtOGgydjEySDd6bTQtMmgydjE0aC0yem00IDRoMnYxMGgtMnptNC0yaDJ2MTJoLTJ6Ii8+PC9zdmc+)

## ✨ Features


- **🔢 Multi-Account Support** - Track unlimited accounts per service with aggregated views
- **📊 Universal Connector** - Pre-built integrations for Google Analytics, AdSense, and AWS
- **🎯 Unified Analytics** - See all your metrics in one place with account-level breakdowns
- **⚡ Real-Time Updates** - Live data streaming with automatic refresh and smart caching
- **🔒 Your Data, Your Control** - Self-hosted solution means your data never leaves your infrastructure
- **🎨 Beautiful by Default** - Professional dark theme with customizable branding
- **📱 Mobile Ready** - Responsive design that looks great on any device

## 🆕 What's New in v2.0


### Multi-Account Support

- Track multiple Google Analytics properties
- Monitor multiple AdSense accounts
- Manage multiple AWS accounts across regions
- Aggregate data across all accounts or view individually
- Account status tracking with error isolation

## 🚀 Quick Start


```bash
# Clone the repository
git clone https://github.com/streamboard/streamboard.git

# Navigate to directory
cd streamboard

# Run the installer
./install.sh

# Copy environment template and configure
cp .env.example .env
# Edit .env with your credentials

# Test your API connections (recommended)
python tests/test_ga_access.py
python tests/test_adsense_access.py
python tests/test_aws_access.py

# Start StreamBoard
./streamboard start
```

Your dashboard will be running at `http://localhost:8501` 🎉

## 📋 Prerequisites


- Python 3.8 or higher
- Google Cloud account (for Analytics/AdSense)
- AWS account (optional)
- 2GB RAM minimum
- Modern web browser

## 🔧 Configuration


StreamBoard now supports both **multi-account** and **single-account** configurations for backward compatibility.

### Multi-Account Configuration (Recommended)


#### Google Analytics - Multiple Properties


```bash
# Enable Google Analytics
ENABLE_GOOGLE_ANALYTICS=True

# Configure multiple GA4 properties using JSON format
GA_ACCOUNTS='[
  {
    "name": "Main Website",
    "property_id": "123456789",
    "credentials_path": "/path/to/main-site-key.json",
    "enabled": true
  },
  {
    "name": "Blog",
    "property_id": "987654321",
    "credentials_path": "/path/to/blog-key.json",
    "enabled": true
  },
  {
    "name": "Mobile App",
    "property_id": "555666777",
    "credentials_path": "/path/to/app-key.json",
    "enabled": true
  }
]'
```

#### Google AdSense - Multiple Accounts


```bash
# Enable AdSense
ENABLE_GOOGLE_ADSENSE=True

# Configure multiple AdSense accounts
ADSENSE_ACCOUNTS='[
  {
    "name": "Primary Account",
    "client_secrets_path": "/path/to/client_secrets_1.json",
    "token_path": "token_primary.json",
    "enabled": true
  },
  {
    "name": "Secondary Account",
    "client_secrets_path": "/path/to/client_secrets_2.json",
    "token_path": "token_secondary.json",
    "enabled": true
  }
]'
```

#### AWS - Multiple Accounts


```bash
# Enable AWS metrics
ENABLE_AWS_METRICS=True

# Configure multiple AWS accounts
AWS_ACCOUNTS='[
  {
    "name": "Production",
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1",
    "enabled": true
  },
  {
    "name": "Development",
    "access_key_id": "AKIAIOSFODNN7EXAMPLE2",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY2",
    "region": "us-west-2",
    "enabled": true
  },
  {
    "name": "Staging",
    "access_key_id": "AKIAIOSFODNN7EXAMPLE3",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY3",
    "region": "eu-west-1",
    "enabled": true
  }
]'
```

### Single Account Configuration (Legacy)


For backward compatibility, you can still use the single account format:

```bash
# Google Analytics
GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS_PATH=/path/to/service-account-key.json

# Google AdSense
ADSENSE_CLIENT_SECRETS_PATH=/path/to/client_secrets.json

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

## 📊 Dashboard Features


### View Modes

- **All Accounts**: Aggregated metrics across all configured accounts
- **Individual Account**: Detailed view of a specific account
- **Comparison View**: Side-by-side account comparisons

### Account Management

- Real-time account status indicators
- Automatic error handling and retry
- Account-level filtering and selection
- Enable/disable accounts without reconfiguration

### Data Aggregation

- Combined metrics with smart averaging for rates/percentages
- Account contribution breakdowns
- Unified time-series charts
- Cross-account trend analysis

## 🔧 Setup Instructions


### Google Analytics Setup


1. **Create Service Account(s)**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a service account for each property (or use one for all)
   - Download JSON key file(s)

2. **Grant Access**:
   - In GA4, go to Admin > Property Access Management
   - Add service account email with "Viewer" role
   - Repeat for each property

3. **Configure StreamBoard**:
   - Add credentials to your `.env` file using the multi-account format
   - Each property needs a unique name for identification

### Google AdSense Setup


1. **Create OAuth2 Credentials**:
   - Enable AdSense Management API in Google Cloud Console
   - Create OAuth 2.0 Client ID (Desktop type)
   - Download client secrets for each account

2. **First-time Authorization**:
   - Run StreamBoard
   - Each account will require browser authentication on first run
   - Tokens are saved automatically for future use

### AWS Setup


1. **Create IAM Users**:
   - Create separate IAM users for each AWS account
   - Grant necessary read permissions:
     - Cost Explorer access
     - CloudWatch read access
     - EC2, S3, RDS describe permissions

2. **Configure Regions**:
   - Specify the primary region for each account
   - Cost Explorer data is always fetched from us-east-1

## 🚦 Running the Application


```bash
# Using the StreamBoard command
./streamboard start   # Start the dashboard
./streamboard stop    # Stop the dashboard
./streamboard status  # Check status

# Direct execution
source streamboard_env/bin/activate
streamlit run app.py
```

## 🌐 Deployment


See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed AWS deployment instructions using CDK.

### Quick Deploy Options


- **AWS ECS Fargate** (Recommended for production)
- **AWS App Runner** (Simpler setup)
- **Docker** (Any container platform)
- **Heroku** (Quick start option)

## 📊 Supported Integrations


- ✅ **Google Analytics (GA4)** - Multiple properties
- ✅ **Google AdSense** - Multiple accounts
- ✅ **AWS** - Multiple accounts with Cost Explorer & CloudWatch
- 🔄 Stripe (Coming Soon)
- 🔄 Facebook Ads (Coming Soon)
- 🔄 Shopify (Coming Soon)

## 🧪 Testing

### API Connection Test Scripts

StreamBoard includes test scripts to verify your API credentials and permissions before running the full dashboard:

#### Test Google Analytics Access
```bash
python tests/test_ga_access.py
```
This script will:
- Verify service account credentials
- Check API access to configured properties
- Display available metrics from the last 7 days
- Show any permission errors

#### Test Google AdSense Access
```bash
python tests/test_adsense_access.py
```
This script will:
- Initiate OAuth2 authentication flow if needed
- Verify AdSense Management API access
- Display account information
- Show recent earnings data

#### Test AWS Access
```bash
python tests/test_aws_access.py
```
This script will:
- Verify AWS credentials for each configured account
- Test permissions for EC2, S3, RDS, CloudWatch, and Cost Explorer
- Display resource counts and status
- Check regional access

### Running All Tests
```bash
# Test all configured services
python tests/test_ga_access.py && python tests/test_adsense_access.py && python tests/test_aws_access.py
```

### Common Test Issues

- **"Permission denied" errors**: Check service account/IAM permissions
- **"API not enabled" errors**: Enable the required APIs in Google Cloud Console
- **"Invalid credentials" errors**: Verify credential file paths in .env
- **No data returned**: Some APIs require 24-48 hours of data before returning results

## 🔍 Troubleshooting

### Test Script Issues

#### Google Analytics Tests
- **"No data found"**: GA4 properties need at least 24 hours of data
- **"Invalid property ID"**: Use numbers only (e.g., 123456789, not GA-123456789)
- **"Credentials not found"**: Check file path is absolute, not relative
- **"403 Forbidden"**: Service account needs "Viewer" role in GA4 property

#### AdSense Tests
- **"Authorization required"**: Delete token file and re-run to re-authenticate
- **"No AdSense account"**: Ensure the Google account has an active AdSense account
- **"Scope error"**: Client must have AdSense Management API scope
- **"Token expired"**: Re-run the script to refresh authentication

#### AWS Tests
- **"Invalid security token"**: AWS credentials may be expired
- **"Access denied"**: Add required permissions to IAM user
- **"Cost data unavailable"**: New AWS accounts need 24 hours for Cost Explorer activation
- **"Region error"**: Ensure the specified region is valid and accessible

### Multi-Account Issues

- **Account not showing**: Check JSON syntax in environment variables
- **Mixed data**: Ensure each account has a unique name
- **Authentication errors**: Each account needs its own credentials
- **Performance issues**: Consider enabling/disabling accounts as needed

### Google Analytics

- Check service account has "Viewer" access to all properties
- Verify property IDs are correct (numbers only)
- Ensure Analytics Data API is enabled
- Service account email must be added to each GA4 property

### Google AdSense

- Delete token files to re-authenticate accounts
- Check AdSense Management API is enabled
- Verify OAuth2 client type is "Desktop"
- Each account needs its own client secrets file

### AWS

- Verify IAM permissions for each account
- Check Cost Explorer is enabled (24h delay for new accounts)
- Ensure credentials are valid and not expired
- Cost data requires specific permissions: ce:GetCostAndUsage

## 🔒 Security Best Practices


1. **Credential Management**:
   - Never commit `.env` or credential files
   - Use AWS Secrets Manager for production
   - Rotate credentials regularly

2. **Access Control**:
   - Use read-only permissions
   - Implement IP whitelisting for production
   - Enable MFA on all service accounts

3. **Data Privacy**:
   - All data processing happens locally
   - No external analytics or tracking
   - Credentials never leave your infrastructure

## 🛠️ Development

### Development Setup

```bash
# Create and activate virtual environment
python -m venv streamboard_env
source streamboard_env/bin/activate  # On Windows: streamboard_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Note: This project doesn't use setup.py, so 'pip install -e .' won't work
# Simply run scripts directly from the project directory

# Run API connection tests (these are standalone scripts, not pytest tests)
python tests/test_ga_access.py
python tests/test_adsense_access.py
python tests/test_aws_access.py
```

### Testing During Development

#### Before Running the Dashboard
1. Test individual service connections:
   ```bash
   # Test a specific service
   python tests/test_ga_access.py
   ```

2. Verify configuration:
   ```bash
   # Check environment variables
   python -c "from config.settings import Settings; s = Settings(); print(s.dict())"
   ```

3. Test with mock data:
   ```bash
   # The dashboard currently uses mock data by default
   streamlit run app.py
   ```

#### Adding New Tests
When implementing new features:
1. Create test scripts following the pattern of existing test_*.py files
2. Test API connections before integrating into the dashboard
3. Use try/except blocks to handle API errors gracefully

#### Debugging Tips
- Enable Streamlit debug mode: `streamlit run app.py --logger.level=debug`
- Check Streamlit logs: `~/.streamlit/logs/`
- Test individual service classes in Python REPL:
  ```python
  from services.google_analytics import GoogleAnalytics
  ga = GoogleAnalytics()
  # Test methods here
  ```

### Future Testing Infrastructure

The project is designed to support a full testing suite in the future. Currently, the test_*.py files are standalone API verification scripts, not pytest tests.

Future testing plans include:
- Unit tests for service classes
- Integration tests with mocked API responses
- UI tests for Streamlit components
- Automated test suite with pytest

See ROADMAP.md for planned testing infrastructure improvements.

## 🤝 Contributing


We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments


- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)
- Multi-account architecture inspired by enterprise analytics needs

## 💬 Community


- [Discord](https://discord.gg/streamboard) - Join our community
- [Documentation](https://docs.streamboard.io) - Full documentation
- [Blog](https://blog.streamboard.io) - Tutorials and updates

---

<p align="center">
  Made with ❤️ by the StreamBoard Team
</p>