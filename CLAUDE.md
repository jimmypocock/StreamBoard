# CLAUDE.md


This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StreamBoard is a self-hosted analytics dashboard built with Streamlit that unifies business metrics from Google Analytics, AdSense, and AWS into a single interface.

## Commands


### Running the Application

```bash
# Start the dashboard
./streamboard start   # Launches on http://localhost:8501

# Stop the dashboard
./streamboard stop

# Check status
./streamboard status

# Direct execution
streamlit run app.py
```

### Development Setup

```bash
# Initial setup (creates virtual environment)
./install.sh

# Activate virtual environment
source streamboard_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Architecture


### Core Application Structure

- **`app.py`**: Main Streamlit application containing the dashboard implementation. Currently uses mock data generators for demonstration. Key sections include:
  - Google Analytics metrics visualization (sessions, users, pageviews, bounce rate)
  - AdSense revenue tracking (earnings, clicks, CTR, RPM)
  - AWS infrastructure monitoring (EC2 instances, S3 buckets, RDS databases, costs)
  - Real-time data refresh capability

### Configuration

- **`.streamlit/config.toml`**: Contains theme configuration with dark mode settings matching StreamBoard branding (primary color: #1E3A5F)
- **`.env`**: Stores API credentials (created by install.sh, not committed to git)

### Key Dependencies

- `streamlit`: Web framework for the dashboard
- `plotly`: Interactive charting library
- `pandas`: Data manipulation
- `google-analytics-data`, `google-ads`, `boto3`: API clients for data sources

## Implementation Notes


The `ROADMAP.md` file contains detailed implementation plans for:
- Real API integrations to replace mock data
- Authentication system with database storage
- Data caching and optimization strategies
- Multi-user support with role-based access

When implementing new features, refer to the existing mock data structure in `app.py` as a template for the expected data format and visualization patterns.