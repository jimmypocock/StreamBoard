import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import services
from config.settings import settings
from services.google_analytics import GoogleAnalyticsService
from services.google_adsense import GoogleAdSenseService
from services.aws_metrics import AWSMetricsService
from utils.auth import SessionManager

# Validate configuration
try:
    settings.validate()
except ValueError as e:
    st.error(f"Configuration error: {str(e)}")
    st.info("Please check your .env file and ensure all required variables are set.")
    st.stop()

# Configure page with StreamBoard branding
st.set_page_config(
    page_title="StreamBoard Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session
SessionManager.init_session()

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

    .logo-icon::before {
        content: "📊";
        font-size: 24px;
        filter: brightness(0) invert(1);
    }

    .logo-text {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
        margin: 0;
    }

    /* Updated metric cards to work better with real data */
    div[data-testid="metric-container"] {
        background: #1a1a1a;
        border: 1px solid #262626;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }

    div[data-testid="metric-container"] > div {
        gap: 0;
    }

    /* Metric value styling */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #e0e7ff;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 0.375rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }

    .stButton > button:hover {
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all enabled services"""
    services = {}
    
    if settings.ENABLE_GOOGLE_ANALYTICS:
        try:
            services['ga'] = GoogleAnalyticsService()
        except Exception as e:
            st.error(f"Failed to initialize Google Analytics: {str(e)}")
            services['ga'] = None
    
    if settings.ENABLE_GOOGLE_ADSENSE:
        try:
            services['adsense'] = GoogleAdSenseService()
        except Exception as e:
            st.error(f"Failed to initialize Google AdSense: {str(e)}")
            services['adsense'] = None
    
    if settings.ENABLE_AWS_METRICS:
        try:
            services['aws'] = AWSMetricsService()
        except Exception as e:
            st.error(f"Failed to initialize AWS Metrics: {str(e)}")
            services['aws'] = None
    
    return services

# Sidebar
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon"></div>
        <h1 class="logo-text">StreamBoard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Analytics Dashboard")
    
    # Date range selector
    date_range = st.selectbox(
        "Time Period",
        options=[7, 14, 30, 60, 90],
        format_func=lambda x: f"Last {x} days",
        index=2  # Default to 30 days
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Service status
    st.markdown("### 🔌 Service Status")
    services = init_services()
    
    # Show service status
    if settings.ENABLE_GOOGLE_ANALYTICS:
        if services.get('ga') and services['ga'].client:
            st.success("✅ Google Analytics")
        else:
            st.error("❌ Google Analytics")
    
    if settings.ENABLE_GOOGLE_ADSENSE:
        if services.get('adsense') and services['adsense'].service:
            st.success("✅ Google AdSense")
        else:
            st.error("❌ Google AdSense")
    
    if settings.ENABLE_AWS_METRICS:
        if services.get('aws') and services['aws'].ce_client:
            st.success("✅ AWS Metrics")
        else:
            st.error("❌ AWS Metrics")
    
    st.markdown("---")
    
    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #64748b; font-size: 0.875rem; margin-top: 2rem;'>
            <p>StreamBoard v1.0</p>
            <p>Real-time Analytics</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main content
st.title("📊 Analytics Overview")

# Display current date range
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown(f"**Showing data for the last {date_range} days**")
with col2:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=date_range)
    st.markdown(f"**{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}**")
with col3:
    if services.get('ga'):
        realtime_users = services['ga'].get_realtime_users()
        st.metric("Live Users", realtime_users)

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["🌐 Google Analytics", "💰 Google AdSense", "☁️ AWS Metrics"])

# Google Analytics Tab
with tab1:
    if not settings.ENABLE_GOOGLE_ANALYTICS:
        st.info("Google Analytics is disabled. Enable it in your .env file.")
    elif not services.get('ga'):
        st.error("Google Analytics service failed to initialize. Please check your configuration.")
    else:
        st.header("Website Analytics")
        
        # Overview metrics
        try:
            metrics = services['ga'].get_overview_metrics(date_range)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Users",
                    f"{metrics['users']:,}",
                    f"{metrics['users_change']:+.1f}%" if metrics['users_change'] else None
                )
            
            with col2:
                st.metric(
                    "Sessions",
                    f"{metrics['sessions']:,}",
                    f"{metrics['sessions_change']:+.1f}%" if metrics['sessions_change'] else None
                )
            
            with col3:
                st.metric(
                    "Page Views",
                    f"{metrics['pageviews']:,}",
                    f"{metrics['pageviews_change']:+.1f}%" if metrics['pageviews_change'] else None
                )
            
            with col4:
                st.metric(
                    "Bounce Rate",
                    f"{metrics['bounce_rate']:.1f}%",
                    f"{metrics['bounce_rate_change']:+.1f}%" if metrics['bounce_rate_change'] else None,
                    delta_color="inverse"
                )
        except Exception as e:
            st.error(f"Error loading overview metrics: {str(e)}")
        
        # Traffic trend chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Traffic Trend")
            try:
                traffic_data = services['ga'].get_traffic_data(date_range)
                
                if not traffic_data.empty:
                    # Convert date string to datetime if needed
                    if 'date' in traffic_data.columns:
                        traffic_data['date'] = pd.to_datetime(traffic_data['date'], format='%Y%m%d')
                    
                    fig = go.Figure()
                    
                    # Add traces
                    fig.add_trace(go.Scatter(
                        x=traffic_data['date'],
                        y=traffic_data['activeUsers'],
                        name='Users',
                        line=dict(color='#6366f1', width=3),
                        mode='lines+markers'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=traffic_data['date'],
                        y=traffic_data['sessions'],
                        name='Sessions',
                        line=dict(color='#8b5cf6', width=3),
                        mode='lines+markers'
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e7ff',
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        xaxis=dict(
                            gridcolor='#1e293b',
                            showgrid=True
                        ),
                        yaxis=dict(
                            gridcolor='#1e293b',
                            showgrid=True
                        ),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No traffic data available for the selected period.")
                    
            except Exception as e:
                st.error(f"Error loading traffic data: {str(e)}")
        
        with col2:
            st.subheader("Device Breakdown")
            try:
                device_data = services['ga'].get_device_data(date_range)
                
                if not device_data.empty:
                    fig = px.pie(
                        device_data,
                        values='sessions',
                        names='deviceCategory',
                        color_discrete_sequence=['#6366f1', '#8b5cf6', '#a78bfa']
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e7ff'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No device data available.")
                    
            except Exception as e:
                st.error(f"Error loading device data: {str(e)}")
        
        # Top pages
        st.subheader("Top Pages")
        try:
            top_pages = services['ga'].get_top_pages(date_range)
            
            if not top_pages.empty:
                # Format the data for display
                display_df = top_pages.copy()
                display_df.columns = ['Page', 'Views', 'Users', 'Avg. Time (sec)']
                display_df['Views'] = display_df['Views'].apply(lambda x: f"{x:,}")
                display_df['Users'] = display_df['Users'].apply(lambda x: f"{x:,}")
                display_df['Avg. Time (sec)'] = display_df['Avg. Time (sec)'].apply(lambda x: f"{x:.0f}")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No page data available.")
                
        except Exception as e:
            st.error(f"Error loading top pages: {str(e)}")

# Google AdSense Tab
with tab2:
    if not settings.ENABLE_GOOGLE_ADSENSE:
        st.info("Google AdSense is disabled. Enable it in your .env file.")
    elif not services.get('adsense'):
        st.error("Google AdSense service failed to initialize. Please check your configuration.")
    else:
        st.header("Ad Revenue Analytics")
        
        # Overview metrics
        try:
            earnings = services['adsense'].get_earnings_overview(date_range)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Earnings",
                    f"${earnings['earnings']:.2f}",
                    f"{earnings['earnings_change']:+.1f}%" if earnings['earnings_change'] else None
                )
            
            with col2:
                st.metric(
                    "Clicks",
                    f"{earnings['clicks']:,}",
                    f"{earnings['clicks_change']:+.1f}%" if earnings['clicks_change'] else None
                )
            
            with col3:
                st.metric(
                    "CTR",
                    f"{earnings['ctr']:.2f}%",
                    f"{earnings['ctr_change']:+.1f}%" if earnings['ctr_change'] else None
                )
            
            with col4:
                st.metric(
                    "RPM",
                    f"${earnings['rpm']:.2f}",
                    f"{earnings['rpm_change']:+.1f}%" if earnings['rpm_change'] else None
                )
        except Exception as e:
            st.error(f"Error loading earnings overview: {str(e)}")
        
        # Daily earnings chart
        st.subheader("Daily Earnings Trend")
        try:
            daily_earnings = services['adsense'].get_daily_earnings(date_range)
            
            if not daily_earnings.empty:
                fig = go.Figure()
                
                # Add earnings line
                fig.add_trace(go.Scatter(
                    x=daily_earnings['date'],
                    y=daily_earnings['earnings'],
                    name='Earnings ($)',
                    line=dict(color='#10b981', width=3),
                    mode='lines+markers',
                    fill='tozeroy',
                    fillcolor='rgba(16, 185, 129, 0.1)'
                ))
                
                # Update layout
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e0e7ff',
                    showlegend=True,
                    xaxis=dict(
                        gridcolor='#1e293b',
                        showgrid=True
                    ),
                    yaxis=dict(
                        gridcolor='#1e293b',
                        showgrid=True,
                        tickformat='$,.2f'
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No earnings data available for the selected period.")
                
        except Exception as e:
            st.error(f"Error loading daily earnings: {str(e)}")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Earnings by Site")
            try:
                site_earnings = services['adsense'].get_earnings_by_site(date_range)
                
                if not site_earnings.empty:
                    fig = px.bar(
                        site_earnings,
                        x='earnings',
                        y='site',
                        orientation='h',
                        color='earnings',
                        color_continuous_scale=['#6366f1', '#8b5cf6']
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e7ff',
                        showlegend=False,
                        xaxis=dict(tickformat='$,.2f'),
                        yaxis=dict(title='')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No site earnings data available.")
                    
            except Exception as e:
                st.error(f"Error loading site earnings: {str(e)}")
        
        with col2:
            st.subheader("Top Performing Pages")
            try:
                top_pages = services['adsense'].get_top_performing_pages(date_range, limit=5)
                
                if not top_pages.empty:
                    # Format for display
                    display_df = top_pages[['page', 'earnings', 'rpm']].copy()
                    display_df.columns = ['Page', 'Earnings', 'RPM']
                    display_df['Earnings'] = display_df['Earnings'].apply(lambda x: f"${x:.2f}")
                    display_df['RPM'] = display_df['RPM'].apply(lambda x: f"${x:.2f}")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No page performance data available.")
                    
            except Exception as e:
                st.error(f"Error loading top pages: {str(e)}")

# AWS Metrics Tab
with tab3:
    if not settings.ENABLE_AWS_METRICS:
        st.info("AWS Metrics is disabled. Enable it in your .env file.")
    elif not services.get('aws'):
        st.error("AWS Metrics service failed to initialize. Please check your configuration.")
    else:
        st.header("AWS Infrastructure & Costs")
        
        # Cost overview
        try:
            cost_overview = services['aws'].get_cost_overview(date_range)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Cost",
                    f"${cost_overview['total_cost']:.2f}",
                    f"{cost_overview['cost_change']:+.1f}%" if cost_overview['cost_change'] else None
                )
            
            with col2:
                st.metric(
                    "Forecasted Cost",
                    f"${cost_overview['forecast_cost']:.2f}"
                )
            
            with col3:
                st.metric(
                    "Active Services",
                    cost_overview['service_count']
                )
            
            with col4:
                # Get resource summary
                resources = services['aws'].get_resource_summary()
                st.metric(
                    "EC2 Instances",
                    f"{resources['ec2_instances']['running']}/{resources['ec2_instances']['total']}"
                )
        except Exception as e:
            st.error(f"Error loading cost overview: {str(e)}")
        
        # Daily cost trend
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Daily Cost Trend")
            try:
                daily_costs = services['aws'].get_daily_costs(date_range)
                
                if not daily_costs.empty:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=daily_costs['date'],
                        y=daily_costs['cost'],
                        name='Daily Cost',
                        marker_color='#f59e0b'
                    ))
                    
                    # Add trend line
                    z = np.polyfit(range(len(daily_costs)), daily_costs['cost'], 1)
                    p = np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=daily_costs['date'],
                        y=p(range(len(daily_costs))),
                        name='Trend',
                        line=dict(color='#ef4444', width=2, dash='dash')
                    ))
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e7ff',
                        showlegend=True,
                        xaxis=dict(
                            gridcolor='#1e293b',
                            showgrid=True
                        ),
                        yaxis=dict(
                            gridcolor='#1e293b',
                            showgrid=True,
                            tickformat='$,.2f'
                        ),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No cost data available for the selected period.")
                    
            except Exception as e:
                st.error(f"Error loading daily costs: {str(e)}")
        
        with col2:
            st.subheader("Cost by Service")
            try:
                service_costs = services['aws'].get_service_costs(date_range)
                
                if not service_costs.empty:
                    # Get top 5 services
                    top_services = service_costs.head(5)
                    
                    fig = px.pie(
                        top_services,
                        values='cost',
                        names='service',
                        color_discrete_sequence=['#f59e0b', '#ef4444', '#10b981', '#3b82f6', '#8b5cf6']
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#e0e7ff'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No service cost data available.")
                    
            except Exception as e:
                st.error(f"Error loading service costs: {str(e)}")
        
        # Resource summary and alarms
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Resource Summary")
            try:
                resources = services['aws'].get_resource_summary()
                
                # Display resource counts
                st.markdown("##### EC2 Instances")
                st.markdown(f"🟢 Running: **{resources['ec2_instances']['running']}**")
                st.markdown(f"🔴 Stopped: **{resources['ec2_instances']['stopped']}**")
                st.markdown(f"📊 Total: **{resources['ec2_instances']['total']}**")
                
                st.markdown("##### Other Resources")
                st.markdown(f"🪣 S3 Buckets: **{resources['s3_buckets']['count']}**")
                st.markdown(f"🗄️ RDS Instances: **{resources['rds_instances']['count']}**")
                
                if resources['errors']:
                    st.warning("Some resources couldn't be loaded:")
                    for error in resources['errors']:
                        st.text(f"• {error}")
                        
            except Exception as e:
                st.error(f"Error loading resource summary: {str(e)}")
        
        with col2:
            st.subheader("Active Alarms")
            try:
                alarms = services['aws'].get_cloudwatch_alarms()
                
                if not alarms.empty:
                    for _, alarm in alarms.iterrows():
                        st.error(f"🚨 **{alarm['name']}**")
                        st.text(f"Metric: {alarm['metric']}")
                        st.text(f"Reason: {alarm['reason']}")
                        st.text(f"Updated: {alarm['updated'].strftime('%Y-%m-%d %H:%M')}")
                        st.markdown("---")
                else:
                    st.success("✅ No active alarms")
                    
            except Exception as e:
                st.error(f"Error loading alarms: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; font-size: 0.875rem;'>
        <p>StreamBoard Analytics Dashboard | Real-time insights from Google Analytics, AdSense & AWS</p>
    </div>
    """,
    unsafe_allow_html=True
)