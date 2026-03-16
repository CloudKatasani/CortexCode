import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.set_page_config(page_title="AI Consumption Dashboard", layout="wide")
st.title("📊 AI Consumption Dashboard")
st.caption("Executive visibility into Snowflake AI/ML usage across the organization")

def run_query(query):
    return session.sql(query).to_pandas()

col1, col2 = st.columns([1, 3])
with col1:
    time_range = st.selectbox(
        "Time Range",
        ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days"],
        index=2
    )

days_map = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 30 Days": 30, "Last 90 Days": 90}
days = days_map[time_range]

kpi_query = f"""
SELECT 
    COALESCE(SUM(token_credits), 0) AS total_cortex_credits,
    COALESCE(SUM(tokens), 0) AS total_tokens,
    COUNT(*) AS total_invocations,
    COUNT(DISTINCT function_name) AS unique_functions,
    COUNT(DISTINCT model_name) AS unique_models
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
"""

analyst_kpi_query = f"""
SELECT 
    COALESCE(SUM(credits), 0) AS analyst_credits,
    COALESCE(SUM(request_count), 0) AS analyst_requests,
    COUNT(DISTINCT username) AS unique_users
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
"""

try:
    kpi_df = run_query(kpi_query)
    analyst_df = run_query(analyst_kpi_query)
    
    total_credits = float(kpi_df['TOTAL_CORTEX_CREDITS'].iloc[0] or 0) + float(analyst_df['ANALYST_CREDITS'].iloc[0] or 0)
    total_tokens = int(kpi_df['TOTAL_TOKENS'].iloc[0] or 0)
    total_requests = int(kpi_df['TOTAL_INVOCATIONS'].iloc[0] or 0) + int(analyst_df['ANALYST_REQUESTS'].iloc[0] or 0)
    unique_users = int(analyst_df['UNIQUE_USERS'].iloc[0] or 0)
    
    st.divider()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Total AI Credits", f"{total_credits:,.2f}")
    m2.metric("🔤 Total Tokens", f"{total_tokens:,.0f}")
    m3.metric("📈 Total Requests", f"{total_requests:,.0f}")
    m4.metric("👥 Active Users", f"{unique_users:,.0f}")

except Exception as e:
    st.error(f"Error loading KPIs: {e}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends", 
    "👤 By User", 
    "🏭 By Warehouse",
    "🤖 By Model",
    "⚡ By Function"
])

with tab1:
    st.subheader("AI Credit Consumption Trend")
    
    trend_query = f"""
    WITH cortex_daily AS (
        SELECT 
            DATE(start_time) AS usage_date,
            SUM(token_credits) AS cortex_credits,
            SUM(tokens) AS tokens
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
        WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY DATE(start_time)
    ),
    analyst_daily AS (
        SELECT 
            DATE(start_time) AS usage_date,
            SUM(credits) AS analyst_credits,
            SUM(request_count) AS requests
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
        WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY DATE(start_time)
    ),
    date_series AS (
        SELECT DATEADD('day', -seq4(), CURRENT_DATE()) AS usage_date
        FROM TABLE(GENERATOR(ROWCOUNT => {days}))
    )
    SELECT 
        ds.usage_date AS "Date",
        COALESCE(c.cortex_credits, 0) AS "Cortex Functions",
        COALESCE(a.analyst_credits, 0) AS "Cortex Analyst",
        COALESCE(c.cortex_credits, 0) + COALESCE(a.analyst_credits, 0) AS "Total Credits",
        COALESCE(c.tokens, 0) AS "Tokens"
    FROM date_series ds
    LEFT JOIN cortex_daily c ON ds.usage_date = c.usage_date
    LEFT JOIN analyst_daily a ON ds.usage_date = a.usage_date
    ORDER BY ds.usage_date
    """
    
    try:
        trend_df = run_query(trend_query)
        
        if not trend_df.empty:
            trend_melted = trend_df.melt(
                id_vars=['Date'], 
                value_vars=['Cortex Functions', 'Cortex Analyst'],
                var_name='Service',
                value_name='Credits'
            )
            
            chart = alt.Chart(trend_melted).mark_area(opacity=0.7).encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Credits:Q', title='Credits', stack='zero'),
                color=alt.Color('Service:N', scale=alt.Scale(scheme='tableau10')),
                tooltip=['Date:T', 'Service:N', alt.Tooltip('Credits:Q', format=',.4f')]
            ).properties(height=350)
            
            st.altair_chart(chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Daily Token Consumption")
                token_chart = alt.Chart(trend_df).mark_bar(color='#1f77b4').encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Tokens:Q', title='Tokens'),
                    tooltip=['Date:T', alt.Tooltip('Tokens:Q', format=',')]
                ).properties(height=200)
                st.altair_chart(token_chart, use_container_width=True)
            
            with col2:
                st.caption("Cumulative Credits")
                trend_df['Cumulative'] = trend_df['Total Credits'].cumsum()
                cum_chart = alt.Chart(trend_df).mark_line(color='#2ca02c', strokeWidth=2).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Cumulative:Q', title='Cumulative Credits'),
                    tooltip=['Date:T', alt.Tooltip('Cumulative:Q', format=',.4f')]
                ).properties(height=200)
                st.altair_chart(cum_chart, use_container_width=True)
        else:
            st.info("No AI usage data found for the selected time range.")
            
    except Exception as e:
        st.error(f"Error loading trend data: {e}")

