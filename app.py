import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Configure page with StreamBoard branding
st.set_page_config(
    page_title="StreamBoard Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for StreamBoard branding
st.markdown("""
<style>
    /* Main background styling */
    .main {
        background: #0a0a0a;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #0f0f0f;
        border-right: 1px solid #1e293b;
    }

    /* StreamBoard Logo and Branding */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1rem 0 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1e293b;
    }

    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
    }

    .logo-text {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }

    .metric-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }

    /* Metric value styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-change {
        font-size: 0.875rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }

    .metric-change-positive {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
    }

    .metric-change-negative {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
    }

    /* Chart container styling */
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        border-bottom: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        border-radius: 0;
        padding: 0.75rem 0;
        border-bottom: 2px solid transparent;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #ffffff;
        border-bottom: 2px solid #6366f1;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(99, 102, 241, 0.4);
    }

    /* Select box styling */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# Initialize mock services for demo
@st.cache_resource
def init_services():
    """Initialize services - in production, these would be real API connections"""
    return {
        'ga': 'GoogleAnalyticsService',
        'adsense': 'GoogleAdSenseService',
        'aws': 'AWSMetricsService'
    }

# Generate mock data for demo
@st.cache_data
def generate_mock_data(days=30):
    """Generate realistic mock data for demonstration"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Google Analytics mock data
    ga_data = pd.DataFrame({
        'date': dates,
        'users': np.random.randint(800, 1500, size=days) + np.random.randint(-50, 50, size=days),
        'sessions': np.random.randint(1200, 2000, size=days) + np.random.randint(-100, 100, size=days),
        'pageviews': np.random.randint(3000, 5000, size=days) + np.random.randint(-200, 200, size=days),
        'bounce_rate': np.random.uniform(40, 60, size=days),
        'avg_session_duration': np.random.uniform(120, 300, size=days)
    })

    # AdSense mock data
    adsense_data = pd.DataFrame({
        'date': dates,
        'earnings': np.random.uniform(50, 200, size=days) * (1 + np.sin(np.arange(days) * 0.2) * 0.3),
        'impressions': np.random.randint(10000, 20000, size=days),
        'clicks': np.random.randint(100, 300, size=days),
        'ctr': np.random.uniform(1.0, 2.5, size=days)
    })

    # AWS cost mock data
    services = ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront']
    aws_data = pd.DataFrame({
        'date': np.repeat(dates, len(services)),
        'service': services * days,
        'cost': np.random.uniform(5, 50, size=days * len(services))
    })

    return ga_data, adsense_data, aws_data

def render_logo():
    """Render StreamBoard logo"""
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13h2v7H3zm4-8h2v12H7zm4-2h2v14h-2zm4 4h2v10h-2zm4-2h2v12h-2z"/>
            </svg>
        </div>
        <div class="logo-text">StreamBoard</div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, change=None, format_type="number"):
    """Render a beautiful metric card"""
    if format_type == "currency":
        formatted_value = f"${value:,.2f}"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
    else:
        formatted_value = f"{value:,}"

    change_html = ""
    if change is not None:
        change_class = "metric-change-positive" if change >= 0 else "metric-change-negative"
        change_symbol = "↑" if change >= 0 else "↓"
        change_html = f'<div class="metric-change {change_class}">{change_symbol} {abs(change):.1f}%</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{formatted_value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

def create_chart_theme():
    """Create consistent chart theme matching StreamBoard branding"""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#94a3b8', 'family': '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif'},
        'xaxis': {'gridcolor': '#1e293b', 'zerolinecolor': '#1e293b'},
        'yaxis': {'gridcolor': '#1e293b', 'zerolinecolor': '#1e293b'},
        'colorway': ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe']
    }

