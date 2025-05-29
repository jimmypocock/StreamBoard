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

## 🔍 Troubleshooting


### Multi-Account Issues


- **Account not showing**: Check JSON syntax in environment variables
- **Mixed data**: Ensure each account has a unique name
- **Authentication errors**: Each account needs its own credentials

### Google Analytics

- Check service account has "Viewer" access to all properties
- Verify property IDs are correct (numbers only)
- Ensure Analytics Data API is enabled

### Google AdSense

- Delete token files to re-authenticate accounts
- Check AdSense Management API is enabled
- Verify OAuth2 client type is "Desktop"

### AWS

- Verify IAM permissions for each account
- Check Cost Explorer is enabled (24h delay for new accounts)
- Ensure credentials are valid and not expired

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


```bash
# Install development dependencies
pip install -e .

# Run tests
pytest

# Format code
black .

# Check types
mypy .
```

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