with tab2:
    st.subheader("AI Consumption by User")
    
    user_query = f"""
    WITH cortex_users AS (
        SELECT 
            qa.user_name,
            SUM(cf.token_credits) AS credits,
            SUM(cf.tokens) AS tokens,
            COUNT(*) AS requests
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY cf
        JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY qa 
            ON cf.warehouse_id = qa.warehouse_id 
            AND cf.start_time BETWEEN qa.start_time AND qa.end_time
        WHERE cf.start_time >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY qa.user_name
    ),
    analyst_users AS (
        SELECT 
            username AS user_name,
            SUM(credits) AS credits,
            0 AS tokens,
            SUM(request_count) AS requests
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
        WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
        GROUP BY username
    ),
    combined AS (
        SELECT * FROM cortex_users
        UNION ALL
        SELECT * FROM analyst_users
    )
    SELECT 
        user_name AS "User",
        SUM(credits) AS "Total Credits",
        SUM(tokens) AS "Total Tokens",
        SUM(requests) AS "Total Requests"
    FROM combined
    WHERE user_name IS NOT NULL
    GROUP BY user_name
    ORDER BY "Total Credits" DESC
    LIMIT 20
    """
    
    try:
        user_df = run_query(user_query)
        
        if not user_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                chart = alt.Chart(user_df.head(10)).mark_bar(color='#ff7f0e').encode(
                    x=alt.X('Total Credits:Q', title='Credits'),
                    y=alt.Y('User:N', sort='-x', title='User'),
                    tooltip=['User:N', alt.Tooltip('Total Credits:Q', format=',.4f'), alt.Tooltip('Total Requests:Q', format=',')]
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.caption("Top Users Summary")
                st.dataframe(user_df.head(10), hide_index=True, use_container_width=True)
        else:
            st.info("No user-level AI usage data found.")
            
    except Exception as e:
        st.error(f"Error loading user data: {e}")

with tab3:
    st.subheader("AI Consumption by Warehouse")
    
    warehouse_query = f"""
    SELECT 
        wmh.warehouse_name AS "Warehouse",
        SUM(cf.tokens) AS "Tokens",
        SUM(cf.token_credits) AS "Credits",
        COUNT(*) AS "Invocations"
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY cf
    LEFT JOIN (
        SELECT DISTINCT warehouse_id, warehouse_name 
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
    ) wmh ON cf.warehouse_id = wmh.warehouse_id
    WHERE cf.start_time >= DATEADD('day', -{days}, CURRENT_DATE())
    GROUP BY wmh.warehouse_name
    ORDER BY "Credits" DESC
    LIMIT 20
    """
    
    try:
        wh_df = run_query(warehouse_query)
        
        if not wh_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                chart = alt.Chart(wh_df.head(10)).mark_bar(color='#9467bd').encode(
                    x=alt.X('Credits:Q', title='Credits'),
                    y=alt.Y('Warehouse:N', sort='-x', title='Warehouse'),
                    tooltip=['Warehouse:N', alt.Tooltip('Credits:Q', format=',.4f'), alt.Tooltip('Tokens:Q', format=',')]
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.caption("Warehouse Summary")
                st.dataframe(wh_df.head(10), hide_index=True, use_container_width=True)
        else:
            st.info("No warehouse-level AI usage data found.")
            
    except Exception as e:
        st.error(f"Error loading warehouse data: {e}")

with tab4:
    st.subheader("AI Consumption by Model")
    
    model_query = f"""
    SELECT 
        model_name AS "Model",
        SUM(tokens) AS "Total Tokens",
        SUM(token_credits) AS "Total Credits",
        COUNT(*) AS "Invocations",
        ROUND(AVG(tokens), 0) AS "Avg Tokens/Call"
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
    WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
      AND model_name IS NOT NULL
    GROUP BY model_name
    ORDER BY "Total Credits" DESC
    """
    
    try:
        model_df = run_query(model_query)
        
        if not model_df.empty:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.caption("Credits by Model")
                pie_chart = alt.Chart(model_df).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta('Total Credits:Q'),
                    color=alt.Color('Model:N', scale=alt.Scale(scheme='category20')),
                    tooltip=['Model:N', alt.Tooltip('Total Credits:Q', format=',.4f')]
                ).properties(height=300)
                st.altair_chart(pie_chart, use_container_width=True)
            
            with col2:
                st.caption("Model Breakdown")
                st.dataframe(model_df, hide_index=True, use_container_width=True)
        else:
            st.info("No model-level AI usage data found.")
            
    except Exception as e:
        st.error(f"Error loading model data: {e}")

with tab5:
    st.subheader("AI Consumption by Function")
    
    func_query = f"""
    SELECT 
        function_name AS "Function",
        SUM(tokens) AS "Total Tokens",
        SUM(token_credits) AS "Total Credits",
        COUNT(*) AS "Invocations",
        ROUND(AVG(tokens), 0) AS "Avg Tokens/Call"
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
    WHERE start_time >= DATEADD('day', -{days}, CURRENT_DATE())
    GROUP BY function_name
    ORDER BY "Total Credits" DESC
    """
    
    try:
        func_df = run_query(func_query)
        
        if not func_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                chart = alt.Chart(func_df).mark_bar(color='#17becf').encode(
                    x=alt.X('Total Credits:Q', title='Credits'),
                    y=alt.Y('Function:N', sort='-x', title='Function'),
                    tooltip=['Function:N', alt.Tooltip('Total Credits:Q', format=',.4f'), alt.Tooltip('Invocations:Q', format=',')]
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            
            with col2:
                st.caption("Function Summary")
                st.dataframe(func_df, hide_index=True, use_container_width=True)
        else:
            st.info("No function-level AI usage data found.")
            
    except Exception as e:
        st.error(f"Error loading function data: {e}")

st.divider()
st.caption(f"Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data from SNOWFLAKE.ACCOUNT_USAGE (~2hr latency)")