def main():
    # Render logo in sidebar
    with st.sidebar:
        render_logo()

        st.markdown("### Configuration")
        date_range = st.selectbox(
            "Date Range",
            options=[7, 14, 30, 60, 90],
            format_func=lambda x: f"Last {x} days",
            index=2
        )

        st.markdown("---")

        refresh_data = st.button("🔄 Refresh Data", use_container_width=True)

        st.markdown("---")
        st.markdown("""
        <div style="padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3);">
            <p style="color: #a5b4fc; font-size: 0.875rem; margin: 0;">
                <strong>Pro Tip:</strong> Connect your real APIs in settings to see live data
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Main content area
    st.markdown("# 📊 Analytics Dashboard")
    st.markdown("Welcome to your unified metrics command center")

    # Get mock data
    ga_data, adsense_data, aws_data = generate_mock_data(date_range)

    # Tabs for different data sources
    tab1, tab2, tab3 = st.tabs(["📈 Google Analytics", "💰 AdSense Revenue", "☁️ AWS Metrics"])

    with tab1:
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            current_users = ga_data['users'].iloc[-1]
            prev_users = ga_data['users'].iloc[-8]
            change = ((current_users - prev_users) / prev_users) * 100
            render_metric_card("Active Users", current_users, change)

        with col2:
            total_sessions = ga_data['sessions'].sum()
            render_metric_card("Total Sessions", total_sessions)

        with col3:
            avg_bounce = ga_data['bounce_rate'].mean()
            render_metric_card("Avg Bounce Rate", avg_bounce, format_type="percentage")

        with col4:
            avg_duration = ga_data['avg_session_duration'].mean()
            render_metric_card("Avg Session", f"{avg_duration:.0f}s", format_type="text")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ga_data['date'],
                y=ga_data['users'],
                mode='lines',
                name='Users',
                line=dict(color='#6366f1', width=3),
                fill='tonexty',
                fillcolor='rgba(99, 102, 241, 0.1)'
            ))
            fig.update_layout(
                title="User Traffic Trend",
                **create_chart_theme()
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            device_data = pd.DataFrame({
                'device': ['Desktop', 'Mobile', 'Tablet'],
                'sessions': [5000, 3500, 1500]
            })
            fig = px.pie(device_data, values='sessions', names='device',
                        title="Sessions by Device",
                        color_discrete_sequence=['#6366f1', '#8b5cf6', '#a78bfa'])
            fig.update_layout(**create_chart_theme())
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        # AdSense KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_earnings = adsense_data['earnings'].sum()
            render_metric_card("Total Earnings", total_earnings, format_type="currency")

        with col2:
            total_impressions = adsense_data['impressions'].sum()
            render_metric_card("Impressions", total_impressions)

        with col3:
            avg_ctr = adsense_data['ctr'].mean()
            render_metric_card("Avg CTR", avg_ctr, format_type="percentage")

        with col4:
            total_clicks = adsense_data['clicks'].sum()
            render_metric_card("Total Clicks", total_clicks)

        # Earnings chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=adsense_data['date'],
            y=adsense_data['earnings'],
            name='Daily Earnings',
            marker_color='#8b5cf6'
        ))
        fig.update_layout(
            title="Daily AdSense Earnings",
            **create_chart_theme()
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        # AWS Cost Summary
        total_cost = aws_data['cost'].sum()
        services_summary = aws_data.groupby('service')['cost'].sum().sort_values(ascending=False)

        col1, col2 = st.columns([1, 2])

        with col1:
            render_metric_card("Total AWS Cost", total_cost, format_type="currency")

            st.markdown("### Top Services by Cost")
            for service, cost in services_summary.head(5).items():
                st.markdown(f"""
                <div style="margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                        <span>{service}</span>
                        <span>${cost:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily_costs = aws_data.groupby('date')['cost'].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_costs['date'],
                y=daily_costs['cost'],
                mode='lines+markers',
                name='Daily Cost',
                line=dict(color='#a78bfa', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title="Daily AWS Spending Trend",
                **create_chart_theme()
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()