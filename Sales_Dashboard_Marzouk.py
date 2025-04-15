import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Upload CSV file
st.sidebar.header("Upload Your Sales Data")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Convert date columns to datetime
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['date_only'] = pd.to_datetime(df['date_only'])

    # Tabs for analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overall Trends",
        "🛒 Product Performance",
        "📍 Branch & City Insights",
        "⏰ Time-Based Analysis",
        "📊 Revenue Distribution"
    ])

    with tab1:
        st.subheader("Sales Trends Over Time")
        sales_by_day = df.groupby('date_only')['total'].sum().reset_index()
        fig1 = px.line(sales_by_day, x='date_only', y='total', title='Total Sales by Day')
        st.plotly_chart(fig1, use_container_width=True)

        orders_by_day = df.groupby('date_only')['order_id'].nunique().reset_index()
        fig2 = px.bar(orders_by_day, x='date_only', y='order_id', title='Number of Orders by Day')
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Top & Bottom Performing Products")
        product_sales = df.groupby('product name').agg({
            'quantity': 'sum',
            'total': 'sum',
            'order_id': 'count'
        }).reset_index().sort_values(by='total', ascending=False)

        top_products = product_sales.head(10)
        bottom_products = product_sales.tail(10)

        fig3 = px.bar(top_products, x='total', y='product name', orientation='h', title='Top 10 Products by Revenue')
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.bar(bottom_products, x='total', y='product name', orientation='h', title='Bottom 10 Products by Revenue')
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.subheader("City and Branch-Level Insights")

        city_sales = df.groupby('city')['total'].sum().reset_index()
        fig5 = px.bar(city_sales, x='city', y='total', title='Revenue by City')
        st.plotly_chart(fig5, use_container_width=True)

        branch_sales = df.groupby('branch')['total'].sum().reset_index()
        fig6 = px.bar(branch_sales, x='branch', y='total', title='Revenue by Branch')
        st.plotly_chart(fig6, use_container_width=True)

    with tab4:
        st.subheader("Sales by Time of Day")

        df['hour'] = pd.to_datetime(df['time_only'], format='%H:%M:%S').dt.hour
        hourly_sales = df.groupby('hour')['total'].sum().reset_index()
        fig7 = px.line(hourly_sales, x='hour', y='total', title='Total Sales by Hour')
        st.plotly_chart(fig7, use_container_width=True)

        heatmap_data = df.groupby(['hour', 'date_only'])['total'].sum().unstack().fillna(0)
        fig8 = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis'))
        fig8.update_layout(title='Hourly Sales Heatmap')
        st.plotly_chart(fig8, use_container_width=True)

    with tab5:
        st.subheader("Revenue Distribution & Insights")

        category_sales = df.groupby('product_category')['total'].sum().reset_index()
        fig9 = px.pie(category_sales, values='total', names='product_category', title='Revenue by Product Category')
        st.plotly_chart(fig9, use_container_width=True)

        product_distribution = df.groupby('product name')['total'].sum().reset_index().sort_values(by='total', ascending=False)
        product_distribution['cumulative_share'] = product_distribution['total'].cumsum() / product_distribution['total'].sum()
        fig10 = px.line(product_distribution, y='cumulative_share', title='Cumulative Revenue Share by Product')
        st.plotly_chart(fig10, use_container_width=True)

else:
    st.title("📊 Sales Dashboard")
    st.info("Upload a sales dataset to begin your analysis.")
